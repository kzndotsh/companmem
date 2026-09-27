#!/usr/bin/env python3
"""
ContinuityBench Evaluation Runner

Supports parallel execution and multiple API providers.

Usage:
    # DeepSeek (native support)
    python run_eval.py --model deepseek/deepseek-chat --stressors all

    # DeepSeek via OpenAI-compatible endpoint
    python run_eval.py --model openai/deepseek-chat --stressors all

    # Anthropic
    python run_eval.py --model anthropic/claude-sonnet-4-6 --stressors all

    # DeepSeek Reasoner (captures reasoning_content)
    python run_eval.py --model deepseek/deepseek-reasoner --stressors all

    # Custom workers and output
    python run_eval.py --model deepseek/deepseek-chat --stressors all --workers 10 --output results/

    # Rescore existing results with a different judge (no re-running conversations)
    python run_eval.py --rescore results/deepseek_deepseek-chat_traditional.json --judge-model openai/anthropic/claude-sonnet-4-6

Environment variables (or .env file):
    DEEPSEEK_API_KEY    - Required for deepseek/ provider
    OPENAI_API_KEY      - Required for openai/ provider
    OPENAI_BASE_URL     - Optional: override OpenAI base URL
    ANTHROPIC_API_KEY   - Required for anthropic/ provider
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import jsonlines
import yaml
from tqdm import tqdm

from scoring.bc_score import BCScore
from scoring.judges import JudgeSystem, JudgeConfig
from scoring.report import generate_report


# ============================================================
# .env loader (no extra dependency needed)
# ============================================================


def load_dotenv(path: str = ".env"):
    """Load environment variables from a .env file if it exists."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            # Don't overwrite existing env vars
            if key not in os.environ:
                os.environ[key] = value


# Load .env on import
load_dotenv()


# ============================================================
# Model Interaction
# ============================================================

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"


def create_model_client(model_spec: str):
    """
    Create an API client for the target model.

    Supported providers:
        - deepseek/  -> DeepSeek API (uses DEEPSEEK_API_KEY)
        - openai/    -> OpenAI or compatible (uses OPENAI_API_KEY + optional OPENAI_BASE_URL)
        - anthropic/ -> Anthropic API (uses ANTHROPIC_API_KEY)
        - doubao/    -> Doubao / Volcengine API (uses DOUBAO_API_KEY)
        - aliyun/    -> Aliyun DashScope API (uses ALIYUN_API_KEY)
        - baidu/     -> Baidu Qianfan API (uses BAIDU_API_KEY)
        - kimi/      -> Moonshot / Kimi API (uses KIMI_API_KEY)
    """
    provider, model_name = model_spec.split("/", 1)

    if provider == "deepseek":
        import openai
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("Error: DEEPSEEK_API_KEY not set.")
            print("  Set it via: set DEEPSEEK_API_KEY=your-key  (Windows)")
            print("  Or add to .env file: DEEPSEEK_API_KEY=your-key")
            sys.exit(1)
        return "openai", model_name, openai.OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
        )
    elif provider == "doubao":
        import openai
        api_key = os.getenv("DOUBAO_API_KEY")
        if not api_key:
            print("Error: DOUBAO_API_KEY not set.")
            print("  Set it via: set DOUBAO_API_KEY=your-key  (Windows)")
            print("  Or add to .env file: DOUBAO_API_KEY=your-key")
            sys.exit(1)
        return "openai", model_name, openai.OpenAI(
            api_key=api_key,
            base_url=DOUBAO_BASE_URL,
        )
    elif provider == "aliyun":
        import openai
        api_key = os.getenv("ALIYUN_API_KEY")
        if not api_key:
            print("Error: ALIYUN_API_KEY not set.")
            print("  Set it via: set ALIYUN_API_KEY=your-key  (Windows)")
            print("  Or add to .env file: ALIYUN_API_KEY=your-key")
            sys.exit(1)
        return "openai", model_name, openai.OpenAI(
            api_key=api_key,
            base_url=ALIYUN_BASE_URL,
        )
    elif provider == "baidu":
        import openai
        api_key = os.getenv("BAIDU_API_KEY")
        if not api_key:
            print("Error: BAIDU_API_KEY not set.")
            print("  Set it via: set BAIDU_API_KEY=your-key  (Windows)")
            print("  Or add to .env file: BAIDU_API_KEY=your-key")
            sys.exit(1)
        return "openai", model_name, openai.OpenAI(
            api_key=api_key,
            base_url=BAIDU_BASE_URL,
        )
    elif provider == "kimi":
        import openai
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            print("Error: KIMI_API_KEY not set.")
            print("  Set it via: set KIMI_API_KEY=your-key  (Windows)")
            print("  Or add to .env file: KIMI_API_KEY=your-key")
            sys.exit(1)
        return "openai", model_name, openai.OpenAI(
            api_key=api_key,
            base_url=KIMI_BASE_URL,
        )
    elif provider == "openai":
        import openai
        base_url = os.getenv("OPENAI_BASE_URL")
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        return "openai", model_name, openai.OpenAI(**client_kwargs)
    elif provider == "anthropic":
        import anthropic
        return "anthropic", model_name, anthropic.Anthropic()
    else:
        print("Error: Unsupported provider '%s'." % provider)
        print("  Supported: deepseek/, openai/, anthropic/, doubao/, aliyun/, baidu/")
        print("  Example:   --model deepseek/deepseek-chat")
        sys.exit(1)


