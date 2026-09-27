"""
Wrapping server template — wrap any persona agent as an OpenAI-compatible endpoint.

This server bakes in all agent config (model, persona, name, etc.) so that
PICON only needs the endpoint URL — no other arguments required.

Example — OpenCharacter (LoRA on Llama-3-8B):

    # 1) Start vLLM with LoRA adapter on GPU 0,1
    CUDA_VISIBLE_DEVICES=0,1 vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
        --enable-lora \
        --lora-modules willystumblr/opencharacter-sft-2025-06-21_14-54-13 \
        --tensor-parallel-size 1 \
        --served-model-name opencharacter-llama-3-8b-sft \
        --port 8000

    # 2) Start wrapping server (persona baked in)
    python servers/template_server.py \
        --port 8001 \
        --vllm_base http://localhost:8000/v1 \
        --vllm_model opencharacter-llama-3-8b-sft \
        --persona "You are a kind-hearted librarian named Alice..." \
        --name "Alice"

    # 3) PICON — only the URL is needed
    picon --agent_api_base http://localhost:8001/v1 --do_eval

    # or Python
    import picon
    result = picon.run(api_base="http://localhost:8001/v1")

Notes:
    - PICON sends conversation history in `messages`, but this server replaces
      the system prompt with the baked-in persona and forwards to vLLM.
    - To wrap something other than vLLM (RAG, external API, etc.),
      replace the generate_response() function with your own logic.
"""
import time
import argparse
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Populated by CLI args at startup
client: OpenAI = None
vllm_model: str = ""
persona: str = ""
agent_name: str = ""


def generate_response(messages: list) -> str:
    """
    Forward request to vLLM with the baked-in persona as system prompt.

    The incoming messages from PICON may have an empty or placeholder system
    prompt. This server replaces it with the real persona before forwarding.
    """
    # Replace/inject system prompt with baked-in persona
    if messages and messages[0]["role"] == "system":
        messages = [{"role": "system", "content": persona}] + messages[1:]
    else:
        messages = [{"role": "system", "content": persona}] + messages

    response = client.chat.completions.create(
        model=vllm_model,
        messages=messages,
    )
    return response.choices[0].message.content.strip()


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    try:
        content = generate_response(messages)
    except Exception as e:
        logging.error(f"Agent error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": agent_name,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapping server for PICON evaluation")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--vllm_base", type=str, required=True,
                        help="vLLM endpoint URL (e.g. http://localhost:8000/v1)")
    parser.add_argument("--vllm_model", type=str, required=True,
                        help="Model name served by vLLM")
    parser.add_argument("--persona", type=str, required=True,
                        help="System prompt / persona description (string or path to .txt file)")
    parser.add_argument("--name", type=str, default="Agent",
                        help="Agent name (used in response metadata)")
    args = parser.parse_args()

    # Load persona from file if path is given
    import os
    if os.path.isfile(args.persona):
        with open(args.persona) as f:
            persona = f.read()
    else:
        persona = args.persona

    agent_name = args.name
    vllm_model = args.vllm_model
    client = OpenAI(base_url=args.vllm_base, api_key="no-key")

    logging.info(f"Agent: {agent_name}")
    logging.info(f"vLLM: {args.vllm_base} / {vllm_model}")
    logging.info(f"PICON endpoint: http://localhost:{args.port}/v1")
    uvicorn.run(app, host=args.host, port=args.port)
