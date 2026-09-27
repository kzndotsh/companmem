"""
End-to-end test: OpenCharacter (LoRA on Llama-3-8B) via vLLM → template_server → picon.run()

Usage:
    python tests/test_opencharacter_vllm.py

This script:
    1. Starts vLLM with OpenCharacter LoRA adapter
    2. Starts template_server.py wrapping the vLLM endpoint with a persona
    3. Calls picon.run(api_base=...) for a short interview
    4. Tears everything down
"""
import os
import sys
import time
import signal
import subprocess
import requests
import json
import logging
import threading

# ── Logging setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("test_opencharacter")

# ── Config ──────────────────────────────────────────────────────────────────
BASE_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
LORA_ADAPTER = '{"name": "open-char", "path": "willystumblr/opencharacter-sft-2025-06-21_14-54-13"}'
SERVED_MODEL_NAME = "opencharacter-llama3-8b"

VLLM_PORT = 8000
WRAPPER_PORT = 8001
VLLM_GPU = "0,1"  # Single GPU is enough for 8B

AGENT_NAME = "Alice"
AGENT_PERSONA = (
    "You are Alice, a 32-year-old librarian from Portland, Oregon. "
    "You love classic literature, hiking, and baking sourdough bread. "
    "You grew up in a small town in Vermont and moved to Portland after college. "
    "You have a golden retriever named Biscuit. "
    "Always stay in character and respond naturally as Alice would."
)

# Short test run
NUM_TURNS = 5
NUM_SESSIONS = 1


def stream_subprocess_output(proc: subprocess.Popen, prefix: str):
    """Stream subprocess stdout line-by-line with a prefix tag."""
    for line in iter(proc.stdout.readline, b""):
        text = line.decode("utf-8", errors="replace").rstrip()
        if text:
            log.info(f"[{prefix}] {text}")