def get_model_response(
    provider: str,
    model_name: str,
    client,
    system_prompt: str,
    messages: list,
    temperature: float = 0.7,
) -> dict:
    """Get a response from the target model.

    Returns a dict with:
        - "content": the assistant's reply text
        - "reasoning_content": reasoning chain (deepseek-reasoner only, else None)
    """
    if provider == "openai":
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            temperature=temperature,
        )
        msg = response.choices[0].message
        return {
            "content": msg.content or "",
            "reasoning_content": getattr(msg, "reasoning_content", None),
        }

    elif provider == "anthropic":
        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
        )
        return {
            "content": response.content[0].text,
            "reasoning_content": None,
        }


# ============================================================
# Stressor Loading
# ============================================================

STRESSOR_FILES = {
    "domain_switch": "stressors/domain_switch.jsonl",
    "abstraction_hop": "stressors/abstraction_hop.jsonl",
    "goal_interrupt": "stressors/goal_interrupt.jsonl",
    "style_pull": "stressors/style_pull.jsonl",
    "multi_project_interleave": "stressors/multi_project_interleave.jsonl",
    "anti_drift_enforcement": "stressors/anti_drift_enforcement.jsonl",
    "burst_switch_meta": "stressors/burst_switch_meta.jsonl",
    "lexical_collision": "stressors/lexical_collision.jsonl",
    "stance_erosion": "stressors/stance_erosion.jsonl",
    "soc_social_engineering": "stressors/soc_social_engineering.jsonl",
    "adaptation_vs_drift": "stressors/adaptation_vs_drift.jsonl",
}

# Retired stressor variants. Never loaded by default — not by an explicit
# --stressors <type>, and not by --stressors all. Only --include-legacy pulls
# them in. See stressors/legacy/README.md for why they are quarantined rather
# than deleted.
LEGACY_STRESSOR_FILES = {
    "abstraction_hop": "stressors/legacy/abstraction_hop_v1.jsonl",
    "domain_switch": "stressors/legacy/domain_switch_v1.jsonl",
    "goal_interrupt": "stressors/legacy/goal_interrupt_v1.jsonl",
    "style_pull": "stressors/legacy/style_pull_v1.jsonl",
}

# Canonical status registry. Identity is NOT inferable from an ID or a filename
# — adf_001, bsm_001, lc_001 and se_001 use v1-style names but are official.
STRESSOR_MANIFEST = "stressors/manifest.json"


def load_stressors(stressor_types: list, max_variants: int = 30,
                   include_legacy: bool = False) -> list:
    """Load stressor sequences from JSONL files.

    Legacy variants are excluded unless include_legacy is set, so neither a
    normal run nor `--stressors all` can silently mix retired items into a
    result set.
    """
    stressors = []
    for st in stressor_types:
        if st not in STRESSOR_FILES:
            print("Warning: Unknown stressor type '%s', skipping." % st)
            continue
        paths = [STRESSOR_FILES[st]]
        if include_legacy and st in LEGACY_STRESSOR_FILES:
            paths.append(LEGACY_STRESSOR_FILES[st])
        for filepath in paths:
            if not os.path.exists(filepath):
                print("Warning: Stressor file not found: %s" % filepath)
                continue
            with jsonlines.open(filepath) as reader:
                for i, item in enumerate(reader.iter(skip_empty=True)):
                    if i >= max_variants:
                        break
                    item["_legacy"] = filepath in LEGACY_STRESSOR_FILES.values()
                    stressors.append(item)
    return stressors


# ============================================================
# Cost Estimation
# ============================================================

# Approximate USD per million tokens (input, output), matched by longest
# prefix of the model spec. These are PLANNING ESTIMATES for --dry-run and
# --max-cost-usd guardrails, not billing figures — provider pricing changes
# and your actual invoice is the authority. Update as needed.
COST_PER_MTOK = {
    "openai/anthropic/claude-opus":   (15.0, 75.0),
    "openai/anthropic/claude-sonnet": (3.0, 15.0),
    "openai/anthropic/claude-haiku":  (1.0, 5.0),
    "openai/google/gemini-3.1-pro":   (2.5, 15.0),
    "openai/google/gemini-3-flash":   (0.3, 2.5),
    "openai/openai/gpt-5.4":          (2.5, 20.0),
    "openai/openai/gpt-5.3":          (1.5, 12.0),
    "openai/openai/gpt-5-mini":       (0.25, 2.0),
    "openai/meta-llama":              (0.5, 2.0),
    "openai/qwen":                    (0.5, 2.0),
    "deepseek/deepseek-reasoner":     (0.6, 2.4),
    "deepseek/":                      (0.3, 1.2),
    "aliyun/":                        (0.4, 2.0),
    "doubao/":                        (0.3, 1.2),
    "baidu/":                         (0.4, 2.0),
    "kimi/":                          (0.6, 2.5),
}
DEFAULT_RATE = (1.0, 5.0)

