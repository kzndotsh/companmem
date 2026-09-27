"""
End-to-end test: HumanSimulacra via human_simulacra_server → picon.run()

Usage:
    python tests/test_human_simulacra.py
    python tests/test_human_simulacra.py --character "Mary Jones" --model "gemini/gemini-2.5-flash"

This script:
    1. Starts human_simulacra_server.py (RAG-based persona agent)
    2. Tests the endpoint directly
    3. Calls picon.run(api_base=...) for a short interview
    4. Tears everything down

Available characters:
    Erica Walker, Haley Collins, James Jones, Kevin Kelly,
    Leslie Nichols, Marsh Zhaleh, Mary Jones, Michael Miller,
    Robert Scott, Sara Ochoa, Tami Clark
"""
import os
import sys
import time
import signal
import subprocess
import requests
import argparse
import logging
import threading
import json

# ── Logging setup ───────────────────────────────────────────────────────────
# Force root logger so picon's internal logs ([ACTION], [RESPONSE]) show in real-time
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)
log = logging.getLogger("test_human_simulacra")

# ── Defaults ────────────────────────────────────────────────────────────────
DEFAULT_CHARACTER = "Mary Jones"
DEFAULT_MODEL = "gemini/gemini-2.5-flash"
SERVER_PORT = 8002

NUM_TURNS = 5
NUM_SESSIONS = 1


def stream_subprocess_output(proc: subprocess.Popen, prefix: str):
    """Stream subprocess stdout line-by-line with a prefix tag."""
    for line in iter(proc.stdout.readline, b""):
        text = line.decode("utf-8", errors="replace").rstrip()
        if text:
            log.info(f"[{prefix}] {text}")


def wait_for_server(url: str, timeout: int = 300, interval: int = 20) -> bool:
    """Poll until server is ready. HumanSimulacra RAG calls can be slow (~60s+)."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.post(
                url,
                json={
                    "model": "human_simulacra",
                    "messages": [{"role": "user", "content": "Hello"}],
                },
                timeout=120,
            )
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
                "model": "human_simulacra",
                "messages": [
                    {"role": "user", "content": "Hello, can you tell me a bit about yourself?"},
                ],
                "max_tokens": 256,
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
    parser = argparse.ArgumentParser(description="Test HumanSimulacra with picon.run()")
    parser.add_argument("--character", type=str, default=DEFAULT_CHARACTER,
                        help=f"Character name (default: {DEFAULT_CHARACTER})")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"LLM model for HumanSimulacra (default: {DEFAULT_MODEL})")
    parser.add_argument("--port", type=int, default=SERVER_PORT,
                        help=f"Server port (default: {SERVER_PORT})")
    parser.add_argument("--num_turns", type=int, default=NUM_TURNS)
    parser.add_argument("--num_sessions", type=int, default=NUM_SESSIONS)
    args = parser.parse_args()

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

    signal.signal(signal.SIGINT, lambda *_: (cleanup(), sys.exit(1)))

    try:
        # ── Step 1: Start human_simulacra_server ────────────────────────
        log.info("=" * 60)
        log.info(f"[1/3] Starting human_simulacra_server")
        log.info(f"       Character: {args.character}")
        log.info(f"       Model: {args.model}")
        log.info(f"       Port: {args.port}")
        log.info("=" * 60)

        server_cmd = [
            sys.executable, "servers/human_simulacra_server.py",
            "--port", str(args.port),
            "--character_name", args.character,
            "--model", args.model,
        ]
        log.info(f"CMD: {' '.join(server_cmd)}")

        server_proc = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        procs.append(server_proc)
        log.info(f"Server process started (PID: {server_proc.pid})")

        # Stream server logs in background thread
        t = threading.Thread(target=stream_subprocess_output, args=(server_proc, "HS_SERVER"), daemon=True)
        t.start()
        log_threads.append(t)

        # Wait for server to be ready (HumanSimulacra loads RAG data, may take a bit)
        server_url = f"http://localhost:{args.port}/v1"
        log.info("Waiting for HumanSimulacra server to load character data...")
        if not wait_for_server(f"{server_url}/chat/completions", timeout=120):
            log.error("FAILED: human_simulacra_server did not start in time")
            return False

        # ── Step 2: Test endpoint directly ──────────────────────────────
        log.info("=" * 60)
        log.info("[2/3] Testing human_simulacra_server chat completions...")
        log.info("=" * 60)

        if not test_chat_completions(server_url):
            log.error("FAILED: human_simulacra_server test failed")
            cleanup()
            return False
        log.info("human_simulacra_server test passed!")

        # ── Step 3: Run picon.run() ─────────────────────────────────────
        log.info("=" * 60)
        log.info(f"[3/3] Running picon.run()")
        log.info(f"       api_base: {server_url}")
        log.info(f"       name: {args.character}")
        log.info(f"       turns: {args.num_turns}, sessions: {args.num_sessions}")
        log.info(f"       do_eval: False")
        log.info("=" * 60)

        from dotenv import load_dotenv
        load_dotenv()

        import picon
        log.info("picon imported, starting run...")

        result = picon.run(
            persona="",  # persona is managed by the server
            api_base=server_url,
            name=args.character,
            num_turns=args.num_turns,
            num_sessions=args.num_sessions,
            do_eval=False,
            output_dir="data/results/test_human_simulacra",
        )

        log.info("=" * 60)
        log.info("TEST PASSED — picon.run() completed successfully!")
        log.info("=" * 60)
        log.info(f"Result path: {result.result_path}")
        log.info(f"Success: {result.success}")
        log.info(f"Summary: {json.dumps(result.summary, indent=2, default=str)[:500]}")

        # Check cost endpoint
        try:
            cost_r = requests.get(f"{server_url}/cost", timeout=5)
            if cost_r.status_code == 200:
                log.info(f"HumanSimulacra accumulated cost: {cost_r.json()}")
        except Exception:
            pass

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
