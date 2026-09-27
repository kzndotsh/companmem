import time
from typing import List, Dict, Any
from picon.agents.base_agent import Agent
from picon.config import get_prompt_path
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput, IntervieweeResponse
from picon.utils import read_json, write_json, get_completion
import logging
import os
from dotenv import load_dotenv


class EntityExtractorTestEnv:
    def __init__(
        self, 
        model, 
        interview_data_path: str,
        **kwargs
        ):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        self.model = model
        self.agent = get_agent("entity_extractor", get_prompt_path("entity_extractor.txt"), model=model, port=kwargs.get('port', None))
        
        self.start_time = time.time()
        self.env_cost = 0.0
        self.interview_data_path = interview_data_path
        data = read_json(interview_data_path)['session_1']
        self.qa_pairs = [item['environment_observation'][0]['response'] for item in data['history'] if item['environment_observation'] and item['environment_observation'][0]['observation_type'] == 'interviewee_response' and item['type'] != 'repeat']

    def reset(self):
        """reset the environment"""
        self.state = State(current_turn=0, history=[])
        return self.state
    
    def step(self): # Interviewee's response -> Extractor -> WebSearch (optional) -> Questioner -> Interviewee
        """run one turn of the interrogation"""
        if self.state.current_turn >= len(self.qa_pairs):
            logging.info("All questions have been processed.")
            return self.state, True  # done
        question, answer = self.qa_pairs[self.state.current_turn]['question'], self.qa_pairs[self.state.current_turn]['content']
        logging.info(f"[TURN {self.state.current_turn}] Question: {question} | Answer: {answer}")
        # 3. Questioner formulates the next question
        # two scenarios: (1) from extractor directly (hence generating from interviewee's response directly), (2) from web search
        message = f"Question:{question}\nResponse: {answer}"
        action = self.agent.act(message) ####### 여기 #######
        if action.action_type == "next_agent":
            logging.info(f"Extractor did not find any entities or claims. Skipping to next agent.")
        else:
            logging.info(f"[ACTION] Entity Agent: {action.action_type} - {action.content if action.content is not None else action.tool_call.tool_name}")
        turn = Turn(
            type='main_interrogation',
            agent_action=[action],
            environment_observation=[
                Observation(
                    observation_type="interviewee_response",
                    response=IntervieweeResponse(
                        question=question,
                        content=answer
                    )
                )
            ]
        )
        self.state.current_turn += 1
        self.state.history.append(turn)

        return self.state, False
        
    def save_state(self, model_name:str, path: str, termination_status: str = "Successfully completed"):
        """save the current state to a json file"""
        final_result={
            "agents_info": "extractor_agent",
            "model" : model_name,
            "source_data_path": self.interview_data_path,
            "total_cost": self.agent.cost + self.env_cost,
            "duration": f"{(time.time() - self.start_time)/60} min", # in minutes
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
            "agent_memory": {
                self.agent.role: self.agent.memory
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

    parser = ArgumentParser(description="Entity Extractor Test Environment")
    parser.add_argument("--model", type=str, default="gpt-5", help="Model to use")
    parser.add_argument("--interview_data_path", type=str, required=True, help="Path to interview data JSON file")
    parser.add_argument("--port", type=int, default=None, help="Port for hosted_vllm models")
    args = parser.parse_args()

    env = EntityExtractorTestEnv(
        model=args.model,
        interview_data_path=args.interview_data_path,
        port=args.port
    )
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()
    env.save_state(args.model, f"data/prompt_engineering/entity_extractor/entity_extractor_{time.strftime('%Y%m%d_%H%M%S')}_{args.model.split('/')[-1]}_{args.interview_data_path.split('/')[-1].split('.')[0]}.json")