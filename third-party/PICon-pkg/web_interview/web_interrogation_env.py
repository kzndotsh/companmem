"""
Web-compatible InterrogationEnv that works with HTTP request/response pattern.
Replaces blocking input() with a state machine approach.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from picon.agents.base_agent import Agent
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput, IntervieweeResponse
from picon.utils import read_json, get_completion
from litellm.cost_calculator import completion_cost
from concurrent.futures import ThreadPoolExecutor
import random
import os
import uuid

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

REPEAT_PROMPT = """You will be given a single question and two corresponding answers. Determine whether the two answers are essentially the same in meaning.
If they are, output TRUE. If they are not, output FALSE.
Do not output any additional explanation or text."""


class WebInterrogationEnv:
    """
    Web-compatible interview environment using state machine pattern.
    Instead of blocking on input(), it returns questions and waits for responses via HTTP.
    """
    
    # Interview phases
    PHASE_INIT = "init"
    PHASE_PREDEFINED = "predefined"
    PHASE_MAIN = "main"
    PHASE_REPEAT = "repeat"
    PHASE_COMPLETE = "complete"
    
    def __init__(
        self, 
        questioner_model: str, 
        web_search_model: str,
        extractor_model: str,
        evaluator_model: str,
        agents: Dict[str, Agent] = {},
        baseline_name: str = "human_interview",
        tools: Dict = {},
        max_turns: int = 50,
        question_path: str = "src/env/wvs_orthogonal_questions.json",
        instruction_path: str = "src/env/interrogation_instruct.txt",
        **kwargs
    ):
        # Random seed for reproducibility
        seed = kwargs.get('question_seed', 42)
        # local_rng = random.Random(seed)
        
        self.tools = tools
        self.questioner_model = questioner_model
        self.web_search_model = web_search_model
        self.extractor_model = extractor_model
        self.evaluator_model = evaluator_model
        
        if not agents:
            logging.warning("No agents provided. Initializing default agents.")
            agents = {
                "questioner": get_agent("questioner", f"{project_root}/src/agents/prompts/questioner.txt", model=questioner_model),
                "extractor": get_agent("entity_extractor", f"{project_root}/src/agents/prompts/entity_extractor.txt", model=extractor_model),
                "web_search": get_agent("web_search", f"{project_root}/src/agents/prompts/websearch_prompt.txt", model=web_search_model),
                "evaluator": get_agent("evaluator", f"{project_root}/src/agents/prompts/evaluator_prompt.txt", model=evaluator_model),
            }
        self.agents = agents
        
        if 'web_search' in self.agents and self.tools:
            self.agents['web_search'].tools = [tool.get_info() for tool in self.tools.values()]
        
        # Create a minimal interviewee object (just holds name, no input() calls)
        # Use the name passed in kwargs, or generate a UUID if not provided
        interviewee_name = kwargs.get('name', str(uuid.uuid4())[:8])
        self.interviewee = WebInterviewee(
            name=interviewee_name,
            nhd_model=kwargs.get('nhd_model', 'gpt-5-nano')
        )
        
        self.max_turns = max_turns
        questions = read_json(question_path)
        random.shuffle(questions)
        self.predefined_questions = questions
        self.instruction = open(instruction_path).read()
        # Load confirmation prompt from file (same as original InterrogationEnv)
        self.confirmation_prompt = open(f"{project_root}/src/agents/prompts/confirmation_prompt.txt").read()
        self.state = State(current_turn=0, history=[])
        self.cutoff_date = time.strftime("%B %d, %Y")
        self.start_time = None
        self.env_cost = 0.0
        self._executor = ThreadPoolExecutor(max_workers=4)

        self.agents['questioner'].set_cutoff_date(self.cutoff_date)
        self.agents['web_search'].set_cutoff_date(self.cutoff_date)
        self.agents['evaluator'].set_cutoff_date(self.cutoff_date)
        
        # Repeat tracking
        self.repeat_score = 0
        self.repeat_results = []
        
        # State machine
        self.current_phase = self.PHASE_INIT
        self.predefined_index = 0
        self.main_turn_count = 0
        self.repeat_index = 0
        self.is_complete = False
        
        # Pending question (waiting for response)
        self.pending_question: Optional[str] = None
        self.pending_confirmations: List[str] = []  # Queue of confirmation questions
        self._last_confirmation_question: Optional[str] = None
        
    def get_progress(self) -> dict:
        """Get current progress information."""
        total_predefined = len(self.predefined_questions)
        total_main = self.max_turns
        total_repeat = len(self.predefined_questions)
        total = total_predefined + total_main + total_repeat
        
        if self.current_phase == self.PHASE_PREDEFINED:
            current = self.predefined_index
        elif self.current_phase == self.PHASE_MAIN:
            current = total_predefined + self.main_turn_count
        elif self.current_phase == self.PHASE_REPEAT:
            current = total_predefined + total_main + self.repeat_index
        elif self.current_phase == self.PHASE_COMPLETE:
            current = total
        else:
            current = 0
            
        return {
            "current": current,
            "total": total,
            "phase": self.current_phase,
            "predefined_complete": self.predefined_index,
            "predefined_total": total_predefined,
            "main_complete": self.main_turn_count,
            "main_total": total_main,
            "repeat_complete": self.repeat_index,
            "repeat_total": total_repeat,
        }
    
    def initialize(self) -> Tuple[str, str]:
        """Initialize the interview. Returns (instruction, first_question)."""
        self.start_time = time.time()
        self.instruction = self.instruction.format(cutoff_date=self.cutoff_date)
        
        # Move to predefined phase
        self.current_phase = self.PHASE_PREDEFINED
        self.predefined_index = 0
        
        # Get first predefined question
        first_question = self.predefined_questions[0]['question']
        self.pending_question = first_question
        
        return self.instruction, first_question
    
    def process_response(self, response: str, is_confirmation: bool = False) -> dict:
        """
        Process user response and return the next question or completion status.
        Returns dict with: next_question, phase, progress, is_complete, confirmation_question
        
        Args:
            response: The user's response text
            is_confirmation: If True, this response is for a confirmation question
        """
        if self.is_complete:
            return {
                "next_question": None,
                "phase": self.PHASE_COMPLETE,
                "progress": self.get_progress(),
                "is_complete": True
            }
        
        # Handle confirmation question response
        if is_confirmation:
            return self._handle_confirmation_response(response)
        
        # Handle response based on current phase
        if self.current_phase == self.PHASE_PREDEFINED:
            return self._handle_predefined_response(response)
        elif self.current_phase == self.PHASE_MAIN:
            return self._handle_main_response(response)
        elif self.current_phase == self.PHASE_REPEAT:
            return self._handle_repeat_response(response)
        else:
            raise ValueError(f"Invalid phase: {self.current_phase}")
    
    def _handle_confirmation_response(self, response: str) -> dict:
        """Handle response to a confirmation question."""
        # The confirmation question was already stored, we need to get it
        # For now, we'll track the last confirmation question asked
        confirmation_question = getattr(self, '_last_confirmation_question', "confirmation question")
        
        logging.info(f"[CONFIRMATION RESPONSE] {self.interviewee.name}: {response}")
        
        # Update agent memories with confirmation Q&A
        self.agents['evaluator'].update_memory(role="assistant", content=confirmation_question)
        self.agents['evaluator'].update_memory(role="user", content=response)
        self.agents['questioner'].update_memory(role="assistant", content=confirmation_question)
        self.agents['questioner'].update_memory(role="user", content=response)
        
        # Add confirmation response to the last turn's observations
        if self.state.history:
            confirmation_response = self._create_interviewee_response(confirmation_question, response)
            self.state.history[-1].environment_observation.append(
                Observation(observation_type="interviewee_response", response=confirmation_response)
            )
        
        # Check if there are more pending confirmation questions
        if self.pending_confirmations:
            next_confirmation = self.pending_confirmations.pop(0)
            self._last_confirmation_question = next_confirmation
            return {
                "next_question": None,
                "confirmation_question": next_confirmation,
                "phase": self.current_phase,
                "progress": self.get_progress(),
                "is_complete": False
            }
        
        # No more confirmations - continue with next question based on current phase
        if self.current_phase == self.PHASE_PREDEFINED:
            if self.predefined_index >= len(self.predefined_questions):
                self.current_phase = self.PHASE_MAIN
                self.main_turn_count = 0
                return self._generate_main_question()
            else:
                next_q = self.predefined_questions[self.predefined_index]['question']
                self.pending_question = next_q
                return {
                    "next_question": next_q,
                    "phase": self.current_phase,
                    "progress": self.get_progress(),
                    "is_complete": False
                }
        elif self.current_phase == self.PHASE_MAIN:
            return self._generate_main_question()
        else:
            return self._generate_repeat_question()
    
    def _create_interviewee_response(self, question: str, response: str) -> IntervieweeResponse:
        """Create an IntervieweeResponse object."""
        return IntervieweeResponse(question=question, content=response)
    
    def _handle_predefined_response(self, response: str) -> dict:
        """Handle response during predefined questions phase."""
        q = self.predefined_questions[self.predefined_index]
        question = q['question']
        
        # Create response object
        interviewee_response = self._create_interviewee_response(question, response)
        
        # Update agent memories
        self.agents['evaluator'].update_memory(role="assistant", content=question)
        self.agents['questioner'].update_memory(role="assistant", content=question)
        self.agents['evaluator'].update_memory(role="user", content=response)
        self.agents['questioner'].update_memory(role="user", content=response)
        
        # Check external consistency
        entity_action, web_observations, web_search_actions = self.check_external(
            f"Question: {question}\nResponse: {response}"
        )
        
        # Create turn record
        res_observation = Observation(
            observation_type="interviewee_response",
            response=interviewee_response
        )
        
        if web_search_actions:
            turn = Turn(
                type='get_to_know', 
                agent_action=[entity_action, *web_search_actions], 
                environment_observation=[res_observation, *web_observations]
            )
        else:
            turn = Turn(
                type='get_to_know', 
                agent_action=[entity_action], 
                environment_observation=[res_observation]
            )
        
        self.state.history.append(turn)
        self.state.current_turn += 1
        
        # Move to next predefined question or switch to main phase
        self.predefined_index += 1
        
        # Check if there are pending confirmation questions
        if self.pending_confirmations:
            confirmation_q = self.pending_confirmations.pop(0)
            self._last_confirmation_question = confirmation_q
            return {
                "next_question": None,
                "confirmation_question": confirmation_q,
                "phase": self.current_phase,
                "progress": self.get_progress(),
                "is_complete": False
            }
        
        if self.predefined_index >= len(self.predefined_questions):
            # Switch to main interrogation phase
            self.current_phase = self.PHASE_MAIN
            self.main_turn_count = 0
            return self._generate_main_question()
        else:
            # Next predefined question
            next_q = self.predefined_questions[self.predefined_index]['question']
            self.pending_question = next_q
            return {
                "next_question": next_q,
                "phase": self.current_phase,
                "progress": self.get_progress(),
                "is_complete": False
            }
    
    def _generate_main_question(self) -> dict:
        """Generate a main interrogation question using the questioner agent."""
        if self.main_turn_count >= self.max_turns:
            # Switch to repeat phase
            self.current_phase = self.PHASE_REPEAT
            self.repeat_index = 0
            return self._generate_repeat_question()
        
        # Use questioner agent to generate question
        question_act = self.agents['questioner'].act()
        question = question_act.content
        
        logging.info(f"[QUESTIONER] Generated question: {question}")
        
        self.pending_question = question
        return {
            "next_question": question,
            "phase": self.current_phase,
            "progress": self.get_progress(),
            "is_complete": False
        }
    
    def _handle_main_response(self, response: str) -> dict:
        """Handle response during main interrogation phase."""
        question = self.pending_question
        
        # Create response object
        interviewee_response = self._create_interviewee_response(question, response)
        
        logging.info(f"[RESPONSE] {self.interviewee.name}: {response}")
        
        # Update agent memories
        self.agents['evaluator'].update_memory(role="assistant", content=question)
        self.agents['questioner'].update_memory(role="user", content=response)
        self.agents['evaluator'].update_memory(role="user", content=response)
        
        # Check external consistency
        entity_action, observations, web_search_actions = self.check_external(
            f"Question: {question}\nResponse: {response}"
        )
        
        self.main_turn_count += 1
        self.state.current_turn += 1
        
        # Create turn record
        res_observation = Observation(observation_type="interviewee_response", response=interviewee_response)
        observations = [res_observation, *observations]
        actions = [Action(action_type="respond", content=question), entity_action]
        if web_search_actions:
            actions.extend(web_search_actions)
        
        turn = Turn(
            type='main_interrogation',
            agent_action=actions,
            environment_observation=observations
        )
        self.state.history.append(turn)
        
        # Check if there are pending confirmation questions
        if self.pending_confirmations:
            confirmation_q = self.pending_confirmations.pop(0)
            self._last_confirmation_question = confirmation_q
            return {
                "next_question": None,
                "confirmation_question": confirmation_q,
                "phase": self.current_phase,
                "progress": self.get_progress(),
                "is_complete": False
            }
        
        # Generate next question
        return self._generate_main_question()
    
    def _generate_repeat_question(self) -> dict:
        """Generate a repeat question."""
        if self.repeat_index >= len(self.predefined_questions):
            # Interview complete
            self.current_phase = self.PHASE_COMPLETE
            self.is_complete = True
            return {
                "next_question": None,
                "phase": self.current_phase,
                "progress": self.get_progress(),
                "is_complete": True
            }
        
        q = self.predefined_questions[self.repeat_index]['question']
        repeat_question = f"Just to clarify, {q}"
        self.pending_question = repeat_question
        
        return {
            "next_question": repeat_question,
            "phase": self.current_phase,
            "progress": self.get_progress(),
            "is_complete": False
        }
    
    def _handle_repeat_response(self, response: str) -> dict:
        """Handle response during repeat phase."""
        q = self.predefined_questions[self.repeat_index]
        question = f"Just to clarify, {q['question']}"
        
        # Create response object
        interviewee_response = self._create_interviewee_response(question, response)
        
        # Create turn record
        action = Action(action_type="respond", content=q['question'])
        observation = Observation(
            observation_type="interviewee_response",
            response=interviewee_response
        )
        turn = Turn(type='repeat', agent_action=[action], environment_observation=[observation])
        self.state.history.append(turn)
        
        
        # Move to next repeat question
        self.repeat_index += 1
        
        return self._generate_repeat_question()
    
    def check_external(self, message: str) -> Tuple[Action, List[Observation], List[Action]]:
        """Check external consistency (same as original InterrogationEnv)."""
        observations = []
        next_action = self.agents["extractor"].act(message)
        
        logging.info(f"[EXTRACTOR] {next_action.action_type} - {next_action.content if next_action.content else next_action.target_agent}")
        
        if next_action.action_type == "next_agent":
            return next_action, observations, []
        elif next_action.action_type == "respond":
            if next_action.content is None:
                return next_action, observations, []
            
            list_of_extractions = [ext.model_dump() for ext in next_action.content]
            history = []
            for turn in self.state.history:
                qa_pair = turn.environment_observation[0].response
                history.append({
                    "question": qa_pair.question,
                    "answer": qa_pair.content
                })
            
            # Web search
            web_search_actions = list(self._executor.map(
                self.agents['web_search'].act,
                list_of_extractions,
                [history] * len(list_of_extractions)
            ))

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
                        {"role": "user", "content": message},
                        filtered_actions[i].tool_call.details,
                        {
                            "role": "tool",
                            "tool_call_id": output.tool_call_id,
                            "name": output.tool_name,
                            "content": f"Entity:{list_of_extractions[filtered_actions_indices[i]]['entity']}\nClaims: {list_of_extractions[filtered_actions_indices[i]]['claims']}\nRationale: {list_of_extractions[filtered_actions_indices[i]]['rationale']}\nSearch Result:{str(output.output)}"
                        }
                    ]
                    
                    """tool call 결과를 evaluator 메모리에 추가"""
                    self.agents['evaluator'].update_memory(**sub_message[1])
                    self.agents['evaluator'].update_memory(**sub_message[2])
                    
                    # Generate confirmation question (same as original InterrogationEnv)
                    messages = [
                        {
                            "role": "system",
                            "content": self.confirmation_prompt
                        },
                    ]
                    messages.extend(sub_message)
                    res = get_completion(
                        model=self.questioner_model,
                        messages=messages,
                        reasoning_effort="low",
                    )
                    self.env_cost += completion_cost(res)
                    confirmation_question = res.choices[0].message.content.strip()
                    
                    if "SKIP" not in confirmation_question:
                        logging.info(f"[CONFIRMATION QUESTION] {confirmation_question}")
                        # Add confirmation question to queue for web interface to handle
                        self.pending_confirmations.append(confirmation_question)
                    else:
                        logging.info("Confirmation question skipped as per web search agent's decision.")
            
            return next_action, observations, filtered_actions
        
        return next_action, observations, []
    
    def invoke_tool(self, action: Action) -> Optional[ToolOutput]:
        """Invoke a tool."""
        if action.action_type == "tool_call":
            tool_name = action.tool_call.tool_name
            if tool_name not in self.tools:
                logging.error(f"Tool {tool_name} not found.")
                return None
            
            tool = self.tools[tool_name]
            tool_output = tool.invoke(**action.tool_call.arguments)
            logging.info(f"[TOOL OUTPUT] {tool_name}: {tool_output[:100]}...")
            
            return ToolOutput(
                tool_call_id=action.tool_call.details.get('tool_calls')[0].get('id'),
                tool_name=tool_name,
                output=tool_output
            )
        return None
    
    def save_state(self, termination_status: str = "Successfully completed") -> dict:
        """Save the current state."""
        agent_cost = sum(agent.cost for agent in self.agents.values())
        interviewee_cost = self.interviewee.cost
        tool_costs = sum(tool.calculate_cost() for tool in self.tools.values())
        total_cost = agent_cost + interviewee_cost + self.env_cost + tool_costs

        return {
            "interview_date": self.cutoff_date,
            "agents_info": {agent_name: agent.model for agent_name, agent in self.agents.items()},
            "interviewee_info": {
                "name": self.interviewee.name,
                "baseline": "human_interview",
            },
            "cost": {
                "agents_cost": agent_cost,
                "interviewee_cost": interviewee_cost,
                "environment_cost": self.env_cost,
                "tool_costs": {tool_name: tool.calculate_cost() for tool_name, tool in self.tools.items()},
                "total_cost": total_cost
            },
            "duration": f"{(time.time() - self.start_time)/60} min" if self.start_time else "N/A",
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
            "agent_memory": {
                agent_name: agent.memory for agent_name, agent in self.agents.items()
            },
        }

    def serialize_for_redis(self) -> dict:
        """Serialize environment state for Redis storage."""
        return {
            "name": self.interviewee.name,
            "current_phase": self.current_phase,
            "predefined_index": self.predefined_index,
            "main_turn_count": self.main_turn_count,
            "repeat_index": self.repeat_index,
            "is_complete": self.is_complete,
            "state_current_turn": self.state.current_turn,
            "state_history": [turn.model_dump() for turn in self.state.history],
            "agent_memories": {
                agent_name: agent.memory for agent_name, agent in self.agents.items()
            },
            "agent_costs": {
                agent_name: agent.cost for agent_name, agent in self.agents.items()
            },
            "pending_question": self.pending_question,
            "pending_confirmations": self.pending_confirmations,
            "last_confirmation_question": getattr(self, '_last_confirmation_question', None),
            "repeat_score": self.repeat_score,
            "repeat_results": self.repeat_results,
            "env_cost": self.env_cost,
            "start_time": self.start_time,
            "cutoff_date": self.cutoff_date,
            # Store the shuffled questions order to preserve on recovery
            "predefined_questions": self.predefined_questions,
        }
    
    def restore_from_redis(self, data: dict) -> None:
        """Restore environment state from Redis data."""
        # Restore phase/progress state
        self.current_phase = data["current_phase"]
        self.predefined_index = data["predefined_index"]
        self.main_turn_count = data["main_turn_count"]
        self.repeat_index = data["repeat_index"]
        self.is_complete = data["is_complete"]
        
        # Restore state history
        self.state.current_turn = data["state_current_turn"]
        self.state.history = [Turn(**turn_data) for turn_data in data["state_history"]]
        
        # Restore agent memories
        for agent_name, memory in data["agent_memories"].items():
            if agent_name in self.agents:
                self.agents[agent_name].memory = memory
        
        # Restore agent costs
        for agent_name, cost in data.get("agent_costs", {}).items():
            if agent_name in self.agents:
                self.agents[agent_name].cost = cost
        
        # Restore pending questions
        self.pending_question = data["pending_question"]
        self.pending_confirmations = data["pending_confirmations"]
        self._last_confirmation_question = data.get("last_confirmation_question")
        
        # Restore tracking
        self.repeat_score = data["repeat_score"]
        self.repeat_results = data["repeat_results"]
        self.env_cost = data["env_cost"]
        self.start_time = data["start_time"]
        self.cutoff_date = data["cutoff_date"]
        
        # Restore the original shuffled questions order
        if "predefined_questions" in data:
            self.predefined_questions = data["predefined_questions"]
        
        logging.info(f"[REDIS] Restored session for {self.interviewee.name} at phase={self.current_phase}, turn={self.state.current_turn}")


class WebInterviewee:
    """Minimal interviewee class for web interface (no input() calls)."""
    
    def __init__(self, name: str, nhd_model: str = "gpt-5"):
        self.name = name
        self.type = "human_interview"
        self.nhd_model = nhd_model
        self.cost = 0.0
    
    def calculate_cost(self) -> float:
        return self.cost