CHARS_PER_TOKEN = 3.5
ASSUMED_RESPONSE_TOKENS = 800   # mean assistant reply; pilot runs averaged ~1.3k
JUDGE_RUBRIC_TOKENS = 1200      # rubric + instructions prepended to each call
JUDGE_OUTPUT_TOKENS = 1500

# JudgeSystem.evaluate() loops over the four dimensions, and
# evaluate_dimension() loops over config.passes inside each. One API call per
# (dimension, pass) — so a 26-item set at 3 passes issues 26 x 4 x 3 = 312
# judge calls, not 78.
JUDGE_DIMENSIONS = 4

# Per-item judge call structure by mode. Only the modes this branch can
# actually run are selectable via --judge-mode; the SEF entries are kept so a
# run can be priced before the judge is reinstated (see docs/judge_modes.md).
#   traditional / vanilla : dims x passes
#   sef (fixed)           : 1 anchor + dims x passes
#   sef_energy            : 1 anchor + 1 energy probe + dims x passes (expected)
SEF_ANCHOR_CALLS = 1
SEF_ENERGY_PROBE_CALLS = 1
# Deliberation is variable and unbounded in principle. Priced separately as a
# conservative ceiling: at most this many extra calls per (dimension, pass).
DELIBERATION_MAX_EXTRA_ROUNDS = 1
JUDGE_MODES_WITH_DELIBERATION = ("sef", "sef_energy")

# Models whose per-run cost is high enough that a batch sweep must stop and ask
# before starting them.
EXPENSIVE_PREFIXES = (
    "openai/anthropic/claude-opus",
    "openai/anthropic/claude-sonnet",
    "openai/openai/gpt-5.4",
    "openai/openai/gpt-5.3",
    "openai/google/gemini-3.1-pro",
)


def _rate_for(model_spec: str):
    best = ""
    for prefix in COST_PER_MTOK:
        if model_spec.startswith(prefix) and len(prefix) > len(best):
            best = prefix
    return COST_PER_MTOK[best] if best else DEFAULT_RATE


def is_expensive(model_spec: str) -> bool:
    return model_spec.startswith(EXPENSIVE_PREFIXES)


def judge_calls_per_item(judge_mode="traditional", judge_passes=3):
    """Judge API calls for one conversation, by mode.

    Returns (expected, upper_bound_including_deliberation).
    """
    base = JUDGE_DIMENSIONS * judge_passes
    if judge_mode == "sef":
        expected = SEF_ANCHOR_CALLS + base
    elif judge_mode == "sef_energy":
        expected = SEF_ANCHOR_CALLS + SEF_ENERGY_PROBE_CALLS + base
    else:                                     # traditional, vanilla
        expected = base
    upper = expected
    if judge_mode in JUDGE_MODES_WITH_DELIBERATION:
        upper += base * DELIBERATION_MAX_EXTRA_ROUNDS
    return expected, upper


def estimate_cost(stressors, model_spec, num_runs=1, judge_model=None,
                  judge_passes=3, judge_mode="traditional"):
    """Estimate calls, token volume and USD for a planned run.

    Generation input tokens are accumulated the way the API actually sees them:
    each assistant turn re-sends the whole conversation so far, so context grows
    turn by turn. Judge cost is priced per (dimension, pass) call, which is how
    JudgeSystem.evaluate() actually issues them.

    For modes with deliberation the expected and conservative-ceiling figures
    differ; both are returned so neither has to be guessed at the call site.
    """
    gen_calls = gin = gout = 0
    conv_tokens = []
    for s in stressors:
        ctx = len(s.get("system_prompt", "")) / CHARS_PER_TOKEN
        for u in [t for t in s.get("turns", []) if t.get("role") == "user"]:
            ctx += len(u.get("content", "")) / CHARS_PER_TOKEN
            gin += ctx                       # request carries the full history
            gout += ASSUMED_RESPONSE_TOKENS
            ctx += ASSUMED_RESPONSE_TOKENS   # reply joins the history
            gen_calls += 1
        conv_tokens.append(ctx)

    gen_calls *= num_runs
    gin *= num_runs
    gout *= num_runs

    jc_exp = jc_up = jin = jin_up = jout = jout_up = 0
    if judge_model:
        per_exp, per_up = judge_calls_per_item(judge_mode, judge_passes)
        for ct in conv_tokens:
            per_call_in = ct + JUDGE_RUBRIC_TOKENS
            jin += per_exp * per_call_in
            jin_up += per_up * per_call_in
        jc_exp = len(stressors) * per_exp * num_runs
        jc_up = len(stressors) * per_up * num_runs
        jin *= num_runs
        jin_up *= num_runs
        jout = jc_exp * JUDGE_OUTPUT_TOKENS
        jout_up = jc_up * JUDGE_OUTPUT_TOKENS

    ti, to = _rate_for(model_spec)
    gen_usd = (gin / 1e6) * ti + (gout / 1e6) * to
    judge_usd = judge_usd_up = 0.0
    if judge_model:
        ji, jo = _rate_for(judge_model)
        judge_usd = (jin / 1e6) * ji + (jout / 1e6) * jo
        judge_usd_up = (jin_up / 1e6) * ji + (jout_up / 1e6) * jo

    return {
        "judge_mode": judge_mode, "judge_passes": judge_passes,
        "conversations": len(stressors) * num_runs,
        "generation_calls": gen_calls,
        "generation_input_tokens": int(gin), "generation_output_tokens": int(gout),
        "generation_usd": gen_usd,
        "judge_calls": jc_exp, "judge_calls_upper": jc_up,
        "judge_input_tokens": int(jin), "judge_output_tokens": int(jout),
        "judge_input_tokens_upper": int(jin_up), "judge_output_tokens_upper": int(jout_up),
        "judge_usd": judge_usd, "judge_usd_upper": judge_usd_up,
        "deliberation_extra_calls_upper": jc_up - jc_exp,
        "deliberation_extra_usd_upper": judge_usd_up - judge_usd,
        "total_usd": gen_usd + judge_usd,
        "total_usd_upper": gen_usd + judge_usd_up,
    }


