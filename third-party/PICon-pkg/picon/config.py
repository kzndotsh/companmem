"""PICON default configuration and resource path helpers."""

from importlib import resources
import os

# ---------------------------------------------------------------------------
# Resource path helpers (work both in dev and installed mode)
# ---------------------------------------------------------------------------

def get_prompt_path(name: str) -> str:
    """Return the absolute path of a prompt file bundled with picon."""
    return str(resources.files("picon.agents.prompts").joinpath(name))


def get_question_path() -> str:
    """Return the absolute path of the default question bank."""
    return str(resources.files("picon.env").joinpath("wvs_orthogonal_questions.json"))


# ---------------------------------------------------------------------------
# Default settings
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "questioner_model": "gpt-5",
    "extractor_model": "gpt-5.1",
    "web_search_model": "gpt-5",
    "evaluator_model": "gemini/gemini-2.5-flash",
    "nhd_model": "gpt-5-nano",
    "num_turns": 30,
    "num_sessions": 2,
    "output_dir": "data/results",
}