def wait_for_server(url: str, timeout: int = 300, interval: int = 5) -> bool:
    """Poll until server is ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                log.info(f"Server ready at {url} (took {int(time.time() - start)}s)")
                return True
        except requests.ConnectionError:
            pass
        elapsed = int(time.time() - start)
        log.info(f"Waiting for {url} ... ({elapsed}s / {timeout}s)")
        time.sleep(interval)
    log.error(f"Server at {url} did not become ready within {timeout}s")
    return False


def test_chat_completions(url: str) -> bool:
    """Quick sanity check: send a message and see if we get a response."""
    log.info(f"Sending test chat request to {url}/chat/completions ...")
    try:
        r = requests.post(
            f"{url}/chat/completions",
            json={
                "model": SERVED_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, who are you?"},
                ],
                "max_tokens": 128,
            },
            timeout=60,
        )
        log.info(f"Response status: {r.status_code}")
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        log.info(f"Response content: {content[:300]}")
        return bool(content.strip())
    except Exception as e:
        log.error(f"Chat test failed: {e}")
        return False


def main():
    procs = []
    log_threads = []

    def cleanup():
        log.info("Cleaning up subprocesses...")
        for p in procs:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                log.info(f"  Sent SIGTERM to process group {p.pid}")
            except Exception as e:
                log.warning(f"  Failed to kill process {p.pid}: {e}")

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda *_: (cleanup(), sys.exit(1)))

    try:
        # ── Step 1: Start vLLM ──────────────────────────────────────────
        log.info("=" * 60)
        log.info(f"[1/4] Starting vLLM: {BASE_MODEL}")
        log.info(f"       LoRA: {LORA_ADAPTER}")
        log.info(f"       GPU: CUDA_VISIBLE_DEVICES={VLLM_GPU}")
        log.info(f"       Port: {VLLM_PORT}")
        log.info("=" * 60)

        vllm_cmd = [
            "vllm", "serve", BASE_MODEL,
            "--enable-lora",
            "--lora-modules", f"{LORA_ADAPTER}",
            "--tensor-parallel-size", "2",
            "--served-model-name", SERVED_MODEL_NAME,
            "--port", str(VLLM_PORT),
            "--max-model-len", "4096",
            "--gpu-memory-utilization", "0.8",
        ]
        vllm_env = os.environ.copy()
        vllm_env["CUDA_VISIBLE_DEVICES"] = VLLM_GPU
        log.info(f"CMD: {' '.join(vllm_cmd)}")

        vllm_proc = subprocess.Popen(
            vllm_cmd,
            env=vllm_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        procs.append(vllm_proc)
        log.info(f"vLLM process started (PID: {vllm_proc.pid})")

        # Stream vLLM logs in background thread
        t = threading.Thread(target=stream_subprocess_output, args=(vllm_proc, "vLLM"), daemon=True)
        t.start()
        log_threads.append(t)

        # Wait for vLLM to be ready
        vllm_url = f"http://localhost:{VLLM_PORT}/v1"
        if not wait_for_server(f"{vllm_url}/models", timeout=300):
            log.error("FAILED: vLLM did not start in time")
            return False

        log.info("vLLM is ready!")

        # ── Step 2: Test vLLM directly ──────────────────────────────────
        log.info("=" * 60)
        log.info("[2/4] Testing vLLM direct chat completions...")
        log.info("=" * 60)

        if not test_chat_completions(vllm_url):
            log.error("FAILED: vLLM direct test failed")
            cleanup()
            return False
        log.info("vLLM direct test passed!")

        # ── Step 3: Start template_server ───────────────────────────────
        log.info("=" * 60)
        log.info(f"[3/4] Starting template_server")
        log.info(f"       Wrapping: {vllm_url} / {SERVED_MODEL_NAME}")
        log.info(f"       Persona: {AGENT_PERSONA[:80]}...")
        log.info(f"       Name: {AGENT_NAME}")
        log.info(f"       Port: {WRAPPER_PORT}")
        log.info("=" * 60)

        server_cmd = [
            sys.executable, "servers/template_server.py",
            "--port", str(WRAPPER_PORT),
            "--vllm_base", vllm_url,
            "--vllm_model", SERVED_MODEL_NAME,
            "--persona", AGENT_PERSONA,
            "--name", AGENT_NAME,
        ]
        log.info(f"CMD: {' '.join(server_cmd)}")

        server_proc = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        procs.append(server_proc)
        log.info(f"template_server process started (PID: {server_proc.pid})")

        # Stream server logs in background thread
        t2 = threading.Thread(target=stream_subprocess_output, args=(server_proc, "WRAPPER"), daemon=True)
        t2.start()
        log_threads.append(t2)

        wrapper_url = f"http://localhost:{WRAPPER_PORT}/v1"
        log.info("Waiting 3s for FastAPI to start...")
        time.sleep(3)

        if not test_chat_completions(wrapper_url):
            log.error("FAILED: template_server test failed")
            cleanup()
            return False
        log.info("template_server test passed (persona baked in)!")

        # ── Step 4: Run picon.run() ─────────────────────────────────────
        log.info("=" * 60)
        log.info(f"[4/4] Running picon.run()")
        log.info(f"       api_base: {wrapper_url}")
        log.info(f"       name: {AGENT_NAME}")
        log.info(f"       turns: {NUM_TURNS}, sessions: {NUM_SESSIONS}")
        log.info(f"       do_eval: False")
        log.info("=" * 60)

        from dotenv import load_dotenv
        load_dotenv()

        import picon
        log.info("picon imported, starting run...")

        result = picon.run(
            persona="",  # persona is managed by the wrapping server
            api_base=wrapper_url,
            name=AGENT_NAME,
            num_turns=NUM_TURNS,
            num_sessions=NUM_SESSIONS,
            do_eval=False,
            output_dir="data/results/test_opencharacter",
        )

        log.info("=" * 60)
        log.info("TEST PASSED — picon.run() completed successfully!")
        log.info("=" * 60)
        log.info(f"Result path: {result.result_path}")
        log.info(f"Sessions: {len(result.histories)}")
        for i, h in enumerate(result.histories):
            log.info(f"  Session {i+1}: {len(h)} turns")

        # Show a sample Q&A
        if result.histories and result.histories[0]:
            sample = result.histories[0][0]
            log.info(f"Sample Q: {str(sample.get('question', ''))[:200]}")
            log.info(f"Sample A: {str(sample.get('answer', ''))[:200]}")

        return True

    except Exception as e:
        log.error(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
