"""
InterrogationEnv v2 — uses the unified GenericAgentSimulator via simulator_v2 factory.

Only the simulator factory import differs from the original InterrogationEnv.
The reset() method is overridden to use the v2 factory; all other logic is identical.
"""
import time
import logging
import time
from typing import List, Dict, Any
from picon.agents.base_agent import Agent
from picon.env.interviewee_simulator.simulator_factory import get_interviewee_simulator
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput
from picon.tools.address_locator import GoogleGeocodeValidate
from picon.tools.web_search import GoogleClaimSearch, SerperSearch
from picon.utils import read_json, get_completion
from picon.config import get_prompt_path, get_question_path, DEFAULT_CONFIG
from importlib import resources
import logging
from litellm.cost_calculator import completion_cost
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import random
import asyncio
from picon.env.interviewee_simulator.simulator_factory import get_interviewee_simulator
from picon.schemas import State, Action, Observation, Turn

class InterrogationEnv:
    def __init__(
        self, 
        agents: Dict[str, Agent] = {},
        baseline_name: str = "characterai",
        tools: Dict[str, Any] = {},
        max_turns: int = 20,
        question_path: str = None,
        instruction_path: str = None,
        result_data=None,
        **kwargs
        ):
        
        # random seed for reproducibility
        seed = kwargs.get('question_seed', 42)
        local_rng = random.Random(seed)
        
        self.tools = tools
        if not agents:
            logging.warning("No agents provided. Initializing default agents.")
            agents = {
                "questioner": get_agent("questioner", get_prompt_path("questioner.txt"), model=kwargs.get('questioner_model', DEFAULT_CONFIG["questioner_model"]), port=None),
                "extractor": get_agent("claim_extractor", get_prompt_path("claim_extractor_prompt.txt"), model=kwargs.get('extractor_model', DEFAULT_CONFIG["extractor_model"])) if kwargs.get('use_claim_extractor', False) else get_agent("entity_extractor", get_prompt_path("entity_extractor.txt"), model=kwargs.get('extractor_model', DEFAULT_CONFIG["extractor_model"]), port=None),
                "web_search": get_agent("web_search", get_prompt_path("websearch_prompt.txt"), model=kwargs.get('web_search_model', DEFAULT_CONFIG["web_search_model"]), port=None),
                "evaluator": get_agent("evaluator", get_prompt_path("evaluator_prompt.txt"), model=kwargs.get('evaluator_model', DEFAULT_CONFIG["evaluator_model"]), port=None),
            }
        self.agents = agents
        
        if not result_data : 
            if 'web_search' in self.agents and not self.tools:
                logging.warning("No tools provided for web search agent.")
            if 'web_search' in self.agents and not self.agents['web_search'].tools:
                logging.info("Setting web search agent tools from environment.")
                self.agents['web_search'].tools = [tool.get_info() for tool in self.tools.values()]
            
            self.baseline_name = baseline_name
            self.interviewee_kwargs = kwargs
            
            self.max_turns = max_turns
            questions = read_json(question_path or get_question_path())
            local_rng.shuffle(questions)
            self.predefined_questions = questions
            _inst_path = instruction_path or str(resources.files("picon.env").joinpath("interrogation_instruct.txt"))
            self.instruction = open(_inst_path).read()
            self.confirmation_prompt = open(get_prompt_path("confirmation_prompt.txt")).read()
            self.env_cost = 0.0
            self._executor = ThreadPoolExecutor(max_workers=4)

            self.cutoff_date = time.strftime("%B %d, %Y")
            self.agents['questioner'].set_cutoff_date(self.cutoff_date)
            self.agents['web_search'].set_cutoff_date(self.cutoff_date)
            self.agents['evaluator'].set_cutoff_date(self.cutoff_date)
            self.instruction = self.instruction.format(cutoff_date=self.cutoff_date)
        else:
            self.cutoff_date = result_data['session_1']["interview_date"]
            self.agents['evaluator'].set_cutoff_date(self.cutoff_date)

    def shutdown(self):
        """Shut down the shared thread pool."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

    def invoke_tool(self, action: Action) -> Observation | None:
        if action.action_type == "tool_call":
            tool_name = action.tool_call.tool_name
            if tool_name not in self.tools:
                logging.error(f"Tool {tool_name} not found.")
                return self.state, True
            
            
            tool = self.tools[tool_name]
            tool_output = tool.invoke(**action.tool_call.arguments) # if 'claim' in action.tool_call.arguments else tool.invoke_batch(**action.tool_call.arguments) # batch for claims list
            logging.info(f"[TOOL OUTPUT] {tool_name}: {tool_output[:100]}...") # print first 100 chars
            
            output = ToolOutput(
                tool_call_id=action.tool_call.details.get('tool_calls')[0].get('id'),
                tool_name=tool_name,
                arguments=action.tool_call.arguments,
                output=tool_output
            )
            return output
        return None

    # def reset(self, reset_only: bool = False) -> State:
    #     """Reset the environment and run predefined questions to initialize the interview state"""
    #     self.state = State(current_turn=0, history=[])
    #     self.start_time = None
        
    #     self.interviewee = get_interviewee_simulator(
    #         baseline_name=self.baseline_name,
    #         **self.interviewee_kwargs # simulator specific args (character_id, user_id, name for characterai; model_path, persona, profile for opencharacter; name for human_simulacra)
    #     )
    #     self.start_time = time.time()
    #     # feed interview instruction to the interviewee
    #     logging.info(f"[INSTRUCTION] {self.instruction}")
    #     response = self.interviewee.get_response(self.instruction)
    #     logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
    #     # run predefined questions
    #     for i, q in enumerate(self.predefined_questions):
    #         logging.info(f"[QUESTION] {q['question']}")
    #         response = self.interviewee.get_response(q['question'])
    #         logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")    
    #         # update state
    #         action = Action(action_type="respond", content=q['question'])
    #         res_observation = Observation(
    #             observation_type="interviewee_response",
    #             response=response
    #         )
            
            
    #         self.state.current_observation = res_observation
    #         self.state.current_turn += 1
    #         if reset_only:
    #             self.state.history.append(
    #                 Turn(type='get_to_know', agent_action=[action], environment_observation=[res_observation])
    #             )
    #             continue
            
    #         self.agents['evaluator'].update_memory(role="assistant", content=q['question'])
    #         self.agents['questioner'].update_memory(role="assistant", content=q['question'])
    #         self.agents['evaluator'].update_memory(role="user", content=response.content)
    #         self.agents['questioner'].update_memory(role="user", content=response.content)
            
    #         entity_action, web_observations, web_search_actions = self.check_external(
    #             f"Question: {q['question']}\nResponse: {response.content}"
    #         )
            
    #         if web_search_actions:
    #             turn = Turn(type='get_to_know', agent_action=[entity_action, *web_search_actions], environment_observation=[res_observation, *web_observations])
    #         else:
    #             turn = Turn(type='get_to_know', agent_action=[entity_action], environment_observation=[res_observation])
            
    #         self.state.history.append(turn)
    #     return self.state

    def reset(self, reset_only: bool = False) -> State:
        """Reset the environment using v2 simulator factory. Logic is identical to parent."""
        self.state = State(current_turn=0, history=[])
        self.start_time = None

        # v2: use unified GenericAgentSimulator
        self.interviewee = get_interviewee_simulator(
            baseline_name=self.baseline_name,
            **self.interviewee_kwargs
        )
        self.start_time = time.time()

        # Feed interview instruction
        logging.info(f"[INSTRUCTION] {self.instruction}")
        response = self.interviewee.get_response(self.instruction)
        logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")

        # Run predefined questions
        for i, q in enumerate(self.predefined_questions):
            logging.info(f"[QUESTION] {q['question']}")
            response = self.interviewee.get_response(q['question'])
            logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")

            action = Action(action_type="respond", content=q['question'])
            res_observation = Observation(
                observation_type="interviewee_response",
                response=response
            )

            self.state.current_observation = res_observation
            self.state.current_turn += 1

            if reset_only:
                self.state.history.append(
                    Turn(type='get_to_know', agent_action=[action], environment_observation=[res_observation])
                )
                continue

            self.agents['evaluator'].update_memory(role="assistant", content=q['question'])
            self.agents['questioner'].update_memory(role="assistant", content=q['question'])
            self.agents['evaluator'].update_memory(role="user", content=response.content)
            self.agents['questioner'].update_memory(role="user", content=response.content)

            entity_action, web_observations, web_search_actions = self.check_external(
                f"Question: {q['question']}\nResponse: {response.content}"
            )

            if web_search_actions:
                turn = Turn(type='get_to_know', agent_action=[entity_action, *web_search_actions], environment_observation=[res_observation, *web_observations])
            else:
                turn = Turn(type='get_to_know', agent_action=[entity_action], environment_observation=[res_observation])

            self.state.history.append(turn)

        return self.state

    def check_external(self, message : str) -> tuple[Action, List[Observation], List[Action]]:
        # 1. Extractor first extracts the entity & claim to verify
        observations = []
        next_action = self.agents["extractor"].act(message)
        logging.info(f"[ACTION] Extractor: {next_action.action_type} - {next_action.content if next_action.content else next_action.target_agent}")
        if next_action.action_type == "next_agent":
            if next_action.target_agent != "questioner":
                logging.error("Extractor can only pass to Questioner.")
                return self.state, True
            logging.info("No entity or claim extracted. Passing to Questioner.")
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
            web_search_actions = list(self._executor.map(self.agents['web_search'].act, list_of_extractions, [history]*len(list_of_extractions)))
            filtered_actions = []
            filtered_actions_indices = []
            for i, action in enumerate(web_search_actions):
                if action and action.action_type == "tool_call":
                    filtered_actions.append(action)
                    filtered_actions_indices.append(i)

            if filtered_actions:
                tool_outputs = list(self._executor.map(self.invoke_tool, filtered_actions))

                observations.append(Observation(
                    observation_type="tool_output",
                    tool_output=tool_outputs
                ))
                
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
                            #"content": f"Entity:{list_of_extractions[filtered_actions_indices[i]]['entity']}\nSearch Result:{str(output.output)}"
                        }
                    ]
                    """tool call 결과를 evaluator 메모리에 추가"""
                    self.agents['evaluator'].update_memory(**sub_message[1]) ####### 여기 #######
                    #tool_output = sub_message[2]
                    #tool_output['claim'] = str(list_of_extractions[filtered_actions_indices[i]]['claims'])
                    self.agents['evaluator'].update_memory(**sub_message[2]) ####### 여기 ####y
                    ###
                    messages = [
                        {
                            "role": "system",
                            "content": self.confirmation_prompt 
                        },
                    ]
                    messages.extend(sub_message)
                    completion_kwargs = dict(
                        model=self.agents['questioner'].model,
                        messages=messages,
                        reasoning_effort="low",
                        timeout=60
                    )
                    if self.agents['questioner'].model.startswith("hosted_vllm/"):
                        assert self.agents['questioner'].port is not None, "Port must be specified for hosted_vllm models."    
                        completion_kwargs['api_base'] = f"http://localhost:{self.agents['questioner'].port}/v1"
                    if self.agents['questioner'].model.startswith("claude-"):
                        completion_kwargs.pop('reasoning_effort') # claude does not support reasoning_effort
                        completion_kwargs['tools']=[] # dummy tools to avoid tool usage
                    max_confirmation_retries = 5
                    for _conf_attempt in range(max_confirmation_retries):
                        res = get_completion(**completion_kwargs)
                        if res and res.choices and res.choices[0].message and res.choices[0].message.content:
                            break
                        logging.warning(f"Empty confirmation response (attempt {_conf_attempt + 1}/{max_confirmation_retries})")
                    else:
                        logging.warning(f"Failed to get confirmation response after {max_confirmation_retries} attempts. Skipping confirmation.")
                        continue
                    self.env_cost += completion_cost(res) if not self.agents['questioner'].model.startswith("hosted_vllm/") else 0.0
                    confirmation_question = res.choices[0].message.content.strip()
                    if "SKIP" not in confirmation_question:
                        logging.info(f"[CONFIRMATION QUESTION] {confirmation_question}")
                        response = self.interviewee.get_response(confirmation_question)
                        logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
                        observations.append(Observation(
                            observation_type="interviewee_response",
                            response=response
                        ))
                        self.agents['evaluator'].update_memory(role="assistant", content=confirmation_question) ####### 여기 #######
                        self.agents['evaluator'].update_memory(role="user", content=response.content) ####### 여기 #######
                        self.agents['questioner'].update_memory(role="assistant", content=confirmation_question) ####### 여기 #######
                        self.agents['questioner'].update_memory(role="user", content=response.content) ####### 여기 #######
                    
                    else:
                        logging.info("Confirmation question skipped as per web search agent's decision.")
            else:
                filtered_actions = []
        return next_action, observations, filtered_actions


    def step(self): # Interviewee's response -> Extractor -> WebSearch (optional) -> Questioner -> Interviewee
        """run one turn of the interrogation"""
        if self.state.current_turn >= self.max_turns:
            logging.warning("Max turns reached. Please reset the environment.")
            return self.state, True
        # verdict = self.state.history[-1].agent_action[-1].content if self.state.history else None
        # question_act = self.agents['questioner'].act(verdict=verdict)
        question_act = self.agents['questioner'].act()
        logging.info(f"[ACTION] Questioner: {question_act.action_type} - {question_act.content if question_act.content else question_act.tool_call.tool_name}")
        self.agents['evaluator'].update_memory(role="assistant", content=question_act.content)
        interviewee_res = self.interviewee.get_response(question_act.content)
        logging.info(f"[RESPONSE] {self.interviewee.name}: {interviewee_res.content}")
        
        self.agents['questioner'].update_memory(role="user", content=interviewee_res.content) 
        self.agents['evaluator'].update_memory(role="user", content=interviewee_res.content)

        entity_action, observations, web_search_actions = self.check_external(f"Question: {interviewee_res.question}\nResponse: {interviewee_res.content}")

        self.state.current_turn += 1

        actions = [question_act, entity_action, *web_search_actions] if web_search_actions else [question_act, entity_action]
        res_ob = Observation(observation_type="interviewee_response", response=interviewee_res)
        observations = [res_ob, *observations]
        turn = Turn(
            type='main_interrogation',
            agent_action=actions,
            environment_observation=observations
        )
        
        self.state.history.append(turn)

        return self.state, False

    def finalize(self):
        """repeat stage: repeat the pre-defined questions to check for consistency"""
        for i, q in enumerate(self.predefined_questions):
            logging.info(f"[REPEAT QUESTION] Just to clarify, {q['question']}")
            response = self.interviewee.get_response(f"Just to clarify, {q['question']}")
            logging.info(f"[RESPONSE] {self.interviewee.name}: {response.content}")
            # update state
            action = Action(action_type="respond", content=q['question'])
            observation = Observation(
                observation_type="interviewee_response",
                response=response
            )
            turn = Turn(type='repeat', agent_action=[action], environment_observation=[observation])
            self.state.history.append(turn)
        if self.interviewee.type == "characterai":
            asyncio.run(self.interviewee.close())
        return self.state
    
    def evaluate(self, histories: List[List[Turn]] = None, eval_factors: List[str] = None) -> Dict[str, Any]:
        """evaluate the entire interrogation session"""
        """use threading to parallelize the four evaluation tasks at once"""
        eval_action = self.agents['evaluator'].act(histories=histories, eval_factors=eval_factors)
        assert eval_action.action_type == "respond", "Evaluator must respond with evaluation."
        assert isinstance(eval_action.content, dict), "Evaluator response must be a dict."
        ### log the evaluation results key by key
        for key, value in eval_action.content.items():
            logging.info(f"[EVALUATION] {key}: {value}\n")
        return eval_action.content
    
    def save_state(self, termination_status: str = "Successfully completed") -> dict:
        """save the current state to a json file"""
        agent_cost = sum(agent.cost for agent in self.agents.values())
        interviewee_cost = self.interviewee.calculate_cost()
        tool_costs = sum(tool.calculate_cost() for tool in self.tools.values())
        total_cost = agent_cost + interviewee_cost + self.env_cost + tool_costs

        final_result={
            "interview_date": self.cutoff_date,
            "agents_info":{agent_name: agent.model for agent_name, agent in self.agents.items()},
            "interviewee_info": {
                "name": self.interviewee.name,
                "baseline": self.interviewee.type,
            },
            "cost": {
                "agents_cost": agent_cost,
                "interviewee_cost": interviewee_cost,
                "environment_cost": self.env_cost,
                "tool_costs": {tool_name: tool.calculate_cost() for tool_name, tool in self.tools.items()},
                "total_cost": total_cost
            },
            "duration": f"{(time.time() - self.start_time)/60} min", # in minutes
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
        }
        logging.info("Cost: (agent):" + ", ".join([f"{agent_name}: ${agent.cost}" for agent_name, agent in self.agents.items()]))
        logging.info(f"Cost: (interviewee): ${interviewee_cost}")
        logging.info(f"Cost: (environment): ${self.env_cost}")
        logging.info(f"Total cost: ${final_result['cost']['total_cost']}, Duration: {final_result['duration']}")
        return final_result

if __name__ == "__main__":
    from picon.utils import setup_logging
    setup_logging(log_to_file=True, process_name="test_env")
    load_dotenv()
    
    env = InterrogationEnv(
        model="gpt-5",
        baseline_name="characterai",
        character_id="6HhWfeDjetnxESEcThlBQtEUo0O8YHcXyHqCgN7b2hY", # example character id
        user_id=os.getenv('CAI_API_KEY'),
        name="Elon Musk",
        tools={
            "serper_search": SerperSearch(api_key=os.getenv('SERPER_API_KEY')),
            # "tavily_search": TavilySearch(api_key=os.getenv('TAVILY_API_KEY')),
            "google_geocode_validate": GoogleGeocodeValidate(api_key=os.getenv('GOOGLE_GEOCODE'))
        },
    )
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()
    state = env.finalize()
    evaluation = env.evaluate()
    final_result = env.save_state()

    
