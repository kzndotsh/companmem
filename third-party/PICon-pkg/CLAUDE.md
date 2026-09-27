# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PICON (Persona Interview & Consistency Evaluation) is a framework for automatically interviewing and evaluating LLM-based personas across three dimensions: internal consistency, external verifiability, and stability over time.

## Build & Install

```bash
pip install -e .            # Development install
pip install -e ".[all]"     # Full install (Character.AI, Google GenAI, GitHub, Redis)
```

## Running

```bash
# CLI entry point (all equivalent)
picon --agent_model gpt-5 --agent_name "John" --agent_persona "You are..."
python -m picon --agent_model gpt-5 --agent_name "John" --agent_persona "You are..."
python main.py --agent_model gpt-5 --agent_name "John" --agent_persona "You are..."

# Key flags
--num_turns 30              # Interview turns per session
--num_sessions 2            # Repeated sessions for stability
--do_eval                   # Run evaluation after interview
--eval_factors internal external intra inter
--questioner_model          # Model for questioning agent
--evaluator_model           # Model for evaluation agent
--agent_api_base             # OpenAI-compatible endpoint URL
--agent_api_key              # API key for the endpoint
--output_dir                # Results directory
```

## Testing

No pytest suite exists. Agent-level testing is done via test environments in `picon/env/test_env/` (e.g., `questioner_test_env.py`, `evaluator_test_env.py`). Batch integration tests run through shell scripts in `scripts/`.

## Architecture

### Public API (`picon/api.py`)
High-level functions exported from `picon/__init__.py`:
- `run()` — interview + evaluation in one call
- `run_interview()` / `run_evaluation()` — separate steps
- `PiconResult` dataclass — result container with `save()` method

### Interview Pipeline (`picon/env/interrogation_env.py`)
`InterrogationEnv` orchestrates the full pipeline:
1. **Reset** — feed instruction, run demographic questions (from WVS)
2. **Main loop** — Questioner → Interviewee → Extractor → Web Search
3. **Repeat phase** — re-ask demographic questions for stability measurement
4. **Finalize** — aggregate stats and scores

### Agents (`picon/agents/`)
Factory pattern via `get_agent(agent_type, system_message_path, **kwargs)`. Agent types: `questioner`, `entity_extractor`, `claim_extractor`, `web_search`, `kg_agent`, `evaluator`. All extend `Agent` ABC from `base_agent.py`.

The **evaluator** (`evaluator.py`, largest module) handles all three evaluation dimensions with `ThreadPoolExecutor` for parallel claim verification.

### Interviewee Simulators (`picon/env/interviewee_simulator/`)
All persona types (cloud APIs, vLLM, wrapping servers) route through `GenericAgentSimulator` via the simulator factory. Wrapping servers in `servers/` expose external persona sources (Character.AI, HumanSimulacra RAG) as OpenAI-compatible endpoints.

### Tools (`picon/tools/`)
Web search tools (Serper, Google Claim Search, Tavily) with HTML→Markdown extraction and BM25 ranking. Address validation via Google Geocoding.

### LLM Calls
All LLM completions go through `picon/utils.py:get_completion()` which wraps `litellm`. Cost tracking is done per-agent via `litellm.cost_calculator`.

## Environment Variables

Required API keys (see `.env.example`):
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` — LLM providers
- `SERPER_API_KEY` — web search (for external verification)
- `GOOGLE_CLAIM_SEARCH`, `GOOGLE_CX_ID` — Google fact-check search
- `GOOGLE_GEOCODE` — address validation

## Data & Prompts

- Agent system prompts: `picon/agents/prompts/*.txt`
- Demographic questions: `picon/env/wvs_orthogonal_questions.json`
- Persona data: `picon/env/personas/` (human_simulacra characters, persona_hub)
- Results output: `data/results/` organized by persona type, `data/evaluation/` by model/type
