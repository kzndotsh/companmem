import time
from picon.env.interviewee_simulator.simulator_factory import get_interviewee_simulator
from picon.config import get_prompt_path
from typing import List, Dict, Any
from picon.agents.base_agent import Agent
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput, IntervieweeResponse
from picon.tools.address_locator import GoogleGeocodeValidate
from picon.tools.web_search import GoogleClaimSearch
from pydantic import BaseModel
from picon.utils import read_json, write_json, get_completion
import logging
from litellm.cost_calculator import completion_cost
import os
from tqdm import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
import random

class QuestionerTestEnv:
    def __init__(
        self, 
        model, 
        agents: Dict[str, Agent] = {},
        baseline_name: str = "characterai",
        tools: List[Dict[str, Any]] = [],
        max_turns: int = 20,
        question_path: str = None,
        instruction_path: str = None,
        **kwargs
        ):
        self.tools = tools
        self.model = model
        if not agents:
            logging.warning("No agents provided. Initializing default agents.")
            agents = {
                "questioner": get_agent("questioner", get_prompt_path("questioner.txt"), model=model),
                "extractor": get_agent("entity_extractor", get_prompt_path("entity_extractor.txt"), model=model),
                "web_search": get_agent("web_search", get_prompt_path("websearch_prompt.txt"), model=model),
                "evaluator": get_agent("evaluator", get_prompt_path("evaluator_prompt.txt"), model=model),
            }
        self.agents = agents
        if 'web_search' in self.agents and not self.tools:
            logging.warning("No tools provided for web search agent.")
        if 'web_search' in self.agents and not self.agents['web_search'].tools:
            logging.info("Setting web search agent tools from environment.")
            self.agents['web_search'].tools = [tool.get_info() for tool in self.tools.values()]
        
        self.interviewee = get_interviewee_simulator(baseline_name, **kwargs)
        self.max_turns = max_turns
        from picon.config import get_question_path
        from importlib import resources
        self.predefined_questions = random.sample(read_json(question_path or get_question_path()), k=5)
        _inst_path = instruction_path or str(resources.files("picon.env").joinpath("interrogation_instruct.txt"))
        self.instruction = open(_inst_path).read()
        self.state = State(current_turn=0, history=[])
        self.cutoff_date = time.strftime("%B %d, %Y") # default to current date
        self.start_time = None
        self.env_cost = 0.0
        
        self.agents['questioner'].set_cutoff_date(self.cutoff_date)
        self.agents['web_search'].set_cutoff_date(self.cutoff_date)
        self.agents['evaluator'].set_cutoff_date(self.cutoff_date)

        # repeat
        self.repeat_score = 0
        self.repeat_results = []
        
        self.human_interviewer = kwargs.get("human_interviewer", False)

    def invoke_tool(self, action: Action) -> Observation | None:
        if action.action_type == "tool_call":
            tool_name = action.tool_call.tool_name
            if tool_name not in self.tools:
                logging.error(f"Tool {tool_name} not found.")
                return self.state, True
            
            # update questioner memory with tool calling details
            # self.agents['questioner'].update_memory(
            #     **action.tool_call.details
            # )
            
            tool = self.tools[tool_name]
            tool_output = tool.invoke(**action.tool_call.arguments)
            logging.info(f"[TOOL OUTPUT] {tool_name}: {tool_output[:100]}...") # print first 100 chars
            
            output = ToolOutput(
                tool_call_id=action.tool_call.details.get('tool_calls')[0].get('id'),
                tool_name=tool_name,
                output=tool_output
            )
            return output
        return None

    def reset(self):
        """run predefined questions to initialize the interview state"""
        self.start_time = time.time()
        self.instruction = self.instruction.format(cutoff_date=self.cutoff_date)
        # feed interview instruction to the interviewee
        logging.info(f"[INSTRUCTION] {self.instruction}")
        response = self.interviewee.get_response(self.instruction)
        logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
        # run predefined questions
        for i, q in enumerate(self.predefined_questions):
            logging.info(f"[QUESTION {self.state.current_turn}] {q['question']}")
            response = self.interviewee.get_response(q['question'])
            logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
            
            # update state
            action = Action(action_type="respond", content=q['question'])
            res_observation = Observation(
                observation_type="interviewee_response",
                response=response
            )
            
            self.state.current_observation = res_observation
            self.state.current_turn += 1
            
            self.agents['evaluator'].update_memory(role="assistant", content=q['question'])
            self.agents['questioner'].update_memory(role="assistant", content=q['question'])
            self.agents['evaluator'].update_memory(role="user", content=response.content)
            self.agents['questioner'].update_memory(role="user", content=response.content)
            
            entity_action, web_observation, web_search_actions = self.consistency_check(
                question=q['question'],
                answer=response.content
            )
            # for verdict_action in verdict_actions:
                # self.agents['questioner'].update_memory(**{"role":"assistant", "content": str(verdict_action.content)}) ####### 여기 #######
            if web_search_actions:
                turn = Turn(type='get_to_know', agent_action=[entity_action, *web_search_actions], environment_observation=[res_observation, web_observation])
            else:
                turn = Turn(type='get_to_know', agent_action=[entity_action], environment_observation=[res_observation])
            
            self.state.history.append(turn)

        return self.state

    def check_external(self, message : str) -> bool:
        # 1. Extractor first extracts the entity & claim to verify
        next_action = self.agents["extractor"].act(message)
        logging.info(f"[ACTION] Extractor: {next_action.action_type} - {next_action.content if next_action.content else next_action.target_agent}")
        if next_action.action_type == "next_agent":
            if next_action.target_agent != "questioner":
                logging.error("Extractor can only pass to Questioner.")
                return self.state, True
            logging.info("No entity or claim extracted. Passing to Questioner.")
            observation = None
            filtered_actions = []
        elif next_action.action_type == "respond": # should be respond with entity & claim
            if next_action.content is None:
                logging.error("Extractor must respond with entity & claim.")
                return self.state, True

            list_of_extractions = [ext.model_dump() for ext in next_action.content] # list of ExtractorResponse
            history = []
            for turn in self.state.history:
                # last element is interviewee response
                qa_pair = turn.environment_observation[0].response
                history.append({
                    "question": qa_pair.question,
                    "answer": qa_pair.content
                })
            # 2. Web Search (optional)
            with ThreadPoolExecutor(max_workers=len(list_of_extractions)) as executor:
                web_search_actions = list(executor.map(self.agents['web_search'].act, list_of_extractions, [history]*len(list_of_extractions)))
            filtered_actions = []
            filtered_actions_indices = []
            for i, action in enumerate(web_search_actions): 
                if action and action.action_type == "tool_call":
                    filtered_actions.append(action)
                    filtered_actions_indices.append(i)
            
            if filtered_actions:
                with ThreadPoolExecutor(max_workers=len(filtered_actions)) as executor:
                    tool_outputs = list(executor.map(self.invoke_tool, filtered_actions))
                
                observation = Observation(
                    observation_type="tool_output",
                    tool_output=tool_outputs
                )
                prev_conf_qa = []
                for i, output in enumerate(tool_outputs):
                    sub_message = [
                        {
                            "role": "user",
                            "content": message
                        },
                        filtered_actions[i].tool_call.details,
                        {
                            "role": "tool",
                            "tool_call_id": output.tool_call_id,
                            "name": output.tool_name,
                            "content": f"Entity:{list_of_extractions[filtered_actions_indices[i]]['entity']}\nClaims: {list_of_extractions[filtered_actions_indices[i]]['claims']}\nRationale: {list_of_extractions[filtered_actions_indices[i]]['rationale']}\nSearch Result:{str(output.output)}"
                        }
                    ]
                    """tool call 결과를 evaluator 메모리에 추가"""
                    self.agents['evaluator'].update_memory(**sub_message[1]) ####### 여기 #######
                    self.agents['evaluator'].update_memory(**sub_message[2]) ####### 여기 #######
                    if prev_conf_qa:
                        sub_message = sub_message + prev_conf_qa
                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "Ask a short, concise \"confirm/refute\" question if the entity that the interviewee mentioned refers to the information found in the web search results. You may provide a brief explanation about the entity based on the search results. "
                                "Assume that no further search is available beyond the provided search results. "
                                "If search results are incomplete due to search failure or error, ask a generic confirmation question about the entity. "
                                "If the search results are duplicate or redundant with previous questions, do not ask a new question; instead, responde with a single word-SKIP."
                                "Generate a single question without any additional explanation. "
                            )
                        },
                    ]
                    messages.extend(sub_message)
                    res = get_completion(
                        model=self.model,
                        messages=messages,
                        reasoning_effort="low",
                    )
                    self.env_cost += completion_cost(res)
                    confirmation_question = res.choices[0].message.content.strip()
                    if not confirmation_question or confirmation_question.upper() == "SKIP":
                        logging.info("No new confirmation question generated. Skipping.")
                        continue
                    else:
                        logging.info(f"[CONFIRMATION QUESTION] {confirmation_question}")
                        response = self.interviewee.get_response(confirmation_question)
                        logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
                        
                        self.agents['evaluator'].update_memory(role="assistant", content=confirmation_question) ####### 여기 #######
                        self.agents['evaluator'].update_memory(role="user", content=response.content) ####### 여기 #######
                        self.agents['questioner'].update_memory(role="assistant", content=confirmation_question) ####### 여기 #######
                        self.agents['questioner'].update_memory(role="user", content=response.content) ####### 여기 #######

                        prev_conf_qa.append({
                            "role": "assistant",
                            "content": confirmation_question
                        })
                        prev_conf_qa.append({
                            "role": "user",
                            "content": response.content
                        })
                    
            else:
                observation = None
                filtered_actions = []
        return next_action, observation, filtered_actions

    def consistency_check(self, question: str, answer : str):
        message = f"Question:{question}\nResponse: {answer}" # find interviewee_response (first index)
        
        next_action, observation, filtered_actions = self.check_external(message)
        
        return next_action, observation, filtered_actions
    
    
    def step(self): # Interviewee's response -> Extractor -> WebSearch (optional) -> Questioner -> Interviewee
        """run one turn of the interrogation"""
        logging.info(f"--- Turn {self.state.current_turn} ---")
        if self.state.current_turn >= self.max_turns:
            logging.warning("Max turns reached. Please reset the environment.")
            return self.state, True
        verdict = self.state.history[-1].agent_action[-1].content if self.state.history else None
        question_act = self.agents['questioner'].act(verdict=verdict)
        logging.info(f"[ACTION] Questioner: {question_act.action_type} - {question_act.content if question_act.content else question_act.tool_call.tool_name}")
        self.agents['evaluator'].update_memory(role="assistant", content=question_act.content)
        interviewee_res = self.interviewee.get_response(question_act.content)
        logging.info(f"[RESPONSE] {self.interviewee.name}: {interviewee_res.content}")
        
        self.agents['questioner'].update_memory(role="user", content=interviewee_res.content) 
        self.agents['evaluator'].update_memory(role="user", content=interviewee_res.content)

        entity_action, observation, web_search_actions = self.consistency_check(
            interviewee_res.question,
            interviewee_res.content
        )

        self.state.current_turn += 1

        actions = [question_act, entity_action, *web_search_actions] if web_search_actions else [question_act, entity_action]
        res_ob = Observation(observation_type="interviewee_response", response=interviewee_res)
        observations = [res_ob, observation] if observation else [res_ob]
        turn = Turn(
            type='main_interrogation',
            agent_action=actions,
            environment_observation=observations
        )
        
        self.state.history.append(turn)

        return self.state, False
        
    def save_state(self, path: str, termination_status: str = "Successfully completed"):
        """save the current state to a json file"""
        final_result={
            "agents_info":{agent_name: agent.model for agent_name, agent in self.agents.items()},
            "interviewee_info": {
                "name": self.interviewee.name,
                "baseline": self.interviewee.type,
            },
            "total_cost": sum(agent.cost for agent in self.agents.values()) + self.interviewee.cost + self.env_cost,
            "duration": f"{(time.time() - self.start_time)/60} min", # in minutes
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
            "agent_memory": {
                agent_name: agent.memory for agent_name, agent in self.agents.items()
            },
            "repeat_score":{
                "repeat_score": self.repeat_score,
                "repeat_results": self.repeat_results
            }
        }
        write_json(final_result, path)
        
        logging.info(f"Saving final result to {path}")
        logging.info(f"Total cost: ${final_result['total_cost']}, Duration: {final_result['duration']}")

    def finalize(self):
        """repeat stage: repeat the pre-defined questions to check for consistency"""
        
        REPEAT_PROMPT = """You will be given a single question and two corresponding answers. Determine whether the two answers are essentially the same in meaning.
If they are, output TRUE. If they are not, output FALSE.
Do not output any additional explanation or text."""
        
        for i, q in enumerate(self.predefined_questions):
            logging.info(f"[REPEAT QUESTION] Just to clarify, {q['question']}")
            response = self.interviewee.get_response(f"Just to clarify, {q['question']}")
            logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
            if i == 0:
                # first turn defines the cutoff date
                continue
            # update state
            action = Action(action_type="respond", content=q['question'])
            observation = Observation(
                observation_type="interviewee_response",
                response=response
            )
            turn = Turn(type='repeat', agent_action=[action], environment_observation=[observation])
            self.state.history.append(turn)
            
            inital_response = self.state.history[i].environment_observation[0].response.content
            while True:
                res = get_completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": REPEAT_PROMPT},
                        {"role": "user", "content": f"Question: {q['question']}\n\nResponse 1: {inital_response}\nResponse 2: {response.content}"}
                    ],
                    reasoning_effort="low",
                )
                self.env_cost += completion_cost(res)
                judge = res.choices[0].message.content.strip() if res and res.choices and res.choices[0].message and res.choices[0].message.content else "FALSE"
                if judge in ["TRUE", "FALSE"]:
                    break
                logging.warning(f"Unexpected response for repeat score: {judge}. Retrying...")
            
            self.repeat_results.append({
                "question": f"Just to clarify, {q['question']}",
                "original_response": inital_response,
                "repeated_response": response.content,
                "is_repeat": judge
            })
            self.repeat_score += (judge=='TRUE')
        self.repeat_score = round(self.repeat_score / len(self.predefined_questions), 4)
        return self.state

