import time
from picon.env.interviewee_simulator import IntervieweeSimulator
from typing import List, Dict, Any
from picon.agents.base_agent import Agent
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput, IntervieweeResponse
from picon.utils import read_json, write_json, get_completion
import logging
from litellm.cost_calculator import completion_cost
import os
from tqdm import tqdm
from dotenv import load_dotenv
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor

class ConflictTestEnv:
    def __init__(
        self, 
        model, 
        kg_path: str,
        **kwargs
        ):
        from importlib import resources
        self.conflict_prompt = open(str(resources.files("picon.env").joinpath("conflict_detection_prompt.txt")), "r").read()
        self.model = model
        
        self.start_time = time.time()
        self.env_cost = 0.0
        self.kg_path = kg_path
        data = read_json(kg_path)
        self.qa_pairs = [item['environment_observation'][-1]['response'] for item in data['history'] if item['environment_observation'] and item['environment_observation'][-1]['observation_type'] == 'interviewee_response']
        self.kg = data.get('interviewee_kg', [])

        self.internal_conflict_pairs_cnt = 0
        self.internal_conflict_pairs = []
        self.total_pairs_evaluated = 0
        self.first_conflict_turn = False

    def reset(self):
        """reset the environment"""
        self.state = State(current_turn=1, history=[])
        return self.state
    
    def step(self): # Interviewee's response -> Extractor -> WebSearch (optional) -> Questioner -> Interviewee
        """run one turn of the interrogation"""
        if self.state.current_turn >= len(self.kg):
            logging.info("All triplets have been processed.")
            return self.state, True  # done
        current_triplets = self.kg[self.state.current_turn]
        combinations_to_check = [(t1, current_triplets) for t1 in self.kg[:self.state.current_turn]]
        pair_format = "Triplet 1: {triplet_1} \n\nTriplet 2: {triplet_2}"
        content_list = []
        for triplet_1, triplet_2 in combinations_to_check:
            content_list.append(pair_format.format(
                triplet_1=triplet_1, triplet_2=triplet_2
            ))
        messages_list = [[
            {
                "role": "system",
                "content": self.conflict_prompt
            },
            {
                "role": "user",
                "content": content
            }
        ] for content in content_list]
        logging.info("Using sequential processing for conflict pair evaluation.")
        logging.info(f"Total pairs to evaluate: {len(messages_list)}")
        logging.info(f"Using model: {self.model}")
        logging.info("This may take a while...")
        with ThreadPoolExecutor(max_workers=32) as executor:
            verdicts = list(tqdm(executor.map(
                lambda messages: get_completion(
                    model=self.model,
                    messages=messages,
                    temperature=1.0
                ),
                messages_list
            )))
        self.total_pairs_evaluated += len(verdicts)
        conflict_pairs = []
        for idx, verdict in enumerate(verdicts):
            self.env_cost += completion_cost(verdict)
            response_text = verdict.choices[0].message.content.lower()
            if "conflict" in response_text:
                conflict_pairs.append(content_list[idx])
        logging.info(f"[CONFLICT DETECTION] Detected {len(conflict_pairs)} conflicting pairs in total.")
        if len(conflict_pairs) > 0:
            if not self.first_conflict_turn:
                self.first_conflict_turn = self.state.current_turn
            self.internal_conflict_pairs_cnt += len(conflict_pairs)
            self.internal_conflict_pairs.extend(conflict_pairs)
            for pair in conflict_pairs:
                logging.info(f"[CONFLICT DETECTION] Conflicting Pair:\n{pair}\n")
        self.state.current_turn += 1
        return self.state, False
        
    def save_state(self, path: str, termination_status: str = "Successfully completed"):
        """save the current state to a json file"""
        final_result={
            "source_data_path": self.kg_path,
            "total_cost": self.env_cost,
            "duration": f"{(time.time() - self.start_time)/60} min", # in minutes
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
            "internal_consistency": {
                "first_conflict_turn": self.first_conflict_turn,
                "conflict_pairs_count": self.internal_conflict_pairs_cnt,
                "conflict_pairs": self.internal_conflict_pairs,
                "total_pairs_evaluated": self.total_pairs_evaluated,
                "conflict_rate": self.internal_conflict_pairs_cnt / self.total_pairs_evaluated if self.total_pairs_evaluated > 0 else 0
            },
        }
        write_json(final_result, path)
        
        logging.info(f"Saving final result to {path}")
        logging.info(f"Total cost: ${final_result['total_cost']}, Duration: {final_result['duration']}")
        

if __name__ == "__main__":
    from picon.utils import setup_logging
    from argparse import ArgumentParser
    setup_logging(log_to_file=True, process_name="test_env")
    load_dotenv()

    parser = ArgumentParser(description="Questioner Test Environment")
    parser.add_argument("--model", type=str, default="gpt-5", help="Model to use")
    parser.add_argument("--kg_path", type=str, required=True, help="Path to interview data JSON file")
    args = parser.parse_args()

    env = ConflictTestEnv(
        model=args.model,
        kg_path=args.kg_path
    )
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()
    env.save_state(f"data/prompt_engineering/conflict_detection/conflict_detection_test_history_{time.strftime('%Y%m%d_%H%M%S')}.json")