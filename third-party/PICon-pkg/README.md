# PICON — Persona Interrogation framework for Consistency evaluation

---
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/picon)
![PyPI Version](https://img.shields.io/pypi/v/picon)
---

An official Python package for evaluating LLM-based persona agents, called `PICON`.
By running a multi-turn interview and fact-checking pipeline, you can measure how consistently and accurately a persona agent behaves.
PICON evaluates persona agents across three dimensions:
* **Internal Consistency**: freedom from self-contradiction across answers.
* **External Consistency**: alignment of claims with real-world facts (via web search).
* **Retest Stability**: consistency of answers when the same questions are repeated within and across sessions.

&nbsp;

### Recent updates
* *March 2026 (v0.1.0)*: Initial release with interview pipeline, evaluation, and CLI.

&nbsp;

&nbsp;

## Installation

```bash
pip install picon-eval
```
```python
import picon
print(picon.__version__)
```

For development or full extras (CharacterAI, Google GenAI, etc.):
```bash
git clone https://github.com/willystumblr/picon.git
cd picon
pip install -e ".[all]"
```

&nbsp;

&nbsp;

## Quick Starts

> [!NOTE]
> Before using PICON, you must provide API keys either directly or in a `.env` file.
> * *OpenAI models (gpt-\*)*: Set `OPENAI_API_KEY` in your `.env` file.
> * *Gemini models (gemini/\*)*: Set `GEMINI_API_KEY` in your `.env` file.
> * *Web search (external verification)*: Set `SERPER_API_KEY` in your `.env` file. Get one at [serper.dev](https://serper.dev).

&nbsp;

### Environment Variables

Create a `.env` file in your working directory:

```bash
# LLM API Keys (at least one required)
OPENAI_API_KEY="YOUR_OPENAI_KEY"
GEMINI_API_KEY="YOUR_GEMINI_KEY"

# Web Search (required for external verification)
SERPER_API_KEY="YOUR_SERPER_KEY"

# Address validation (required for external verification)
GOOGLE_GEOCODE="YOUR_GOOGLE_GEOCODE_KEY"

# Optional
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
GOOGLE_CLAIM_SEARCH="YOUR_GOOGLE_API_KEY"       # Fact-check search
GOOGLE_CX_ID="YOUR_CUSTOM_SEARCH_ENGINE_ID"     # Custom Search Engine ID
```

&nbsp;

### Component-Based Usage

Import individual components and compose your own simulation pipeline:

```python
from picon import Questioner, EntityExtractor, Evaluator, Interviewee
from picon import InterrogationSimulation

# Set up agents
questioner = Questioner(model="gpt-5")
extractor = EntityExtractor(model="gpt-5.1")
evaluator = Evaluator(model="gemini/gemini-2.5-flash")

# Set up the persona to evaluate
interviewee = Interviewee(
    model="gpt-5",
    persona="You are a 35-year-old software engineer living in Seoul.",
    name="John",
)

# Run the full interview + evaluation pipeline
sim = InterrogationSimulation(
    interviewee=interviewee,
    questioner=questioner,
    extractor=extractor,
    evaluator=evaluator,
    num_turns=20,
    num_sessions=2,
)
result = sim.run(do_eval=True)

print(result.eval_scores)
result.save("results/john.json")

# Example output:
# {
#     "internal_harmonic_mean": 0.82,
#     "external_ec": 0.75,
#     "inter_session_stability": 0.68,
#     "intra_session_stability": 0.91,
# }
```

With default agent models, you can omit agent setup entirely:

```python
from picon import Interviewee, InterrogationSimulation

interviewee = Interviewee(model="gpt-5", persona="You are ...", name="John")
result = InterrogationSimulation(interviewee=interviewee, num_turns=20).run()
```

&nbsp;

### Evaluate an LLM Persona (Simple API)

For quick evaluations, use the `picon.run()` shortcut:

```python
import picon

result = picon.run(
    model="gpt-5",
    persona="You are a 35-year-old software engineer living in Seoul.",
    name="John",
    num_turns=20,
    num_sessions=2,
    do_eval=True,
)

print(result.eval_scores)
result.save("results/john.json")
```

```bash
# Equivalent CLI command
picon --agent_model gpt-5 \
      --agent_persona "You are a 35-year-old software engineer living in Seoul." \
      --agent_name "John" \
      --num_turns 20 --num_sessions 2 --do_eval
```

&nbsp;

### Evaluate an External Agent Endpoint

If you already have a persona agent running (e.g. a wrapping server, fine-tuned model, RAG agent), provide its OpenAI-compatible endpoint URL (`/v1/chat/completions`).

```python
from picon import Interviewee, InterrogationSimulation

interviewee = Interviewee(api_base="http://localhost:8000/v1", name="MyAgent")
result = InterrogationSimulation(interviewee=interviewee, num_turns=20).run()
```

```bash
# Equivalent CLI command
picon --agent_api_base http://localhost:8000/v1 \
      --agent_name "MyAgent" \
      --num_turns 20 --num_sessions 2 --do_eval
```

&nbsp;

### Self-hosted Models (vLLM)

For self-hosted models, provide both `api_base` and `model`:

```python
from picon import Interviewee, InterrogationSimulation

interviewee = Interviewee(
    api_base="http://localhost:8000/v1",
    model="meta-llama/Llama-3-8B",
    persona="You are a 30-year-old teacher named Jane...",
    name="Jane",
)
result = InterrogationSimulation(interviewee=interviewee).run()
```

```bash
picon --agent_api_base http://localhost:8000/v1 \
      --agent_model meta-llama/Llama-3-8B \
      --agent_persona "You are a 30-year-old teacher named Jane..." \
      --agent_name "Jane" --do_eval
```

&nbsp;

### Separate Interview and Evaluation

```python
import picon

# Step 1: Interview only
interview_result = picon.run_interview(
    name="John",
    model="gpt-5",
    persona="You are a 35-year-old software engineer...",
    num_turns=20,
    num_sessions=2,
)

# Step 2: Evaluate
persona_stats = picon.run_evaluation(interview_result, eval_factors=["internal", "external"])
print(persona_stats)
```

### Evaluate an Existing Result File

```python
scores = picon.evaluate("results/john.json", eval_factors=["internal", "external"])
```

&nbsp;

&nbsp;

## Building a Custom API Endpoint

If your persona agent uses custom logic (RAG, fine-tuned model, external API, etc.), you can wrap it as an **OpenAI-compatible endpoint** and evaluate it with PICON.
Your server only needs to implement one endpoint: `POST /v1/chat/completions`.

&nbsp;

### Endpoint Specification

**Request** — PICON sends a JSON body with a `messages` list:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Hello, tell me about yourself."},
    {"role": "assistant", "content": "I'm Alice, a librarian from Portland..."},
    {"role": "user", "content": "What books do you enjoy?"}
  ]
}
```

**Response** — Your server must return an OpenAI-compatible JSON:

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "my-agent",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "I love classic literature..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
}
```

