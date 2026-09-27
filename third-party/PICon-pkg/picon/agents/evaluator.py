from typing import List, Dict, Any, Literal
import re
import time
from pydantic import BaseModel, Field, ValidationError
import logging
import litellm
import os
import json
import time
import threading
from picon.agents.base_agent import Agent
from picon.utils import get_completion
from picon.schemas import Action, Observation, Turn, ToolOutput
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

litellm.drop_params = True

# Thread-safe flag to detect if we're running in a nested thread context
_IN_THREAD_CONTEXT = threading.local()


def set_thread_context(in_thread: bool):
    """Set whether we're running inside a thread pool (to avoid nested threading deadlocks)."""
    _IN_THREAD_CONTEXT.value = in_thread

def is_in_thread_context() -> bool:
    """Check if we're running inside a thread pool."""
    return getattr(_IN_THREAD_CONTEXT, 'value', False)


class EvaluatorAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            role=kwargs.get('role', "evaluator"),
            system_message=kwargs.get('system_message', ""),
            model=kwargs['model'],
            port=kwargs.get('port', None),
            host=kwargs.get('host', 'localhost')
        )
        # Allow disabling internal threading to prevent deadlocks when called from threaded context
        self.use_internal_threading = kwargs.get('use_internal_threading', True)
        from picon.config import get_prompt_path
        self.REPEAT_PROMPT = ("You will be given a single question and two corresponding answers. Determine whether the two answers are essentially the same in meaning. "
                              "If they are, output TRUE. If they are not, output FALSE. "
                              "Do not output any additional explanation or text.")
        self.abstain_prompt = open(get_prompt_path("abstain.txt")).read()
        
        self.affirmative_prompt = (
            "Your task is to evaluate whether the interviewee's response affirms the search results provided.\n"
            "An affirmative response should clearly confirm the fact presented in the question/search result.\n"
            "**Affirmative (True):**\n"
            "The response clearly confirms the fact.\n"
            "- *Includes:* \"Yes\", \"Correct\", \"That's me\".\n\n"
            "**Non-Affirmative (False):**\n"
            "The response does not confirm the fact, is vague, or indicates uncertainty.\n"
            "- *Includes:* \"I don't know\", \"Maybe\", \"Not sure\", irrelevant answers.\n\n"
            "Please strictly follow the guidelines above when making your judgment."
        )
        self.fact_verification_prompt = (
            "You are a fact verification expert. Your task is to verify claims against search result evidence.\n\n"
            "**Labels:**\n"
            "1. **supported**: The search result provides clear evidence that supports/confirms the claim.\n"
            "2. **refuted**: The search result provides clear evidence that contradicts/refutes the claim.\n"
            "3. **nei** (not enough info): The search result does not contain sufficient information to verify or refute the claim.\n\n"
            "**Guidelines:**\n"
            "- Focus ONLY on whether the search result evidence supports or refutes the specific claim.\n"
            "- Do not make assumptions beyond what is explicitly stated in the search result.\n"
            "- If the search result is about a different entity or topic, classify as 'nei'.\n"
            "- If the search result confirms the entity exists but provides no info about the specific claim, classify as 'nei'.\n"
            "- Be strict: only classify as 'supported' if there is clear supporting evidence, and 'refuted' only if there is clear contradicting evidence."
        )
        self.affirmed_search_results = []  # Store affirmed search results for external consistency check
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.results_dict = {
            'internal': {
                'score': {
                    "harmonic_mean": 0.0,
                    "responsiveness_score": 0.0,
                    "consistency_score": 0.0         
                },
                'conflict': {
                    "count": 0,
                    "details": []
                },
                'plausible': {
                    "count": 0,
                    "details": []
                },
                'uncooperative': {
                    "count": 0,
                    "details": []
                },
            },
            'external': {
                'score': {
                    "ec_score": 0.0,
                    "coverage": 0.0,
                    "non_refutation_rate": 0.0,
                },
                'not_confirmed': {
                    "count": 0,
                    "details": []
                },
                'claims': {
                    'supported': {
                        "count": 0,
                        "details": []
                    },
                    'refuted': {
                        "count": 0,
                        "details": []
                    },
                    'nei': {
                        "count": 0,
                        "details": []
                    }
                }
            },
            'stability': {
                'inter_session': {
                    'score': 0.0,
                    "details": []
                },
                'intra_session': {
                    'score': 0.0,
                    "details": []
                }
            }
        }

    def set_cutoff_date(self, cutoff_date: str) -> None:
        self.memory[0]['content'] = self.memory[0]['content'].format(cutoff_date=cutoff_date)

    def _run_tasks(self, func, items, desc: str = "Processing"):
        """Run tasks either in parallel or sequentially based on threading context.

        When called from within a thread pool (nested threading), runs sequentially
        to prevent deadlocks. Otherwise uses the shared ThreadPoolExecutor for parallelism.
        """
        should_use_threading = self.use_internal_threading and not is_in_thread_context()

        if should_use_threading and len(items) > 1:
            return list(tqdm(self._executor.map(func, items), total=len(items), desc=desc))
        else:
            # Sequential execution - safer when in nested thread context
            return [func(item) for item in tqdm(items, desc=f"{desc} (sequential)")]

    def update_memory(self, **kwargs) -> None:
        if kwargs.get('index') is not None:
            index = kwargs.pop('index')
            assert 0 <= index <= len(self.memory), "Index out of range"
            # insert at specific index
            if index == len(self.memory):
                self.memory.append(kwargs)
            else:
                self.memory.insert(index, kwargs)
        else:
            self.memory.append(kwargs) # typically role and content

    def __generate_uncooperative_check(self, qa_pair: Dict[str, Any]):
        """Check if the answer is uncooperative (Step 1)"""
        class UncooperativeResponse(BaseModel):
            is_uncooperative: bool = Field(..., description="Whether the response is uncooperative (abstaining from answering)")
            rationale: str = Field(..., description="The rationale behind the verdict")
            uncooperative_type: Literal["none", "refusal", "lack_info", "asking_back", "unrelated"] | None = Field(None, description="Type of uncooperative response")
        
        user_content = "Question: " + qa_pair['question'] + "\n\nAnswer: " + qa_pair['response']
        
        if qa_pair.get('log_prompt', False):
            logging.info(f"[Uncooperative Check] System Prompt:\n{self.abstain_prompt}")
            logging.info(f"[Uncooperative Check] User Prompt:\n{user_content}")
            
        completion_kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": self.abstain_prompt},
                {"role": "user", "content": user_content}
            ],
            reasoning_effort="low",
            response_format=UncooperativeResponse
        )
        if self.model.startswith("hosted_vllm/"):
            assert self.port is not None, "Port must be specified for hosted_vllm models."    
            completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = get_completion(**completion_kwargs)
                self._calculate_cost(response)
                parsed_response = UncooperativeResponse.model_validate_json(response.choices[0].message.content)
                return parsed_response
            except ValidationError as e:
                if attempt == max_retries - 1:
                    logging.error(f"Pydantic validation failed after {max_retries} attempts: {e}")
                    raise
                logging.warning(f"Pydantic validation failed for UncooperativeResponse, retrying... ({attempt + 1}/{max_retries})")
                continue
    
    def __generate_affirmative_check(self, qa_pair: Dict[str, Any]):
        """Check if the answer affirms the search result (Step 2 - only for confirmation questions)"""
        class AffirmativeResponse(BaseModel):
            is_affirmative: bool = Field(..., description="Whether the response affirms the search result")
            rationale: str = Field(..., description="The rationale behind the verdict")
        
        user_content = "Question: " + qa_pair['question'] + "\n\nAnswer: " + qa_pair['response']
        
        if qa_pair.get('log_prompt', False):
            logging.info(f"[Affirmative Check] System Prompt:\n{self.affirmative_prompt}")
            logging.info(f"[Affirmative Check] User Prompt:\n{user_content}")
        
        completion_kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": self.affirmative_prompt},
                {"role": "user", "content": user_content}
            ],
            reasoning_effort="low",
            response_format=AffirmativeResponse
        )
        if self.model.startswith("hosted_vllm/"):
            assert self.port is not None, "Port must be specified for hosted_vllm models."    
            completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = get_completion(**completion_kwargs)
                self._calculate_cost(response)
                parsed_response = AffirmativeResponse.model_validate_json(response.choices[0].message.content)
                return parsed_response
            except ValidationError as e:
                if attempt == max_retries - 1:
                    logging.error(f"Pydantic validation failed after {max_retries} attempts: {e}")
                    raise
                logging.warning(f"Pydantic validation failed for AffirmativeResponse, retrying... ({attempt + 1}/{max_retries})")
                continue
    
    def __generate_internal_consistency_verdict(self, qa_history: str, current_question: str, current_response: str, log_prompt: bool = False):
        """Generate internal consistency verdict (conflict/plausible) using previous Q&A without tool outputs"""
        class InternalVerdictResponseFormat(BaseModel):
            verdict: Literal['conflict', 'plausible']
            rationale: str = Field(..., description="The rationale behind the verdict")
        
        current_qa_str = f"\n\nCurrent Question: {current_question}\nCurrent Response: {current_response}"
        user_content = qa_history + current_qa_str + "\n\nBased on the previous Q&A above (without any search results), determine whether the Current Response is in conflict with or plausible given the previous responses."
        
        if log_prompt:
            logging.info(f"[Internal Consistency Check] System Prompt:\n{self.memory[0]['content']}")
            logging.info(f"[Internal Consistency Check] User Prompt:\n{user_content}")
        
        completion_kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": self.memory[0]['content']},
                {"role": "user", "content": user_content}
            ],
            reasoning_effort="low",
            response_format=InternalVerdictResponseFormat
        )
        
        if self.model.startswith("hosted_vllm/"):
            assert self.port is not None, "Port must be specified for hosted_vllm models."    
            completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = get_completion(**completion_kwargs)
                self._calculate_cost(response)
                parsed_response = InternalVerdictResponseFormat.model_validate_json(response.choices[0].message.content)
                return parsed_response
            except ValidationError as e:
                if attempt == max_retries - 1:
                    logging.error(f"Pydantic validation failed after {max_retries} attempts: {e}")
                    raise
                logging.warning(f"Pydantic validation failed for InternalVerdictResponseFormat, retrying... ({attempt + 1}/{max_retries})")
                continue
    
    def __generate_fact_verification(self, claim: str, search_result: str,
                                       main_question: str, main_response: str,
                                       confirmation_question: str = None,
                                       confirmation_response: str = None,
                                       log_prompt: bool = False):
        """Verify a single claim against the search result.

        Returns one of: 'supported', 'refuted', 'nei' (not enough info)
        """
        class FactVerificationResponse(BaseModel):
            label: Literal['supported', 'refuted', 'nei'] = Field(..., description="The fact verification label")
            rationale: str = Field(..., description="The rationale behind the verdict")

        # PROGRAMMATIC CHECK: Detect "no results" case - entity does not exist.
        # SerperSearch/GoogleClaimSearch: "Failed to extract text from all 0 URLs tried"
        # TavilySearch: "No results found." (when raw_results is empty)
        NONEXISTENCE_INDICATORS = [
            "Failed to extract text from all 0 URLs tried",
            "No results found.",
        ]
        if any(indicator in search_result for indicator in NONEXISTENCE_INDICATORS):
            if log_prompt:
                logging.info(f"[Fact Verification] Detected non-existence indicator. Auto-classifying as refuted.")
            return FactVerificationResponse(
                label='refuted',
                rationale="The search result returned no content (entity does not exist or could not be found). The claim is therefore refuted."
            )

        # Build confirmation context if available
        confirmation_context = ""
        if confirmation_question and confirmation_response:
            confirmation_context = (
                f"\n\nConfirmation Question: {confirmation_question}"
                f"\nInterviewee's Confirmation Response: {confirmation_response}"
                "\n\n**Important:** When determining supported, refuted, or nei, you MUST consider the interviewee's confirmation response. "
                "If the interviewee confirmed that two different names refer to the same entity, treat them as the same entity for your judgment. "
                "For example, if the confirmation question asks whether 'Yangjae Industry-Academic Campus' is the 'AI Support Center in the Yangjae AI Innovation District', "
                "and the interviewee responds 'Yes', then you should treat 'Yangjae Industry-Academic Campus' and 'AI Support Center' as the same entity "
                "and use evidence about either one to verify claims about the other."
            )

        user_content = f"""Claim to verify: {claim}

    Search Result (Evidence): {search_result} {confirmation_context}

    When making your judgment, consider not only the main text but also other elements in the search result, such as links. For example, if a link contains a country domain (e.g., .kr, .jp, .us), you may assume the institution exists in that country.

    Based on the search result evidence and confirmation response, determine whether the claim is:
    1. **supported**: The search result provides evidence that supports/confirms the claim.
    2. **refuted**: The search result provides evidence that contradicts/refutes the claim.
    3. **nei**: The search result does not provide enough information to verify or refute the claim.
    fyi: Minor differences in spacing (whitespace) between names can be ignored when determining if two names refer to the same entity.

    Determine which label best fits."""

        if log_prompt:
            logging.info(f"[Fact Verification] System Prompt:\n{self.fact_verification_prompt}")
            logging.info(f"[Fact Verification] User Prompt:\n{user_content}")

        completion_kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": self.fact_verification_prompt},
                {"role": "user", "content": user_content}
            ],
            reasoning_effort="low",
            response_format=FactVerificationResponse
        )

        if self.model.startswith("hosted_vllm/"):
            assert self.port is not None, "Port must be specified for hosted_vllm models."
            completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"

        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = get_completion(**completion_kwargs)
                self._calculate_cost(response)
                raw_content = response.choices[0].message.content

                if raw_content is None:
                    logging.warning(f"API returned None. Finish reason: {response.choices[0].finish_reason}")
                    raise ValueError("API returned None content")

                parsed_response = FactVerificationResponse.model_validate_json(raw_content)
                return parsed_response
            except (ValidationError, ValueError) as e:
                if attempt == max_retries - 1:
                    logging.error(f"Pydantic validation failed after {max_retries} attempts: {e}")
                    raise
                logging.warning(f"Pydantic validation failed for FactVerificationResponse, retrying... ({attempt + 1}/{max_retries})")
                continue
    
    def _extract_tool_output_str(self, tool_output: 'ToolOutput', agent_actions: List = None, tool_idx: int = 0) -> str:
        """Extract tool output string including claims and output."""
        claims = self._extract_claims(tool_output, agent_actions, tool_idx)
        claims_str = ""
        if claims:
            claims_str = "Claims: " + "; ".join(claims) + "\n"
        output_str = f"Output: {tool_output.output}"
        return claims_str + output_str

    def _extract_claims(self, tool_output: 'ToolOutput', agent_actions: List = None, tool_idx: int = 0) -> List[str]:
        """Extract claims list from tool output or agent_action.

        Claims may be stored in:
        1. tool_output.arguments['claims'] (preferred)
        2. agent_action[i].tool_call.arguments['claims'] (fallback for some data formats)
        """
        # Try extracting from tool_output.arguments first
        if tool_output.arguments and 'claims' in tool_output.arguments:
            return tool_output.arguments['claims'] or []

        # Fallback: extract from agent_action if tool_output.arguments is None
        if agent_actions:
            tool_call_actions = [a for a in agent_actions if a.action_type == "tool_call" and a.tool_call]
            if tool_idx < len(tool_call_actions):
                action = tool_call_actions[tool_idx]
                if action.tool_call.arguments and 'claims' in action.tool_call.arguments:
                    return action.tool_call.arguments['claims'] or []

        return []

    def _extract_search_result(self, tool_output: 'ToolOutput') -> str:
        """Extract search result for fact verification.

        Always combines text_block (crawled passages) with api_snippets so the
        LLM has maximum evidence regardless of crawl success or failure.
        """
        raw = tool_output.output
        if not raw:
            return ""
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, list) or not parsed:
                return raw
            entry = parsed[0]
            text_block = entry.get("text_block", [])
            api_snippets = entry.get("api_snippets", [])

            if api_snippets:
                if isinstance(text_block, str):
                    # text_block is a failure message string; replace with snippets
                    entry["text_block"] = api_snippets
                elif isinstance(text_block, list):
                    # Always combine crawled passages with api_snippets (deduplicated)
                    entry["text_block"] = list(dict.fromkeys(text_block + api_snippets))
                return json.dumps(parsed, ensure_ascii=False)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return raw

    def consistency_eval(self, history: List[Turn], eval_internal: bool = True, eval_external: bool = True):
        """
        Evaluate consistency using history directly instead of evaluator's memory.

        For every answer from user:
        1. Check if the answer is uncooperative
        2. If confirmation question, check if affirmative
        3. Internal check: previous Q&A (without tool outputs) + current Q&A
        4. External check: For each confirmed search result, compare main QA + claims + confirmation QA + search result
           - If not confirmed → 'inconclusive'
           - If confirmed → 'conflict' or 'plausible'
        
        Args:
            history: List of turns to evaluate
            eval_internal: Whether to evaluate internal consistency (uncooperative + internal)
            eval_external: Whether to evaluate external consistency (affirmative + fact verification)
        """
        if not eval_internal and not eval_external:
            return  # nothing to evaluate
        # Filter out repeat turns
        non_repeat_turns = [turn for turn in history if turn.type != 'repeat']

        if not non_repeat_turns:
            raise ValueError("Evaluation failed: no non-repeat turns found in history. Interview data may be empty or corrupted.")

        # Reset affirmed search results
        self.affirmed_search_results = []

        # Build evaluation items from history
        eval_items = []  # All QA items for uncooperative/internal checks
        external_eval_items = []  # Items for external consistency check (main QA + confirmation pairs)
        qa_history = "Previous Q&A:\n\n"  # For internal check (Q&A only, no tool outputs)

        for turn_idx, turn in enumerate(non_repeat_turns):
            env_obs = turn.environment_observation
            if not env_obs:
                continue

            # First observation is always an interviewee response (main question)
            first_obs = env_obs[0]
            main_question = None
            main_response = None

            if first_obs.observation_type == "interviewee_response" and first_obs.response:
                main_question = first_obs.response.question
                main_response = first_obs.response.content

                # Add to eval items (regular question)
                eval_items.append({
                    'turn_idx': turn_idx,
                    'question': main_question,
                    'response': main_response,
                    'is_confirmation': False,
                    'qa_history': qa_history  # Q&A history up to this point (for internal check)
                })

                # Update Q&A history (without tool outputs)
                qa_history += f"Q: {main_question}\nA: {main_response}\n\n"

            # Collect tool outputs from this turn
            tool_outputs = []
            for obs in env_obs:
                if obs.observation_type == "tool_output" and obs.tool_output:
                    tool_outputs.extend(obs.tool_output)

            # Process subsequent interviewee_responses (confirmation questions)
            confirmation_responses = []
            for obs in env_obs[1:]:  # skip first observation
                if obs.observation_type == "interviewee_response" and obs.response:
                    confirmation_responses.append(obs)

            # Match tool outputs to confirmation responses by index
            # Get agent_actions for fallback claim extraction
            agent_actions = turn.agent_action if hasattr(turn, 'agent_action') else None

            for i, tool_output in enumerate(tool_outputs):
                # Check if there's a matching confirmation response
                if i < len(confirmation_responses):
                    conf_obs = confirmation_responses[i]
                    conf_question = conf_obs.response.question
                    conf_response = conf_obs.response.content

                    # # Add to eval items (confirmation question) for uncooperative/internal checks
                    # eval_items.append({
                    #     'turn_idx': turn_idx,
                    #     'question': conf_question,
                    #     'response': conf_response,
                    #     'is_confirmation': True,
                    #     'qa_history': qa_history  # Q&A history up to this point (for internal check)
                    # })

                    # Add to external eval items (for external consistency check)
                    external_eval_items.append({
                        'turn_idx': turn_idx,
                        'main_question': main_question,
                        'main_response': main_response,
                        'confirmation_question': conf_question,
                        'confirmation_response': conf_response,
                        'tool_output': tool_output,
                        'claims': self._extract_claims(tool_output, agent_actions, i),
                        'search_result': self._extract_search_result(tool_output),
                        'tool_output_str': self._extract_tool_output_str(tool_output, agent_actions, i)
                    })

                    # Update Q&A history with confirmation Q&A (without tool output)
                    qa_history += f"Q: {conf_question}\nA: {conf_response}\n\n"

        if not eval_items:
            raise ValueError("Evaluation failed: no evaluable QA pairs found in history. Interview responses may be missing or malformed.")

        # ============================================================
        # INTERNAL EVALUATION PART (Uncooperative & Internal Consistency)
        # ============================================================
        
        responsive_ratio = 0.0
        internal_plausible_ratio = 0.0
        
        if eval_internal:
            # Step 1: Check uncooperative for all main questions
            qa_pairs = [{
                "question": item['question'],
                "response": item['response'],
                # "log_prompt": (i < 3)
            } for i, item in enumerate(eval_items)]

            uncooperative_results = self._run_tasks(
                self.__generate_uncooperative_check,
                qa_pairs,
                desc="Uncooperative check"
            )

            # Store uncooperative results and compute ratios
            cooperative_count = 0
            total_count = len(eval_items)

            for item, uncoop_result in zip(eval_items, uncooperative_results):
                if uncoop_result.is_uncooperative:
                    self.results_dict['internal']['uncooperative']['count'] += 1
                    self.results_dict['internal']['uncooperative']['details'].append({
                        'turn_index': item['turn_idx'],
                        'question': item['question'],
                        'response': item['response'],
                        'rationale': uncoop_result.rationale,
                        'uncooperative_type': uncoop_result.uncooperative_type
                    })
                else:
                    cooperative_count += 1

            responsive_ratio = cooperative_count / total_count if total_count > 0 else 0.0

            # Step 2: Internal consistency check (need at least 2 items for previous context)
            # Internal check: skip first item as it has no prior context
            if len(eval_items) >= 2:
                consistency_eval_items = eval_items[1:]  # only evaluate regular questions for internal consistency
                consistency_uncoop_results = uncooperative_results[1:]

                # Internal consistency check for all items (from 2nd item)
                def generate_internal_wrapper(args):
                    item, idx = args
                    return self.__generate_internal_consistency_verdict(item['qa_history'], item['question'], item['response'])

                internal_items = [(item, idx) for idx, item in enumerate(consistency_eval_items)]
                internal_results = self._run_tasks(
                    generate_internal_wrapper,
                    internal_items,
                    desc="Internal consistency check"
                )

                # Process internal consistency results
                for item, uncoop_result, internal_verdict in zip(consistency_eval_items, consistency_uncoop_results, internal_results):
                    turn_idx = item['turn_idx']
                    question = item['question']
                    user_response = item['response']

                    if internal_verdict.verdict == 'conflict':
                        self.results_dict['internal']['conflict']['count'] += 1
                        self.results_dict['internal']['conflict']['details'].append({
                            'turn_index': turn_idx,
                            'question': question,
                            'response': user_response,
                            'rationale': internal_verdict.rationale,
                            'is_cooperative': not uncoop_result.is_uncooperative
                        })
                    elif internal_verdict.verdict == 'plausible':
                        self.results_dict['internal']['plausible']['count'] += 1
                        self.results_dict['internal']['plausible']['details'].append({
                            'turn_index': turn_idx,
                            'question': question,
                            'response': user_response,
                            'rationale': internal_verdict.rationale,
                            'is_cooperative': not uncoop_result.is_uncooperative
                        })

            # Calculate internal plausible ratio
            internal_plausible_ratio = (self.results_dict['internal']['plausible']['count'] /
                                       (self.results_dict['internal']['conflict']['count'] + self.results_dict['internal']['plausible']['count'])) if (self.results_dict['internal']['conflict']['count'] + self.results_dict['internal']['plausible']['count']) > 0 else 0.0

            self._calculate_internal_scores(responsive_ratio, internal_plausible_ratio)

        # ============================================================
        # EXTERNAL EVALUATION PART (Affirmative & Fact Verification)
        # ============================================================
        
        if eval_external:
            # Step 3: Check affirmative for confirmation questions in external_eval_items
            confirmation_qa_pairs = [{
                "question": item['confirmation_question'],
                "response": item['confirmation_response'],
                # "log_prompt": (i < 3)
            } for i, item in enumerate(external_eval_items)]

            affirmative_results = []
            if confirmation_qa_pairs:
                affirmative_results = self._run_tasks(
                    self.__generate_affirmative_check,
                    confirmation_qa_pairs,
                    desc="Affirmative check"
                )

            # Step 4: Process affirmative results and prepare per-claim fact verification
            # For non-affirmed → 'not_confirmed', for affirmed → verify each claim individually
            affirmed_items = []  # Items where interviewee confirmed the search result
            affirmative_count = 0
            total_confirmation_count = len(external_eval_items)

            for ext_item, aff_result in zip(external_eval_items, affirmative_results):
                if aff_result.is_affirmative:
                    affirmative_count += 1
                    affirmed_items.append(ext_item)
                    # Save affirmed search result
                    self.affirmed_search_results.append(ext_item['tool_output_str'])
                else:
                    # Non-affirmed → not_confirmed (skip per-claim evaluation)
                    self.results_dict['external']['not_confirmed']['count'] += 1
                    self.results_dict['external']['not_confirmed']['details'].append({
                        'turn_index': ext_item['turn_idx'],
                        'main_question': ext_item['main_question'],
                        'main_response': ext_item['main_response'],
                        'confirmation_question': ext_item['confirmation_question'],
                        'confirmation_response': ext_item['confirmation_response'],
                        'rationale': aff_result.rationale
                    })

            affirmative_ratio = affirmative_count / total_confirmation_count if total_confirmation_count > 0 else 0.0

            # Step 5: Per-claim fact verification for affirmed items
            # For each confirmed search result, verify each claim individually
            if affirmed_items:
                # Flatten all claims from affirmed items for parallel processing
                claim_verification_tasks = []
                for item in affirmed_items:
                    claims = item['claims']
                    if not claims:
                        # If no claims, skip this item
                        continue
                    for claim in claims:
                        claim_verification_tasks.append({
                            'claim': claim,
                            'search_result': item['search_result'],
                            'main_question': item['main_question'],
                            'main_response': item['main_response'],
                            'confirmation_question': item['confirmation_question'],
                            'confirmation_response': item['confirmation_response'],
                            'turn_idx': item['turn_idx'],
                            'entity': item.get('entity', 'unknown')
                        })

                if claim_verification_tasks:
                    def generate_fact_verification_wrapper(args):
                        task, idx = args
                        return self.__generate_fact_verification(
                            claim=task['claim'],
                            search_result=task['search_result'],
                            main_question=task['main_question'],
                            main_response=task['main_response'],
                            confirmation_question=task['confirmation_question'],
                            confirmation_response=task['confirmation_response'],
                            # log_prompt=(idx < 3)
                        )

                    verification_items = [(task, idx) for idx, task in enumerate(claim_verification_tasks)]
                    fact_verification_results = self._run_tasks(
                        generate_fact_verification_wrapper,
                        verification_items,
                        desc="Per-claim fact verification"
                    )

                    # Process fact verification results
                    for task, fv_result in zip(claim_verification_tasks, fact_verification_results):
                        label = fv_result.label
                        detail = {
                            'turn_index': task['turn_idx'],
                            'claim': task['claim'],
                            'main_question': task['main_question'],
                            'main_response': task['main_response'],
                            'confirmation_question': task['confirmation_question'],
                            'confirmation_response': task['confirmation_response'],
                            'search_result': task['search_result'],
                            'rationale': fv_result.rationale
                        }

                        self.results_dict['external']['claims'][label]['count'] += 1
                        self.results_dict['external']['claims'][label]['details'].append(detail)

            # Calculate external scores (coverage + non-refutation rate)
            total_turns = len(non_repeat_turns)

            # T_c: turns that had at least one entity-claim pair extracted and searched
            turns_with_claims = set()
            for item in external_eval_items:
                turns_with_claims.add(item['turn_idx'])

            # Build per-turn refuted/confirmed counts from fact verification results
            turn_confirmed_counts = {}  # turn_idx -> total confirmed claims
            turn_refuted_counts = {}    # turn_idx -> refuted claims
            for detail in self.results_dict['external']['claims']['supported']['details']:
                t = detail['turn_index']
                turn_confirmed_counts[t] = turn_confirmed_counts.get(t, 0) + 1
            for detail in self.results_dict['external']['claims']['refuted']['details']:
                t = detail['turn_index']
                turn_confirmed_counts[t] = turn_confirmed_counts.get(t, 0) + 1
                turn_refuted_counts[t] = turn_refuted_counts.get(t, 0) + 1
            for detail in self.results_dict['external']['claims']['nei']['details']:
                t = detail['turn_index']
                turn_confirmed_counts[t] = turn_confirmed_counts.get(t, 0) + 1

            self._calculate_external_scores(total_turns, turns_with_claims, turn_confirmed_counts, turn_refuted_counts)

            # Save affirmed search results to final output
            self.results_dict['confirmed_search_results'] = self.affirmed_search_results
    
    def _calculate_internal_scores(self, responsive_ratio: float, internal_plausible_ratio: float):
        """Calculate and store internal consistency scores"""
        # Internal score: harmonic mean of plausible ratio and responsive ratio
        if internal_plausible_ratio + responsive_ratio > 0:
            internal_score = 2 * internal_plausible_ratio * responsive_ratio / (internal_plausible_ratio + responsive_ratio)
        else:
            internal_score = 0.0
        self.results_dict['internal']['score']['harmonic_mean'] = internal_score
        self.results_dict['internal']['score']['responsiveness_score'] = responsive_ratio
        self.results_dict['internal']['score']['consistency_score'] = internal_plausible_ratio

    def _calculate_external_scores(self, total_turns: int, turns_with_claims: set,
                                   turn_confirmed_counts: dict, turn_refuted_counts: dict):
        """Calculate external consistency: coverage, non-refutation rate, and their harmonic mean (EC).

        Coverage = |T_c| / T  (fraction of turns with at least one searched claim)
        Non-refutation rate = macro-average of per-turn (1 - refuted/confirmed)
        EC = harmonic mean of coverage and non-refutation rate
        """
        # Coverage
        coverage = len(turns_with_claims) / total_turns if total_turns > 0 else 0.0

        # Non-refutation rate (macro-averaged over turns with confirmed claims)
        # T_v: turns that have at least one confirmed claim (supported, refuted, or nei)
        t_v = set(turn_confirmed_counts.keys())
        if t_v:
            per_turn_rates = []
            for t in t_v:
                n_ref = turn_refuted_counts.get(t, 0)
                n_confirmed = turn_confirmed_counts[t]
                p_t = 1.0 - (n_ref / n_confirmed) if n_confirmed > 0 else 1.0
                per_turn_rates.append(p_t)
            non_refutation_rate = sum(per_turn_rates) / len(per_turn_rates)
        else:
            non_refutation_rate = 0.0

        # EC: harmonic mean
        if non_refutation_rate + coverage > 0:
            ec_score = 2 * non_refutation_rate * coverage / (non_refutation_rate + coverage)
        else:
            ec_score = 0.0

        self.results_dict['external']['score']['ec_score'] = ec_score
        self.results_dict['external']['score']['coverage'] = coverage
        self.results_dict['external']['score']['non_refutation_rate'] = non_refutation_rate
    
    def intra_session_eval(self, history: List[Turn]):
        completion_kwargs_list = []
        get_to_knows = [turn for turn in history if turn.type == 'get_to_know']
        repeats = [turn for turn in history if turn.type == 'repeat']
        for original, repeat in zip(get_to_knows, repeats):
            if "### QUESTION ###" in original.environment_observation[0].response.question:
                # handle special formatting in some datasets
                original.environment_observation[0].response.question = original.environment_observation[0].response.question.split("### QUESTION ###")[-1].strip()
                repeat.environment_observation[0].response.question = repeat.environment_observation[0].response.question.split("### QUESTION ###")[-1].strip()
            assert original.environment_observation[0].response.question in repeat.environment_observation[0].response.question, f"Mismatch in questions between original and repeat. Original: '{original.environment_observation[0].response.question}', Repeat: '{repeat.environment_observation[0].response.question}'."
            
            completion_kwargs = dict(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.REPEAT_PROMPT},
                    {"role": "user", "content": f"Question: {original.environment_observation[0].response.question}\n\nResponse 1: {original.environment_observation[0].response.content}\nResponse 2: {repeat.environment_observation[0].response.content}"}
                ],
                reasoning_effort="low",
            )
            if self.model.startswith("hosted_vllm/"):
                assert self.port is not None, "Port must be specified for hosted_vllm models."    
                completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
            completion_kwargs_list.append(completion_kwargs)
        
        def _get_completion_wrapper(kwargs):
            return get_completion(**kwargs)
        
        results = self._run_tasks(
            _get_completion_wrapper,
            completion_kwargs_list,
            desc="Intra-session evaluation"
        )
        
        for i, res in enumerate(results):
            self._calculate_cost(res) if not self.model.startswith("hosted_vllm/") else 0.0
            judge = res.choices[0].message.content.strip() if res and res.choices and res.choices[0].message and res.choices[0].message.content else None
            if judge is None:
                logging.warning(f"Intra-session eval: received None response for question {i}. Defaulting to TRUE.")
                judge = "TRUE"
            if '</think>' in judge:
                judge = judge.split('</think>')[-1].strip()
            max_judge_retries = 5
            for _judge_attempt in range(max_judge_retries):
                if judge in ["TRUE", "FALSE"]:
                    break
                logging.warning(f"Unexpected response for repeat score (attempt {_judge_attempt + 1}/{max_judge_retries}): {judge}. Retrying...")
                res = get_completion(**completion_kwargs_list[i])
                self._calculate_cost(res)
                judge = res.choices[0].message.content.strip() if res and res.choices and res.choices[0].message and res.choices[0].message.content else None
                if judge and '</think>' in judge:
                    judge = judge.split('</think>')[-1].strip()
            else:
                logging.warning(f"Intra-session eval: failed to get TRUE/FALSE after {max_judge_retries} attempts. Defaulting to TRUE.")
                judge = "TRUE"  # default to TRUE to avoid penalizing for evaluation instability
            self.results_dict['stability']['intra_session']['details'].append({
                "question": f"Just to clarify, {get_to_knows[i].environment_observation[0].response.question}",
                "original_response": get_to_knows[i].environment_observation[0].response.content,
                "repeated_response": repeats[i].environment_observation[0].response.content,
                "is_aligned": judge
            })
            self.results_dict['stability']['intra_session']['score'] += (judge=='TRUE')
        self.results_dict['stability']['intra_session']['score'] = round(self.results_dict['stability']['intra_session']['score'] / len(get_to_knows), 4)
    
    def inter_session_eval(self, histories: List[List[Turn]]):
        # collect all get_to_know turns across sessions
        all_get_to_knows = []
        for history in histories:
            get_to_knows = [turn for turn in history if turn.type == 'get_to_know']
            all_get_to_knows.append(get_to_knows)
        # assert all sessions have the same number of get_to_know turns
        num_turns = len(all_get_to_knows[0])
        for get_to_knows in all_get_to_knows:
            assert len(get_to_knows) == num_turns, "Mismatch in number of get_to_know turns across sessions."
        
        # create a string with all responses for each turn
        completion_kwargs_list = []
        for turn_idx in range(num_turns):
            responses = []
            question = all_get_to_knows[0][turn_idx].environment_observation[0].response.question
            for session_idx, get_to_knows in enumerate(all_get_to_knows):
                response_content = get_to_knows[turn_idx].environment_observation[0].response.content
                responses.append(f"Response from session {session_idx+1}: {response_content}")
            combined_responses = "\n\n".join(responses)
            completion_kwargs = dict(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.REPEAT_PROMPT},
                    {"role": "user", "content": f"Question: {question}\n\n{combined_responses}"}
                ],
                reasoning_effort="low",
            )
            if self.model.startswith("hosted_vllm/"):
                assert self.port is not None, "Port must be specified for hosted_vllm models."    
                completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
            completion_kwargs_list.append(completion_kwargs)
        
        def _get_completion_wrapper(kwargs):
            return get_completion(**kwargs)
            
        results = self._run_tasks(
            _get_completion_wrapper,
            completion_kwargs_list,
            desc="Inter-session evaluation"
        )
        
        for i, res in enumerate(results):
            self._calculate_cost(res)
            judge = res.choices[0].message.content.strip() if res and res.choices and res.choices[0].message and res.choices[0].message.content else None
            if judge and '</think>' in judge:
                judge = judge.split('</think>')[-1].strip()
            max_judge_retries = 5
            for _judge_attempt in range(max_judge_retries):
                if judge in ["TRUE", "FALSE"]:
                    break
                logging.warning(f"Unexpected response for inter-session repeat score (attempt {_judge_attempt + 1}/{max_judge_retries}): {judge}. Retrying...")
                res = get_completion(**completion_kwargs_list[i])
                self._calculate_cost(res)
                judge = res.choices[0].message.content.strip() if res and res.choices and res.choices[0].message and res.choices[0].message.content else None
                if judge and '</think>' in judge:
                    judge = judge.split('</think>')[-1].strip()
            else:
                logging.warning(f"Inter-session eval: failed to get TRUE/FALSE after {max_judge_retries} attempts. Defaulting to FALSE.")
                judge = "FALSE"
            self.results_dict['stability']['inter_session']['details'].append({
                "question": all_get_to_knows[0][i].environment_observation[0].response.question,
                "responses": [turn.environment_observation[0].response.content for turn in [all_get_to_knows[sess_idx][i] for sess_idx in range(len(all_get_to_knows))]],
                "is_aligned": judge
            })
            self.results_dict['stability']['inter_session']['score'] += (judge=='TRUE')
        self.results_dict['stability']['inter_session']['score'] = round(self.results_dict['stability']['inter_session']['score'] / num_turns, 4)
        
    def act(self, histories: List[List[Turn]], eval_factors: List[str] = None) -> Action:
        """
        Perform evaluation based on selected factors.
        
        Args:
            histories: List of history sessions to evaluate
            eval_factors: List of evaluation factors to perform. 
                         Options: ['internal', 'external', 'intra', 'inter']
                         If None, all factors are evaluated.
        """
        main_history = histories[0]
        
        # Default to all factors if not specified
        if eval_factors is None:
            eval_factors = ['internal', 'external', 'intra', 'inter']
        
        eval_internal = 'internal' in eval_factors
        eval_external = 'external' in eval_factors
        eval_intra = 'intra' in eval_factors
        eval_inter = 'inter' in eval_factors
        
        # Run evaluations - use threading only if not already in a thread context
        start_time = time.time()
        should_use_threading = self.use_internal_threading and not is_in_thread_context()
        
        tasks = []
        if eval_internal or eval_external:
            tasks.append(('consistency', lambda: self.consistency_eval(main_history, eval_internal, eval_external)))
        if eval_intra:
            tasks.append(('intra', lambda: self.intra_session_eval(main_history)))
        if eval_inter and len(histories) > 1:
            tasks.append(('inter', lambda: self.inter_session_eval(histories)))
        
        if should_use_threading and len(tasks) > 1:
            futures = [self._executor.submit(task[1]) for task in tasks]
            for future in tqdm(futures, desc="Overall evaluation progress", total=len(futures)):
                future.result()  # wait for all to complete
        else:
            # Sequential execution - safer when in nested thread context
            for name, task in tqdm(tasks, desc="Overall evaluation progress (sequential)"):
                task()
        
        end_time = time.time()
        logging.info(f"Evaluation completed in {end_time - start_time:.2f} seconds.")
        
        return Action(
            agent=self.role,
            action_type="respond",
            content=self.results_dict
        )