def print_cost_estimate(est, model_spec, judge_model):
    has_delib = est["deliberation_extra_calls_upper"] > 0
    print("Target-model generation")
    print("  calls:             %d  (%d conversation(s))"
          % (est["generation_calls"], est["conversations"]))
    print("  tokens:            %.2fM in / %.2fM out"
          % (est["generation_input_tokens"] / 1e6, est["generation_output_tokens"] / 1e6))
    print("  cost (%s): $%.2f" % (model_spec, est["generation_usd"]))

    if judge_model:
        print("Judge  [mode=%s, %d passes x %d dimensions]"
              % (est["judge_mode"], est["judge_passes"], JUDGE_DIMENSIONS))
        print("  calls:             %d%s"
              % (est["judge_calls"], "  (expected)" if has_delib else ""))
        print("  tokens:            %.2fM in / %.2fM out"
              % (est["judge_input_tokens"] / 1e6, est["judge_output_tokens"] / 1e6))
        print("  cost (%s): $%.2f" % (judge_model, est["judge_usd"]))
        if has_delib:
            print("  deliberation ceiling (priced separately, not in the expected figure):")
            print("    up to +%d calls  ->  up to +$%.2f"
                  % (est["deliberation_extra_calls_upper"],
                     est["deliberation_extra_usd_upper"]))

    print("Estimated total (planning figure, not a quote)")
    print("  expected:          $%.2f" % est["total_usd"])
    if has_delib:
        print("  conservative ceiling: $%.2f" % est["total_usd_upper"])


# ============================================================
# Conversation Runner
# ============================================================

def run_conversation(
    provider: str,
    model_name: str,
    client,
    stressor: dict,
    temperature: float = 0.7,
) -> list:
    """
    Run a stressor conversation against the target model.

    Returns the full conversation (user + assistant turns).
    Assistant turns include reasoning_content when available.
    """
    system_prompt = stressor["system_prompt"]
    conversation = []

    # Inject scripted context turns (user/assistant pairs) without calling the API.
    # Used in v2 stressors to establish a precise, reproducible ground truth before probes.
    for ctx in stressor.get("context_turns", []):
        conversation.append({
            "role": ctx["role"],
            "content": ctx["content"],
            "turn_id": len(conversation) + 1,
            "scripted": True,
        })

    for turn in stressor["turns"]:
        # User turn: add to history, then call the model
        conversation.append({
            "role": "user",
            "content": turn["content"],
            "phase": turn.get("phase", "unknown"),
            "turn_id": turn.get("turn_id", len(conversation) + 1),
        })

        # Only pass role + content to the API (strip metadata)
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in conversation
        ]
        response = get_model_response(
            provider, model_name, client,
            system_prompt, api_messages, temperature,
        )

        # Add assistant turn (with reasoning_content if present)
        assistant_turn = {
            "role": "assistant",
            "content": response["content"],
            "turn_id": turn.get("turn_id", len(conversation)),
        }
        if response["reasoning_content"]:
            assistant_turn["reasoning_content"] = response["reasoning_content"]

        conversation.append(assistant_turn)

    return conversation