&nbsp;

### Minimal Example

A minimal custom endpoint using FastAPI:

```python
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

def generate_response(messages: list) -> str:
    """Replace this with your own agent logic (RAG, API call, etc.)."""
    user_message = messages[-1]["content"]
    # ... your custom logic here ...
    return "This is my response."

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    content = generate_response(messages)

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "my-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

Start the server, then point PICON at it:

```python
import picon

result = picon.run(
    api_base="http://localhost:8001/v1",
    name="MyAgent",
    num_turns=20,
    do_eval=True,
)
```

```bash
picon --agent_api_base http://localhost:8001/v1 \
      --agent_name "MyAgent" \
      --num_turns 20 --do_eval
```

&nbsp;

### Using the Built-in Template Server

For agents backed by a vLLM or other OpenAI-compatible LLM service, the included [`servers/template_server.py`](servers/template_server.py) handles persona injection automatically:

```bash
# 1) Start your LLM backend (e.g. vLLM)
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
    --served-model-name my-model --port 8000

# 2) Start the wrapping server (persona is baked in)
python servers/template_server.py \
    --port 8001 \
    --vllm_base http://localhost:8000/v1 \
    --vllm_model my-model \
    --persona "You are Alice, a 32-year-old librarian from Portland..." \
    --name "Alice"

# 3) Evaluate with PICON
picon --agent_api_base http://localhost:8001/v1 --agent_name "Alice" --do_eval
```

The template server replaces the system prompt in incoming requests with the baked-in persona, so PICON only needs the endpoint URL. The `--persona` flag accepts either a string or a path to a `.txt` file.

See [`examples/`](examples/) for full end-to-end scripts using the template server with vLLM + LoRA and HumanSimulacra RAG.

&nbsp;

&nbsp;

## How It Works

```
1. Get-to-Know        Ask predefined demographic questions (WVS dataset)
       |
2. Main Interrogation Each turn runs this agent chain:
       |
       |-- Questioner    Generate the next question based on conversation history
       |-- Interviewee   The persona under evaluation answers the question
       |-- Extractor     Pull out entities and verifiable claims from the answer
       |-- Web Search    Fact-check extracted claims against the web
       '-- Evaluator     Compare this answer with previous answers for consistency
       |
3. Repeat Phase        Re-ask the get-to-know questions to measure stability
       |
