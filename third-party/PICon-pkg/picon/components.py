"""
User-facing component classes for PICON.

Usage:
    from picon import Questioner, EntityExtractor, Evaluator, Interviewee
    from picon import InterrogationSimulation

    questioner = Questioner(model="gpt-5")
    extractor = EntityExtractor(model="gpt-5.1")
    evaluator = Evaluator(model="gemini/gemini-2.5-flash")

    interviewee = Interviewee(
        model="gpt-5",
        persona="You are a 35-year-old software engineer living in Seoul.",
        name="John",
    )

    sim = InterrogationSimulation(
        interviewee=interviewee,
        questioner=questioner,
        extractor=extractor,
        evaluator=evaluator,
        num_turns=20,
        num_sessions=2,
    )
    result = sim.run(do_eval=True)
"""

import os
import time
import logging
from typing import List, Optional

from dotenv import load_dotenv

from picon.agents.agent_factory import get_agent
from picon.config import DEFAULT_CONFIG, get_prompt_path, get_question_path
from picon.tools.web_search import SerperSearch
from picon.tools.address_locator import GoogleGeocodeValidate
from picon.env.interrogation_env import InterrogationEnv
from picon.utils import write_json


class Questioner:
    """Questioner agent that generates interview questions.

    Args:
        model: LLM model name. Default: ``"gpt-5"``.
        prompt_path: Custom system prompt file. ``None`` uses the built-in prompt.
    """

    def __init__(self, model: str = None, prompt_path: str = None):
        self.model = model or DEFAULT_CONFIG["questioner_model"]
        self.prompt_path = prompt_path or get_prompt_path("questioner.txt")
        self._agent = get_agent("questioner", self.prompt_path, model=self.model)

    @property
    def agent(self):
        return self._agent


class EntityExtractor:
    """Entity extractor agent that pulls verifiable claims from answers.

    Args:
        model: LLM model name. Default: ``"gpt-5.1"``.
        prompt_path: Custom system prompt file. ``None`` uses the built-in prompt.
    """

    def __init__(self, model: str = None, prompt_path: str = None):
        self.model = model or DEFAULT_CONFIG["extractor_model"]
        self.prompt_path = prompt_path or get_prompt_path("entity_extractor.txt")
        self._agent = get_agent("entity_extractor", self.prompt_path, model=self.model)

    @property
    def agent(self):
        return self._agent


class WebSearch:
    """Web search agent that fact-checks extracted claims against the web.

    Args:
        model: LLM model name. Default: ``"gpt-5"``.
        prompt_path: Custom system prompt file. ``None`` uses the built-in prompt.
    """

    def __init__(self, model: str = None, prompt_path: str = None):
        self.model = model or DEFAULT_CONFIG["web_search_model"]
        self.prompt_path = prompt_path or get_prompt_path("websearch_prompt.txt")
        self._agent = get_agent("web_search", self.prompt_path, model=self.model)

    @property
    def agent(self):
        return self._agent


class Evaluator:
    """Evaluator agent that scores consistency, accuracy, and stability.

    Args:
        model: LLM model name. Default: ``"gemini/gemini-2.5-flash"``.
        prompt_path: Custom system prompt file. ``None`` uses the built-in prompt.
    """

    def __init__(self, model: str = None, prompt_path: str = None):
        self.model = model or DEFAULT_CONFIG["evaluator_model"]
        self.prompt_path = prompt_path or get_prompt_path("evaluator_prompt.txt")
        self._agent = get_agent("evaluator", self.prompt_path, model=self.model)

    @property
    def agent(self):
        return self._agent


class Interviewee:
    """Persona agent being evaluated.

    Two modes:
      - **LLM persona**: provide ``model`` and ``persona``.
      - **External endpoint**: provide ``api_base`` (model is optional).

    Args:
        model: LLM model name (e.g. ``"gpt-5"``). Required if ``api_base`` is not set.
        persona: System prompt string or path to a ``.txt`` file. Default: ``""``.
        name: Interviewee display name. Default: ``"Agent"``.
        api_base: OpenAI-compatible endpoint URL. Required if ``model`` is not set.
        api_key: API key for the endpoint. Default: ``None``.
    """

    def __init__(
        self,
        model: str = None,
        persona: str = "",
        name: str = "Agent",
        api_base: str = None,
        api_key: str = None,
        **kwargs,
    ):
        if not model and not api_base:
            raise ValueError("Either 'model' or 'api_base' must be provided.")
        self.model = model
        self.persona = persona
        self.name = name
        self.api_base = api_base
        self.api_key = api_key
        self.extra_kwargs = kwargs

        # Read persona from file if path is given
        if self.persona and os.path.isfile(self.persona):
            with open(self.persona) as f:
                self.persona = f.read()