def run_single_stressor(provider, model_name, client, stressor, temperature, judge):
    """Run a single stressor conversation + judge scoring. Used by parallel executor."""
    conversation = run_conversation(
        provider, model_name, client, stressor, temperature
    )

    score = None
    judge_error = None
    if judge is not None:
        try:
            score = judge.evaluate(
                conversation=conversation,
                system_prompt=stressor["system_prompt"],
                target_dimensions=stressor.get("target_dimensions"),
                stressor=stressor,
            )
        except Exception as e:
            judge_error = str(e)
            print("\nJudge failed for %s: %s (conversation saved)" % (stressor["id"], e))

    return {
        "stressor_id": stressor["id"],
        "stressor_type": stressor["type"],
        "system_prompt": stressor["system_prompt"],
        "difficulty": stressor["difficulty"],
        "conversation": conversation,
        "score": score.to_dict() if score else None,
        "judge_error": judge_error,
    }, score


# ============================================================
# Rescore Mode
# ============================================================

def find_stressor_by_id(stressor_id, stressor_type=None):
    """Try to find the original stressor definition for a given stressor_id.

    Returns the stressor dict if found, None otherwise.
    Needed so the judge can access baseline_markers for enhanced evaluation.
    """
    # Try all stressor files
    for st_name, filepath in STRESSOR_FILES.items():
        if not os.path.exists(filepath):
            continue
        try:
            with jsonlines.open(filepath) as reader:
                for item in reader:
                    if item.get("id") == stressor_id:
                        return item
        except Exception:
            continue
    return None


