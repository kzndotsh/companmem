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


class KGAgentTestEnv:
    def __init__(
        self, 
        model, 
        interview_data_path: str,
        **kwargs
        ):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        self.model = model
        self.agent = get_agent("kg_agent", get_prompt_path("kg_agent_prompt.txt"), model=model)
        
        self.start_time = time.time()
        self.env_cost = 0.0
        self.interview_data_path = interview_data_path
        data = read_json(interview_data_path)
        self.qa_pairs = [item['environment_observation'][-1]['response'] for item in data['history'] if item['environment_observation'] and item['environment_observation'][-1]['observation_type'] == 'interviewee_response']

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
        if self.state.current_turn == 0:
            message = f"The interviewee's cutoff date information {answer}." # the first question's answer is about the cutoff date
        else:
            message = f"Question:{question}\nResponse: {answer}"
        action = self.agent.act(message) ####### 여기 #######

        logging.info(f"[ACTION] KG Agent: {action.action_type} - {action.content if action.content is not None else action.tool_call.tool_name}")
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
        
    def save_state(self, path: str, termination_status: str = "Successfully completed"):
        """save the current state to a json file"""
        final_result={
            "agents_info": "kg_agent",
            "source_data_path": self.interview_data_path,
            "total_cost": self.agent.cost + self.env_cost,
            "duration": f"{(time.time() - self.start_time)/60} min", # in minutes
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
            "agent_memory": {
                self.agent.role: self.agent.memory
            },
            "interviewee_kg": self.agent.kg
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
    parser.add_argument("--interview_data_path", type=str, required=True, help="Path to interview data JSON file")
    args = parser.parse_args()

    env = KGAgentTestEnv(
        model=args.model,
        interview_data_path=args.interview_data_path
    )
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()
    env.save_state(f"data/prompt_engineering/kg_agent/kg_agent_test_history_{time.strftime('%Y%m%d_%H%M%S')}.json")