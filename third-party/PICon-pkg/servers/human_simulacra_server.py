"""
HumanSimulacra wrapping server — exposes Top_agent as an OpenAI-compatible endpoint.

Usage:
    python servers/human_simulacra_server.py --port 8002 --character_name "Mary Jones" --model gemini/gemini-2.5-flash
"""
import argparse
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from picon.env.personas.human_simulacra.hs_agents import Top_agent

logging.basicConfig(level=logging.INFO)
app = FastAPI()

agent = None


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    user_message = messages[-1].get("content", "")

    try:
        content = agent.send_message(user_message)
    except Exception as e:
        logging.error(f"HumanSimulacra error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {
        "id": f"chatcmpl-hs-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "human_simulacra",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@app.get("/v1/cost")
async def get_cost():
    """Retrieve accumulated cost from the agent."""
    return {"cost": agent.calculate_cost() if agent else 0.0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--character_name", type=str, required=True)
    parser.add_argument("--model", type=str, default="gemini/gemini-2.5-flash")
    args = parser.parse_args()

    logging.info(f"Loading HumanSimulacra agent: {args.character_name}")
    agent = Top_agent(character_name=args.character_name, model=args.model)
    logging.info(f"Agent loaded. Starting server on port {args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)