def rescore_results(results_path, judge, output_dir, model_name="rescored"):
    """Re-score existing conversation results with a (different) judge.

    Reads the conversation JSON, runs judge on each conversation,
    and saves new results + report.
    """
    print("\nRescore Mode")
    print("=" * 40)
    print("Input:  %s" % results_path)

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    print("Conversations found: %d" % len(results))

    all_scores = []
    rescored = []
    errors = 0

    for r in tqdm(results, desc="Rescoring"):
        sid = r["stressor_id"]
        stype = r["stressor_type"]
        conversation = r["conversation"]

        # Try to find original stressor for baseline_markers
        stressor = find_stressor_by_id(sid, stype)

        # We need the system_prompt. Try stressor first, then extract from conversation metadata.
        system_prompt = ""
        if stressor:
            system_prompt = stressor.get("system_prompt", "")
        if not system_prompt:
            # Fallback: check if it was saved in the result
            system_prompt = r.get("system_prompt", "You are a helpful assistant.")

        try:
            score = judge.evaluate(
                conversation=conversation,
                system_prompt=system_prompt,
                target_dimensions=stressor.get("target_dimensions") if stressor else None,
                stressor=stressor,
            )
            all_scores.append(score)
            r["score"] = score.to_dict()
            r["judge_error"] = None
            if "system_prompt" not in r:
                r["system_prompt"] = system_prompt
        except Exception as e:
            print("\nJudge failed for %s: %s" % (sid, e))
            r["score"] = None
            r["judge_error"] = str(e)
            errors += 1

        rescored.append(r)

    print("\nCompleted: %d/%d | Errors: %d" % (len(all_scores), len(results), errors))

    # Save rescored results
    os.makedirs(output_dir, exist_ok=True)

    # Derive filename from input
    input_stem = Path(results_path).stem
    rescored_path = os.path.join(output_dir, "%s_rescored.json" % input_stem)
    with open(rescored_path, "w", encoding="utf-8") as f:
        json.dump(rescored, f, indent=2, ensure_ascii=False)

    if all_scores:
        report_path = os.path.join(output_dir, "%s_rescored_report.json" % input_stem)
        generate_report(
            scores=all_scores,
            model_name=model_name,
            output_path=report_path,
        )
        print("\nRescored results: %s" % rescored_path)
        print("Rescored report:  %s" % report_path)
    else:
        print("\nRescored results: %s" % rescored_path)
        print("(All judge calls failed)")

    return rescored, all_scores


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ContinuityBench Evaluation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_eval.py --model deepseek/deepseek-chat --stressors all
  python run_eval.py --model openai/gpt-4o --stressors domain_switch,style_pull
  python run_eval.py --model anthropic/claude-sonnet-4-6 --workers 5 --output results/
  python run_eval.py --model deepseek/deepseek-reasoner --stressors all --skip-judge
  python run_eval.py --rescore results/deepseek_deepseek-chat_traditional.json --judge-model openai/anthropic/claude-sonnet-4-6
        """,
    )
    parser.add_argument(
        "--model", required=False, default=None,
        help="Target model as provider/model (e.g., deepseek/deepseek-chat). Not needed for --rescore."
    )
    parser.add_argument(
        "--stressors", default="all",
        help="Comma-separated stressor types or 'all' (default: all)"
    )
    parser.add_argument(
        "--config", default="configs/default",
        help="Path to evaluation config (default: configs/default)"
    )
    parser.add_argument(
        "--output", default="results/",
        help="Output directory for results (default: results/)"
    )
    parser.add_argument(
        "--max-variants", type=int, default=None,
        help="Override max variants per stressor type"
    )
    parser.add_argument(
        "--judge-model", default=None,
        help="Override judge model (e.g., deepseek/deepseek-chat)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Load stressors and show plan without running"
    )
    parser.add_argument(
        "--skip-judge", action="store_true",
        help="Run conversations only, without judge scoring"
    )
    parser.add_argument(
        "--judge-mode", default="traditional",
        choices=["vanilla", "traditional", "sef", "sef_energy"],
        help="Judge mode: 'vanilla' (original), 'traditional' (primary/secondary dims). 'sef' and 'sef_energy' are PRICING-ONLY on this branch — the SEF judge was removed (see docs/judge_modes.md); they can be costed with --dry-run but not run."
    )
    parser.add_argument(
        "--workers", type=int, default=5,
        help="Number of parallel workers (default: 5)"
    )
    parser.add_argument(
        "--rescore", default=None,
        help="Path to existing results JSON. Re-runs judge only (no new conversations). Requires --judge-model."
    )
    parser.add_argument(
        "--stressor-ids", default=None,
        help="Comma-separated stressor IDs to run (e.g. gi_v2_001,ah_v2_001). Overrides --stressors and --max-variants."
    )
    parser.add_argument(
        "--num-runs", type=int, default=1, metavar="N",
        help="Number of times to run each stressor (results are averaged). Default: 1."
    )
    parser.add_argument(
        "--model-name", default=None,
        help="Display name for the model in reports and leaderboard (e.g. 'Claude Opus 4.6'). Defaults to --model if not provided."
    )
    parser.add_argument(
        "--leaderboard", action="store_true",
        help="Run only the 26 leaderboard stressor variants (reads IDs from configs/default). Equivalent to --stressor-ids with the official set."
    )
    parser.add_argument(
        "--include-legacy", action="store_true",
        help="Also load retired legacy variants from stressors/legacy/. Excluded by default, including under --stressors all. Results are NOT leaderboard-comparable."
    )
    parser.add_argument(
        "--max-estimated-usd", type=float, default=None,
        help="Estimated-cost gate: refuse to START if the pre-flight ESTIMATE exceeds this. It is not a spend cap — it cannot stop or bound a run already in progress, and the estimate is a planning figure, not a quote. Use provider-side spend limits for real ceilings."
    )
    parser.add_argument(
        "--max-cost-usd", type=float, default=None,
        help=argparse.SUPPRESS   # deprecated: misleading name, implies a real cap
    )
    args = parser.parse_args()

    if args.max_cost_usd is not None:
        print("[!] --max-cost-usd is deprecated and renamed --max-estimated-usd.")
        print("    It gates on a pre-flight estimate and never caps actual spend.")
        if args.max_estimated_usd is None:
            args.max_estimated_usd = args.max_cost_usd

    # ---- Rescore mode ----
    if args.rescore:
        if not os.path.exists(args.rescore):
            print("Error: Results file not found: %s" % args.rescore)
            sys.exit(1)

        # Load config
        config = {}
        if os.path.exists(args.config):
            with open(args.config, encoding="utf-8") as f:
                config = yaml.safe_load(f)

        scoring_cfg = config.get("scoring", {})
        reference_judge = scoring_cfg.get("reference_judge_model", "openai/gpt-5-mini")
        judge_model = args.judge_model or scoring_cfg.get("judge_model", reference_judge)
        judge_passes = scoring_cfg.get("judge_passes", 3)
        judge_temp = scoring_cfg.get("judge_temperature", 0.1)

        is_reference_judge = (judge_model == reference_judge)
        print("Judge model: %s%s" % (judge_model, "" if is_reference_judge else " [non-reference]"))
        if not is_reference_judge:
            print("  Reference judge is: %s" % reference_judge)
            print("  Results are non-reference and should not be compared to official leaderboard scores.")

        judge = JudgeSystem(JudgeConfig(
            model=judge_model,
            passes=judge_passes,
            temperature=judge_temp,
        ))

        rescore_results(args.rescore, judge, args.output, model_name=args.judge_model or "rescored")
        return

    # ---- Normal mode ----
    if not args.model:
        print("Error: --model is required (unless using --rescore).")
        sys.exit(1)

    # Load config
    config = {}
    if os.path.exists(args.config):
        with open(args.config, encoding="utf-8") as f:
            config = yaml.safe_load(f)

    # --leaderboard flag: load IDs from config
    if args.leaderboard:
        lb_ids = config.get("stressors", {}).get("leaderboard_ids", [])
        if not lb_ids:
            print("Error: No leaderboard_ids found in config file: %s" % args.config)
            sys.exit(1)
        args.stressor_ids = ",".join(lb_ids)
        args.stressors = "all"  # need all types loaded to filter by ID
        print("Leaderboard mode: %d stressor variants" % len(lb_ids))

    # Determine stressor types
    if args.stressors == "all":
        stressor_types = list(STRESSOR_FILES.keys())
    else:
        stressor_types = [s.strip() for s in args.stressors.split(",")]

    # Load stressors
    max_variants = args.max_variants or config.get("evaluation", {}).get("variants_per_stressor", 10)
    if args.leaderboard and args.include_legacy:
        print("Error: --include-legacy cannot be combined with --leaderboard.")
        print("       The leaderboard set is defined by the 26 official IDs in %s." % args.config)
        sys.exit(1)
    stressors = load_stressors(stressor_types, max_variants,
                               include_legacy=args.include_legacy)

    # Filter by explicit stressor IDs if provided
    if args.stressor_ids:
        ids_set = {s.strip() for s in args.stressor_ids.split(",")}
        stressors = [s for s in stressors if s["id"] in ids_set]
        missing = ids_set - {s["id"] for s in stressors}
        if missing:
            print("Warning: stressor IDs not found: %s" % ", ".join(sorted(missing)))
            legacy_only = load_stressors(stressor_types, max_variants, include_legacy=True)
            hidden = {s["id"] for s in legacy_only if s.get("_legacy")} & missing
            if hidden:
                print("       These are legacy variants: %s" % ", ".join(sorted(hidden)))
                print("       Pass --include-legacy to load them (not leaderboard-comparable).")

    if not stressors:
        print("No stressors loaded. Check your stressor files.")
        sys.exit(1)

    n_legacy = sum(1 for s in stressors if s.get("_legacy"))
    if n_legacy:
        print("")
        print("!" * 72)
        print("!! WARNING: %d LEGACY stressor variant(s) included." % n_legacy)
        print("!! Legacy variants are retired and are NOT part of the 26-variant")
        print("!! leaderboard set. A pilot found severe ceiling compression on them")
        print("!! (see stressors/legacy/README.md). Results are NOT comparable to")
        print("!! published leaderboard scores and must not be reported as such.")
        print("!" * 72)
        print("")

    num_runs = args.num_runs
    stressor_runs = [(s, r) for s in stressors for r in range(num_runs)]
    total_runs = len(stressor_runs)
    workers = min(args.workers, total_runs)

    display_name = args.model_name or args.model

    print("\nContinuityBench Evaluation")
    print("=" * 40)
    if args.model_name and args.model_name != args.model:
        print("Target Model:   %s (display: %s)" % (args.model, args.model_name))
    else:
        print("Target Model:   %s" % args.model)
    print("Stressor Types: %s" % ", ".join(stressor_types))
    print("Total Variants: %d" % len(stressors))
    if num_runs > 1:
        print("Runs per stressor: %d (total: %d)" % (num_runs, total_runs))
    print("Workers:        %d" % workers)
    print("Output:         %s" % args.output)
    print()

    # Resolve the judge up front so both --dry-run and the estimated-cost gate
    # can account for judge calls, which usually dominate the token bill.
    scoring_cfg = config.get("scoring", {})
    planned_judge_model = None
    planned_judge_passes = scoring_cfg.get("judge_passes", 3)
    if not args.skip_judge:
        planned_judge_model = args.judge_model or scoring_cfg.get(
            "judge_model", scoring_cfg.get("reference_judge_model", "openai/gpt-5-mini"))

    est = estimate_cost(stressors, args.model, num_runs=num_runs,
                        judge_model=planned_judge_model,
                        judge_passes=planned_judge_passes,
                        judge_mode=args.judge_mode)
    # Gate on the conservative figure when a mode has unbounded deliberation.
    gate_usd = est["total_usd_upper"]

    if args.dry_run:
        print("Dry run - stressor plan:")
        for s in stressors:
            print("  [%s] %s%s (difficulty: %s, turns: %d, targets: %s)" % (
                s["type"], s["id"], " [LEGACY]" if s.get("_legacy") else "",
                s["difficulty"], len(s["turns"]), s["target_dimensions"]))
        print()
        print("Models:            1 (%s)" % args.model)
        print("Stressor variants: %d" % len(stressors))
        print_cost_estimate(est, args.model, planned_judge_model)
        if args.max_estimated_usd is not None:
            verdict = "OK" if gate_usd <= args.max_estimated_usd else "GATE WOULD BLOCK"
            print("Estimated-cost gate")
            print("  threshold:         $%.2f" % args.max_estimated_usd)
            print("  compared against:  $%.2f  -> %s" % (gate_usd, verdict))
        print("\nNo API calls were made.")
        return

    if args.judge_mode in ("sef", "sef_energy"):
        print("Error: judge mode '%s' cannot be run on this branch." % args.judge_mode)
        print("       The SEF judge was removed in e22fa20; see docs/judge_modes.md.")
        print("       The mode is retained for --dry-run cost modelling only.")
        sys.exit(1)

    if args.max_estimated_usd is not None and gate_usd > args.max_estimated_usd:
        print("Estimated-cost gate: refusing to start.")
        print("  estimate $%.2f exceeds --max-estimated-usd $%.2f"
              % (gate_usd, args.max_estimated_usd))
        print_cost_estimate(est, args.model, planned_judge_model)
        print("\nThis gate is a pre-flight check against an ESTIMATE. It cannot cap")
        print("actual spend once a run starts — set provider-side spend limits for that.")
        print("Raise the threshold, cut --num-runs, or narrow --stressor-ids.")
        sys.exit(2)

    print_cost_estimate(est, args.model, planned_judge_model)
    print()

    # Initialize model client
    provider, model_name, client = create_model_client(args.model)

    # Initialize judge
    judge = None
    is_reference_judge = True
    if not args.skip_judge:
        scoring_cfg = config.get("scoring", {})
        reference_judge = scoring_cfg.get("reference_judge_model", "openai/gpt-5-mini")
        judge_model = args.judge_model or scoring_cfg.get("judge_model", reference_judge)
        judge_passes = scoring_cfg.get("judge_passes", 3)
        judge_temp = scoring_cfg.get("judge_temperature", 0.1)

        is_reference_judge = (judge_model == reference_judge)
        if not is_reference_judge:
            print("[!] Non-reference judge: %s (reference: %s)" % (judge_model, reference_judge))
            print("    Results should be marked 'non-reference' — do not compare directly to leaderboard scores.")

        # "vanilla" and "traditional" use the same JudgeSystem;
        # the difference is that "traditional" marks primary/secondary dims
        # via target_dimensions (already wired through run_single_stressor)
        print("Judge mode: %s" % args.judge_mode)
        judge = JudgeSystem(JudgeConfig(
            model=judge_model,
            passes=judge_passes,
            temperature=judge_temp,
        ))

    # Run evaluations in parallel
    temperature = config.get("evaluation", {}).get("temperature", 0.7)
    all_scored = []   # list of (stressor_id, BCScore)
    all_conversations = []
    errors = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                run_single_stressor,
                provider, model_name, client, stressor, temperature, judge
            ): (stressor, run_idx)
            for stressor, run_idx in stressor_runs
        }

        with tqdm(total=total_runs, desc="Running stressors") as pbar:
            for future in as_completed(futures):
                stressor, run_idx = futures[future]
                try:
                    result, score = future.result()
                    all_conversations.append(result)
                    if score is not None:
                        all_scored.append((stressor["id"], score))
                    pbar.set_postfix({"done": stressor["id"]})
                except Exception as e:
                    print("\nError on %s: %s" % (stressor["id"], e))
                    # Save conversation even if judge failed
                    all_conversations.append({
                        "stressor_id": stressor["id"],
                        "stressor_type": stressor["type"],
                        "difficulty": stressor["difficulty"],
                        "conversation": [],
                        "score": None,
                        "judge_error": str(e),
                    })
                    errors += 1
                pbar.update(1)

    # Group scores by stressor_id for per-stressor reporting
    from collections import defaultdict
    per_stressor_scores = defaultdict(list)
    for sid, score in all_scored:
        per_stressor_scores[sid].append(score)

    all_scores = [score for _, score in all_scored]

    print("\nCompleted: %d/%d | Errors: %d" % (len(all_scores), len(all_conversations), errors))

    if not args.skip_judge and not all_scores:
        print("No evaluations completed successfully.")
        # Still save conversations so they can be rescored later
        if all_conversations:
            os.makedirs(args.output, exist_ok=True)
            safe_model_name = args.model.replace("/", "_")
            mode_suffix = "" if args.judge_mode == "vanilla" else "_%s" % args.judge_mode
            results_path = os.path.join(args.output, "%s%s.json" % (safe_model_name, mode_suffix))
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(all_conversations, f, indent=2, ensure_ascii=False)
            print("Conversations saved (no scores): %s" % results_path)
            print("You can rescore later with: python run_eval.py --rescore %s --judge-model <model>" % results_path)
        sys.exit(1)

    # Generate output
    os.makedirs(args.output, exist_ok=True)
    safe_model_name = args.model.replace("/", "_")

    # Add judge mode suffix to avoid overwriting across modes
    mode_suffix = "" if args.judge_mode == "vanilla" else "_%s" % args.judge_mode

    # Save full results (UTF-8 for Windows compatibility)
    results_path = os.path.join(args.output, "%s%s.json" % (safe_model_name, mode_suffix))
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_conversations, f, indent=2, ensure_ascii=False)

    # Generate and display report
    if all_scores:
        report_path = os.path.join(args.output, "%s%s_report.json" % (safe_model_name, mode_suffix))
        judge_metadata = {
            "judge_model": judge_model if not args.skip_judge else None,
            "is_reference_judge": is_reference_judge,
            "judge_mode": args.judge_mode,
        }
        generate_report(
            scores=all_scores,
            model_name=display_name,
            output_path=report_path,
            per_stressor=dict(per_stressor_scores),
            num_runs=num_runs,
            metadata=judge_metadata,
        )
        print("\nFull results: %s" % results_path)
        print("Report:       %s" % report_path)
    else:
        print("\nFull results: %s" % results_path)
        print("(Judge scoring was skipped)")


if __name__ == "__main__":
    main()
