"""
CharacterAI wrapping server — exposes Character.AI as an OpenAI-compatible endpoint.

Usage:
    python servers/characterai_server.py --port 8001 --character_id <id> --user_id <id>
"""
import argparse
import asyncio
import logging
import time
import threading

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

logging.basicConfig(level=logging.INFO)
app = FastAPI()

CAI_TIMEOUT = 30
client = None
chat_id = None
_loop = None


async def setup_client(user_id: str, character_id: str):
    global client, chat_id
    client = await asyncio.wait_for(get_client(user_id), timeout=CAI_TIMEOUT)
    _, (chat, _) = await asyncio.wait_for(
        asyncio.gather(
            client.account.fetch_me(),
            client.chat.create_chat(character_id),
        ),
        timeout=CAI_TIMEOUT,
    )
    chat_id = chat.chat_id
    logging.info(f"CharacterAI session established. chat_id={chat_id}")


def run_on_loop(coro, timeout=CAI_TIMEOUT):
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=timeout)


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    user_message = messages[-1].get("content", "")

    async def _send():
        return await asyncio.wait_for(
            client.chat.send_message(
                character_id=args.character_id,
                chat_id=chat_id,
                text=user_message,
            ),
            timeout=CAI_TIMEOUT,
        )

    try:
        time.sleep(0.5)
        response = run_on_loop(_send(), timeout=CAI_TIMEOUT + 5)
        content = response.get_primary_candidate().text
    except Exception as e:
        logging.error(f"CharacterAI error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {
        "id": f"chatcmpl-cai-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "characterai",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--character_id", type=str, required=True)
    parser.add_argument("--user_id", type=str, required=True)
    args = parser.parse_args()

    _loop = asyncio.new_event_loop()
    threading.Thread(target=_loop.run_forever, daemon=True).start()

    run_on_loop(setup_client(args.user_id, args.character_id))
    uvicorn.run(app, host="0.0.0.0", port=args.port)