class InterrogationSimulation:
    """Orchestrates the full PICON interview and evaluation pipeline.

    Composes agent components (Questioner, EntityExtractor, WebSearch, Evaluator)
    with an Interviewee to run multi-turn interviews and evaluate persona consistency.

    Args:
        interviewee: The persona agent to evaluate.
        questioner: Questioner agent. ``None`` creates one with default settings.
        extractor: Entity extractor agent. ``None`` creates one with default settings.
        web_search: Web search agent. ``None`` creates one with default settings.
        evaluator: Evaluator agent. ``None`` creates one with default settings.
        num_turns: Number of interview turns per session. Default: ``30``.
        num_sessions: Number of repeated sessions. Default: ``2``.
        nhd_model: Model for AI detection. Default: ``"gpt-5-nano"``.
        output_dir: Output directory for results. Default: ``"data/results"``.
        question_seed: Random seed for question selection. Default: ``42``.
    """

    def __init__(
        self,
        interviewee: Interviewee,
        questioner: Questioner = None,
        extractor: EntityExtractor = None,
        web_search: WebSearch = None,
        evaluator: Evaluator = None,
        num_turns: int = 30,
        num_sessions: int = 2,
        nhd_model: str = None,
        output_dir: str = None,
        question_seed: int = 42,
    ):
        self.interviewee = interviewee
        self.questioner = questioner or Questioner()
        self.extractor = extractor or EntityExtractor()
        self.web_search = web_search or WebSearch()
        self.evaluator = evaluator or Evaluator()
        self.num_turns = num_turns
        self.num_sessions = num_sessions
        self.nhd_model = nhd_model or DEFAULT_CONFIG["nhd_model"]
        self.output_dir = output_dir or DEFAULT_CONFIG["output_dir"]
        self.question_seed = question_seed

    def run(self, do_eval: bool = True, eval_factors: List[str] = None) -> "PiconResult":
        """Run the interview pipeline and optionally evaluate.

        Args:
            do_eval: Run evaluation after interview. Default: ``True``.
            eval_factors: Evaluation factors to run (``"internal"``, ``"external"``,
                ``"intra"``, ``"inter"``). ``None`` runs all.

        Returns:
            A :class:`PiconResult` with scores and raw results.
        """
        from picon.api import PiconResult

        load_dotenv()

        agents = {
            "questioner": self.questioner.agent,
            "extractor": self.extractor.agent,
            "web_search": self.web_search.agent,
            "evaluator": self.evaluator.agent,
        }

        tools = {
            "serper_search": SerperSearch(api_key=os.getenv("SERPER_API_KEY")),
            "google_geocode_validate": GoogleGeocodeValidate(api_key=os.getenv("GOOGLE_GEOCODE")),
        }

        name = self.interviewee.name
        result_path = (
            f"{self.output_dir}/{name.replace(' ', '_')}"
            f"_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )
        os.makedirs(os.path.dirname(result_path) or ".", exist_ok=True)

        interviewee_kwargs = {
            "baseline_name": "generic_agent",
            "model": self.interviewee.model,
            "api_base": self.interviewee.api_base,
            "api_key": self.interviewee.api_key,
            "persona": self.interviewee.persona,
            "name": name,
            "nhd_model": self.nhd_model,
            "question_seed": self.question_seed,
            **self.interviewee.extra_kwargs,
        }

        picon_result = PiconResult()
        persona_stats = {
            "name": name,
            "ai_detected": False,
            "success": False,
            "total_cost": 0.0,
            "sessions_completed": 0,
        }

        try:
            env = InterrogationEnv(
                agents=agents,
                tools=tools,
                max_turns=self.num_turns,
                question_path=get_question_path(),
                **interviewee_kwargs,
            )

            results_complete = {}
            histories = []
            reset_only = False
            for session_idx in range(self.num_sessions):
                logging.info(f"Starting session {session_idx + 1}/{self.num_sessions} for: {name}")
                env.reset(reset_only=reset_only)
                if not reset_only:
                    done = False
                    while not done:
                        state, done = env.step()
                    state = env.finalize()
                session_result = env.save_state()
                histories.append(env.state.history)
                results_complete[f"session_{session_idx + 1}"] = session_result
                persona_stats["sessions_completed"] += 1
                reset_only = True

            results_complete["agents_memory"] = {
                n: agent.memory for n, agent in env.agents.items()
            }
            write_json(results_complete, result_path)

            persona_stats["success"] = True
            for session_key in [k for k in results_complete if k.startswith("session_")]:
                cost_data = results_complete[session_key].get("cost", {})
                persona_stats["total_cost"] += cost_data.get("total_cost", 0.0)

            # Evaluation
            eval_scores = {}
            if do_eval:
                logging.info(f"Running evaluation for {name}...")
                eval_result = env.evaluate(histories, eval_factors=eval_factors)
                results_complete["evaluation"] = eval_result
                write_json(results_complete, result_path)

                if eval_result:
                    internal = eval_result.get("internal", {}).get("score", {})
                    external = eval_result.get("external", {}).get("score", {})
                    stability = eval_result.get("stability", {})
                    eval_scores = {
                        "internal_harmonic_mean": internal.get("harmonic_mean"),
                        "internal_responsiveness": internal.get("responsiveness_score"),
                        "internal_consistency": internal.get("consistency_score"),
                        "external_ec": external.get("ec_score"),
                        "external_coverage": external.get("coverage"),
                        "external_non_refutation_rate": external.get("non_refutation_rate"),
                        "inter_session_stability": stability.get("inter_session", {}).get("score"),
                        "intra_session_stability": stability.get("intra_session", {}).get("score"),
                    }

            env.shutdown()

            picon_result.success = True
            picon_result.summary = persona_stats
            picon_result.eval_scores = eval_scores
            picon_result.raw_results = results_complete
            picon_result.result_path = result_path
            return picon_result

        except Exception as e:
            if "env" in locals():
                env.shutdown()
            raise
