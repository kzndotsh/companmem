import os
import time
from typing import List, Dict, Any, Literal
from picon.agents.agent_factory import get_agent
from picon.schemas import Turn
from picon.utils import read_json, write_json
import logging
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))


class EvaluatorTestEnv:
    def __init__(
        self, 
        model: str, 
        interview_path: Any | str | Dict,
        **kwargs
        ):
        self.model = model
        self.host = kwargs.get('host', None)
        self.port = kwargs.get('port', None)
        self.eval_factors = kwargs.get('eval_factors', None)  # ['internal', 'external', 'intra', 'inter'] or None for all
        self.start_time = time.time()
        self.env_cost = 0.0
        self.interview_path = interview_path if isinstance(interview_path, str) else "provided as dict"
        self.all_data = read_json(interview_path) if isinstance(interview_path, str) else interview_path
        
        if "agents_memory" not in self.all_data:
            if "session_1" in self.all_data:
                data = self.all_data["session_1"]
                self.num_sessions = len([k for k in self.all_data.keys() if k.startswith('session_')])
            else:
                data = self.all_data
                self.num_sessions = 1
            self.evaluator_memory = data["agent_memory"]["evaluator"]
        else:
            self.evaluator_memory = self.all_data["agents_memory"]["evaluator"]
            self.num_sessions = len([k for k in self.all_data.keys() if k.startswith('session_')])
        
        # Get evaluator memory to initialize the evaluator agent
        
        
        # Build histories as List[List[Turn]] for evaluator.act()
        self.histories = []
        if "session_1" in self.all_data:
            for session_id in ['session_'+str(i+1) for i in range(self.num_sessions)]:
                if session_id in self.all_data:
                    session_data = self.all_data[session_id]
                    # Convert dict history to Turn objects
                    history = [Turn(**turn) for turn in session_data['history']]
                    self.histories.append(history)
        else:
            history = [Turn(**turn) for turn in self.all_data['history']]
            self.histories.append(history)

        # Initialize the evaluator agent with model and memory from the saved data
        self.evaluator = get_agent(
            "evaluator",
            get_prompt_path("evaluator_prompt.txt"),
            model=model,
            port=self.port,
            host=self.host
        )
        # Replace the evaluator's memory with the saved memory
        self.evaluator.memory = self.evaluator_memory.copy()
        
        # Results placeholder
        self.evaluation_results = None
    
    def _has_existing_evaluation(self) -> bool:
        """Check if evaluation already exists in the data."""
        session_data = self.all_data.get("session_1", self.all_data)
        # Check for new format: data['evaluation']
        if 'evaluation' in session_data:
            return True
        # Check for old format keys
        if "external_consistency" in session_data or "internal_consistency" in session_data:
            return True
        return False

    def reset(self):
        """reset the environment - reinitialize evaluator memory from saved data"""
        self.evaluator.memory = self.evaluator_memory.copy()
        return
    
    def step(self):
        """Run evaluation using evaluator.act()"""
        logging.info(f"[EVALUATOR] Running evaluation with {self.num_sessions} session(s)...")
        if self.eval_factors:
            logging.info(f"[EVALUATOR] Evaluating factors: {self.eval_factors}")
        
        # Call evaluator.act() with histories and eval_factors
        eval_action = self.evaluator.act(histories=self.histories, eval_factors=self.eval_factors)
        
        assert eval_action.action_type == "respond", "Evaluator must respond with evaluation."
        assert isinstance(eval_action.content, dict), "Evaluator response must be a dict."
        
        self.evaluation_results = eval_action.content
        self.env_cost = self.evaluator.cost
        self._is_existing_evaluation = False
        
        # Log results
        logging.info("[EVALUATOR] Evaluation completed.")
        logging.info(f"Internal Score: {self.evaluation_results['internal']['score']}")
        logging.info(f"External Score: {self.evaluation_results['external']['score']}")
        logging.info(f"Intra-Session Score: {self.evaluation_results['stability']['intra_session']['score']}")
        if self.num_sessions > 1:
            logging.info(f"Inter-Session Score: {self.evaluation_results['stability']['inter_session']['score']}")
        
        return True
    
    def save_state(self, path: str, termination_status: str = "Successfully completed"):
        """Save the current state to a json file
        
        Output format aligns with expected format from main.py/interrogation_env.py
        """
        if self.evaluation_results is None:
            logging.warning("No evaluation results to save. Run step() first.")
            return
        
        # Check if this is an existing evaluation (old format) or new evaluation from evaluator.act()
        is_existing = getattr(self, '_is_existing_evaluation', False)
        
        if is_existing:
            # Use the existing format directly
            final_result = {
                "interview": self.interview_path,
                "total_cost": self.env_cost,
                "duration": f"{(time.time() - self.start_time)/60:.2f} minutes",
                "evaluation": self.evaluation_results
            }
            logging.info(f"Saving existing evaluation to {path}")
        else:
            # Convert evaluator.act() output format to expected output format
            final_result = {
                "interview": self.interview_path,
                "total_cost": self.env_cost,
                "duration": f"{(time.time() - self.start_time)/60:.2f} minutes",
                "evaluation": self.evaluation_results, 
                "evaluation_model": self.model,
            }
            
            logging.info(f"Saving final result to {path}")
            logging.info(f"Total cost: ${final_result['total_cost']}, Duration: {final_result['duration']}")
            logging.info("Results summary:")
            logging.info(f"Internal Score: {self.evaluation_results['internal']['score']}")
            logging.info(f"External Score: {self.evaluation_results['external']['score']}")
            logging.info(f"Intra-Session Stability Score: {self.evaluation_results['stability']['intra_session']['score']}")
            if self.num_sessions > 1:
                logging.info(f"Inter-Session Stability Score: {self.evaluation_results['stability']['inter_session']['score']}")
            
        write_json(final_result, path)
        return 


if __name__ == "__main__":
    from picon.utils import setup_logging
    from argparse import ArgumentParser
    setup_logging(log_to_file=True, process_name="test_env")
    load_dotenv()

    parser = ArgumentParser(description="Evaluator Test Environment")
    parser.add_argument("--model", type=str, default="gpt-5", help="Model to use")
    parser.add_argument("--interview_path", type=str, required=True, help="Path to interview data JSON file")
    parser.add_argument("--baseline_name", type=str, required=True, help="Baseline name for saving results")
    parser.add_argument("--host", type=str, default=None, help="Evaluator api base url")
    parser.add_argument("--port", type=int, default=None, help="Port for model API if needed")
    parser.add_argument("--output_dir", type=str, default="data/evaluation", help="Directory to save evaluation results")
    parser.add_argument("--eval_factors", type=str, nargs='+', default=None, choices=['internal', 'external', 'intra', 'inter'], help='Evaluation factors to compute. If not specified, all factors are evaluated.')
    
    args = parser.parse_args()
    
    curr_time = time.strftime("%Y%m%d_%H%M%S")

    env = EvaluatorTestEnv(
        model=args.model,
        interview_path=args.interview_path,
        port=args.port,
        host=args.host,
        eval_factors=args.eval_factors
    )
    state = env.reset()
    env.step()
    env.save_state(f"{args.output_dir}/{args.baseline_name}/evaluation_{os.path.basename(args.interview_path).split('.json')[0]}_{curr_time}.json")