if __name__ == "__main__":
    from picon.utils import setup_logging, read_jsonl
    from argparse import ArgumentParser
    from datasets import load_dataset
    import re
    import glob
    
    load_dotenv()

    parser = ArgumentParser(description="Questioner Test Environment")
    parser.add_argument("--model", type=str, default="gpt-5", help="Model to use")
    parser.add_argument("--nhd_model", type=str, default="gpt-5", help="NHD model to use")
    parser.add_argument("--simulator_model", type=str, default=None, help="Simulator model for LLM-based baselines")
    parser.add_argument("--max_turns", type=int, default=30, help="Maximum number of turns")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for persona selection")
    parser.add_argument("--human_interviewer", action="store_true", help="Use human simulacra as interviewer")
    parser.add_argument("--baseline_name", type=str, required=True, 
                        choices=['characterai', 'human_simulacra', 'naive_human_simulacra', 'opencharacter', 
                                 'consistent_llm', 'human_interview', 'persona_hub', 'twin_2k_500', 
                                 'deeppersona', 'llm_generated'],
                        help="Baseline interviewee simulator to use")
    parser.add_argument("--simulator_port", type=int, default=None, help="Port for the persona simulator")
    parser.add_argument("--simulator_host", type=str, default='localhost', help="Host for the persona simulator")
    parser.add_argument("--nhd_port", type=int, default=None, help="Port for the NH detector")
    args = parser.parse_args()
    
    setup_logging(log_to_file=True, process_name="questioner_test_env")
    random.seed(args.seed)
    
    # Build interviewee kwargs based on baseline
    interviewee_kwargs = []
    
    if args.baseline_name == "characterai":
        assert os.getenv('CAI_API_KEY') is not None, "Character AI requires CAI_API_KEY"
        personas = read_json("src/env/personas/characterai.json")
        for persona in personas:
            interviewee_kwargs.append({
                "baseline_name": "characterai",
                "character_id": persona['character_id'],
                "user_id": os.getenv('CAI_API_KEY'),
                "name": persona['character_name'],
                "nhd_model": args.nhd_model,
                "nhd_port": args.nhd_port,
            })
    
    elif "human_simulacra" in args.baseline_name:
        names = ["Mary Jones", "Haley Collins", "Sara Ochoa", "James Jones", "Tami Clark", 
                 "Michael Miller", "Kevin Kelly", "Erica Walker", "Leslie Nichols", "Robert Scott", "Marsh Zhaleh"]
        for name in names:
            interviewee_kwargs.append({
                "baseline_name": args.baseline_name,
                "name": name,
                "nhd_model": args.nhd_model,
                "simulator_model": args.simulator_model,
                "nhd_port": args.nhd_port,
            })
    
    elif args.baseline_name == "opencharacter":
        dataset = load_dataset("xywang1/OpenCharacter", "Synthetic-Character", split="train")
        for data in dataset:
            name_match = re.match(r"Name:\s(.*)\n", data['character'])
            if not name_match:
                continue
            interviewee_kwargs.append({
                "baseline_name": "opencharacter",
                "model_path": "willystumblr/opencharacter-sft-2025-06-21_14-54-13",
                "persona": data['persona'],
                "profile": data['character'],
                "name": name_match.group(1).strip(),
                "load_in_4bit": True,
                "nhd_model": args.nhd_model,
                "simulator_model": args.simulator_model,
                "port": args.simulator_port,
                "simulator_host": args.simulator_host,
                "nhd_port": args.nhd_port,
            })
    
    elif args.baseline_name == "consistent_llm":
        dataset = read_jsonl("src/env/personas/consistent_llm_personas.jsonl")
        for data in dataset:
            interviewee_kwargs.append({
                "baseline_name": "consistent_llm",
                "model_path": "/home/edlab/sjim/consistent-LLMs/rl_training/checkpoints/chatting/llama-8b-sft-ppo-prompt",
                "persona": data['persona'],
                "name": data['name'],
                "counterpart_name": data['counterpart_name'],
                "instruction": data['instruction'],
                "nhd_model": args.nhd_model,
                "nhd_port": args.nhd_port,
                "simulator_model": args.simulator_model,
                "simulator_host": args.simulator_host,
                "port": args.simulator_port,
            })
    
    elif args.baseline_name == "persona_hub":
        dataset = read_jsonl("src/env/personas/persona_hub/named_personas_with_key.jsonl")
        for data in dataset:
            data['persona'] = data['persona'][0].lower() + data['persona'][1:] if len(data['persona']) > 1 else data['persona'].lower()
            interviewee_kwargs.append({
                "baseline_name": "persona_hub",
                "persona": data['persona'],
                "name": data['name'],
                "nhd_model": args.nhd_model,
                "nhd_port": args.nhd_port,
                "simulator_model": args.simulator_model,
                "simulator_host": args.simulator_host,
                "port": args.simulator_port,
            })
    
    elif args.baseline_name == "human_interview":
        interviewee_kwargs.append({
            "baseline_name": "human_interview",
            "name": input("Enter your name: "),
            "nhd_model": args.nhd_model,
            "nhd_port": args.nhd_port,
        })
    
    elif args.baseline_name == "twin_2k_500":
        dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona", split="data")
        for data in dataset:
            name = f"Twin-{data['pid']}"
            interviewee_kwargs.append({
                "baseline_name": "twin_2k_500",
                "simulator_model": args.simulator_model,
                "persona": data['persona_json'],
                "name": name,
                "nhd_model": args.nhd_model,
                "port": args.simulator_port,
                "simulator_host": args.simulator_host,
            })
    
    elif args.baseline_name == "deeppersona":
        dataset_path = "/home/data_storage/deeppersona"
        persona_files = glob.glob(os.path.join(dataset_path, "*.json"))
        for persona_file in persona_files:
            data = read_json(persona_file)
            name = os.path.basename(persona_file).replace(".json", "")
            interviewee_kwargs.append({
                "baseline_name": "deeppersona",
                "simulator_model": args.simulator_model,
                "persona": data,
                "name": name,
                "nhd_model": args.nhd_model,
                "port": args.simulator_port,
                "simulator_host": args.simulator_host,
            })
    
    elif args.baseline_name == "llm_generated":
        dataset = load_dataset("Tianyi-Lab/Personas", split="train")
        preferred_prefixes = ["Llama-3.1-70B-Instruct"]
        available_prefixes = [
            col[: -len("_descriptive_persona")]
            for col in dataset.column_names
            if col.endswith("_descriptive_persona")
        ]
        selected_prefix = None
        for prefix in preferred_prefixes:
            if prefix in available_prefixes:
                selected_prefix = prefix
                break
        if selected_prefix is None and available_prefixes:
            selected_prefix = available_prefixes[0]
        if selected_prefix is None:
            raise ValueError("No persona columns found in Tianyi-Lab/Personas.")
        
        for data in dataset:
            persona_number = data.get("persona_number")
            persona = {
                "meta_persona": data.get("meta_persona", ""),
                "descriptive_persona": data.get(f"{selected_prefix}_descriptive_persona", ""),
                "objective_table_persona": data.get(f"{selected_prefix}_objective_table_persona", ""),
                "subjective_table_persona": data.get(f"{selected_prefix}_subjective_table_persona", ""),
            }
            interviewee_kwargs.append({
                "baseline_name": "llm_generated",
                "simulator_model": args.simulator_model,
                "persona": persona,
                "name": f"LLM-Persona-{persona_number}" if persona_number is not None else "LLM-Persona-unknown",
                "nhd_model": args.nhd_model,
                "port": args.simulator_port,
                "simulator_host": args.simulator_host,
            })
    
    else:
        raise ValueError(f"Invalid baseline name: {args.baseline_name}")
    
    # Randomly select ONE persona from the baseline
    if not interviewee_kwargs:
        raise ValueError(f"No personas found for baseline: {args.baseline_name}")
    
    selected_kwargs = random.choice(interviewee_kwargs)
    logging.info(f"Selected persona: {selected_kwargs.get('name', 'unknown')} from baseline: {args.baseline_name}")
    
    # Create environment with selected persona
    tools = {
        "google_claim_search": GoogleClaimSearch(
            api_key=os.environ.get('GOOGLE_CLAIM_SEARCH'),
            cx=os.environ.get('GOOGLE_CX_ID')
        ),
        "google_geocode_validate": GoogleGeocodeValidate(api_key=os.environ.get('GOOGLE_GEOCODE'))
    }
    
    env = QuestionerTestEnv(
        model=args.model,
        tools=tools,
        max_turns=args.max_turns,
        human_interviewer=args.human_interviewer,
        **selected_kwargs
    )
    
    # Run the test
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()
    env.finalize()
    
    # Save results
    output_dir = f"data/prompt_engineering/questioner/{args.baseline_name}"
    os.makedirs(output_dir, exist_ok=True)
    persona_name = selected_kwargs.get('name', 'unknown').replace(' ', '_')
    env.save_state(f"{output_dir}/questioner_test_{persona_name}_{time.strftime('%Y%m%d_%H%M%S')}.json")