4. Finalize            Compute all evaluation scores and save results
```

&nbsp;

&nbsp;

## API Reference

### Component Classes

> `Interviewee(model, persona, name, api_base, api_key)`:
> * `model` (str): LLM model name. Required if `api_base` is not provided.
> * `persona` (str): System prompt or path to a `.txt` file. Default: `""`.
> * `name` (str): Interviewee display name. Default: `"Agent"`.
> * `api_base` (str): OpenAI-compatible endpoint URL. Required if `model` is not provided.
> * `api_key` (str): API key for the endpoint. Default: `None`.

> `Questioner(model, prompt_path)` / `EntityExtractor(model, prompt_path)` / `Evaluator(model, prompt_path)` / `WebSearch(model, prompt_path)`:
> * `model` (str): LLM model name. Each agent has its own default (see below).
> * `prompt_path` (str): Custom system prompt file. `None` uses the built-in prompt.

> `InterrogationSimulation(interviewee, questioner, extractor, web_search, evaluator, ...)`:
> * `interviewee` (Interviewee): The persona agent to evaluate. **Required.**
> * `questioner` (Questioner): Questioner agent. `None` creates one with default model.
> * `extractor` (EntityExtractor): Extractor agent. `None` creates one with default model.
> * `web_search` (WebSearch): Web search agent. `None` creates one with default model.
> * `evaluator` (Evaluator): Evaluator agent. `None` creates one with default model.
> * `num_turns` (int): Interview turns per session. Default: `30`.
> * `num_sessions` (int): Number of repeated sessions. Default: `2`.
> * `nhd_model` (str): Model for AI detection. Default: `"gpt-5-nano"`.
> * `output_dir` (str): Output directory. Default: `"data/results"`.
> * `question_seed` (int): Random seed for question selection. Default: `42`.

&nbsp;

### Simple API

> `picon.run()` / `picon.run_interview()` Parameters:
> * `name` (str): Interviewee name. Default: `"Agent"`.
> * `model` (str): LLM model name (e.g. `"gpt-5"`, `"gemini/gemini-2.5-flash"`). Required if `api_base` is not provided.
> * `persona` (str): System prompt or path to a `.txt` file. Default: `""`.
> * `api_base` (str): OpenAI-compatible API endpoint URL. Required if `model` is not provided.
> * `api_key` (str): API key for the persona endpoint. Default: `None`.
> * `num_turns` (int): Number of interview turns. Default: `30`.
> * `num_sessions` (int): Number of repeated sessions. Default: `2`.
> * `do_eval` (bool): Run evaluation after interview. Default: `True`.
> * `eval_factors` (list): Evaluation factors to run: `"internal"`, `"external"`, `"intra"`, `"inter"`. Default: `None` (all).
> * `questioner_model` (str): Model for the questioner agent. Default: `"gpt-5"`.
> * `extractor_model` (str): Model for the entity extractor agent. Default: `"gpt-5.1"`.
> * `web_search_model` (str): Model for the web search agent. Default: `"gpt-5"`.
> * `evaluator_model` (str): Model for the evaluator agent. Default: `"gemini/gemini-2.5-flash"`.
> * `nhd_model` (str): Model for AI detection. Default: `"gpt-5-nano"`.
> * `output_dir` (str): Output directory for results. Default: `"data/results"`.
> * `question_seed` (int): Random seed for question selection. Default: `42`.

&nbsp;

&nbsp;

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Internal Responsiveness** | Relevance of answers to questions |
| **Internal Consistency** | Consistency of answers to repeated questions |
| **Internal Harmonic Mean** | Harmonic mean of Responsiveness and Consistency |
| **External Coverage** | Fraction of turns containing at least one verifiable claim |
| **External Non-refutation Rate** | Per-turn rate of claims not refuted by web evidence |
| **External Consistency (EC)** | Harmonic mean of Coverage and Non-refutation Rate |
| **Inter-session Stability** | Answer stability across sessions |
| **Intra-session Stability** | Answer stability within a session |

&nbsp;

&nbsp;

## Examples

End-to-end scripts in [`examples/`](examples/):

```bash
# OpenCharacter (vLLM + LoRA)
python examples/test_opencharacter_vllm.py

# HumanSimulacra (RAG agent)
python examples/test_human_simulacra.py
python examples/test_human_simulacra.py --character "Kevin Kelly" --model "gpt-5"
```

&nbsp;

&nbsp;

## Citation

If you use PICON in your research, please cite:

```bibtex
@article{kim2026picon,
  title={PICON: A Multi-Turn Interrogation Framework for Evaluating Persona Agent Consistency},
  author={Kim, Minseo and Im, Sujeong and Choi, Junseong and Lee, Junhee and Shim, Chaeeun and Choi, Edward},
  journal={arXiv preprint arXiv:2603.25620},
  year={2026}
}
```

&nbsp;
