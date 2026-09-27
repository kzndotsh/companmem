"""
ConsistentLLM wrapping server — exposes ConsistentLLM's custom history logic
as an OpenAI-compatible endpoint.

Usage:
    python servers/consistent_llm_server.py \
        --port 8003 \
        --model_path /path/to/model \
        --simulator_model hosted_vllm/model-name \
        --vllm_port 8000 \
        --persona "You are ..." \
        --name "John" \
        --counterpart_name "Interviewer" \
        --instruction "Answer in character."
"""
import argparse
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from transformers import AutoTokenizer

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from picon.utils import get_completion

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# State
tokenizer = None
history = []  # plain text history: ["Interviewer: ...", "Name: ..."]
persona = ""
instruction = ""
name = ""
prompt_flag = "Your conversation so far is below:\nConversation: \n"
simulator_model = ""
vllm_host = "localhost"
vllm_port = 8000
max_position = 8192


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    user_message = messages[-1].get("content", "")
    history.append(f"Interviewer: {user_message}")

    # Build messages with custom history format (ConsistentLLM pattern)
    while True:
        user_content = prompt_flag + '\n'.join(history) + instruction
        llm_messages = [
            {"role": "system", "content": persona},
            {"role": "user", "content": user_content},
        ]
        input_ids = tokenizer.apply_chat_template(
            llm_messages,
            tokenize=True,
            return_tensors="pt",
            add_generation_prompt=True,
        )
        if input_ids.shape[1] + 1024 <= max_position:
            break
        # Drop oldest messages
        if len(history) > 2:
            history.pop(0)
            history.pop(0)
        else:
            break

    try:
        res = get_completion(
            model=simulator_model,
            messages=llm_messages,
            reasoning_effort="low",
            api_base=f"http://{vllm_host}:{vllm_port}/v1",
            max_tokens=1024,
        )
        content = res.choices[0].message.content.strip()
        history.append(f"{name}: {content}")
    except Exception as e:
        logging.error(f"ConsistentLLM error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {
        "id": f"chatcmpl-cllm-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "consistent_llm",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument("--model_path", type=str, required=True, help="HuggingFace model path for tokenizer")
    parser.add_argument("--simulator_model", type=str, required=True, help="Model name for vLLM (e.g. hosted_vllm/...)")
    parser.add_argument("--vllm_host", type=str, default="localhost")
    parser.add_argument("--vllm_port", type=int, required=True, help="Port where vLLM is running")
    parser.add_argument("--persona", type=str, required=True)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--counterpart_name", type=str, default="Interviewer")
    parser.add_argument("--instruction", type=str, required=True)
    args = parser.parse_args()

    logging.info(f"Loading tokenizer from {args.model_path}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    persona = args.persona
    instruction = args.instruction
    name = args.name
    simulator_model = args.simulator_model
    vllm_host = args.vllm_host
    vllm_port = args.vllm_port

    logging.info(f"ConsistentLLM server starting on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
