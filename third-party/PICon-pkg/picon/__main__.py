"""
CLI entry point for PICON.

Usage:
  # Mode 1: External agent endpoint (model optional)
  picon --agent_api_base http://localhost:8000/v1 --agent_name "MyAgent" --do_eval

  # Mode 2: LLM + persona prompt
  picon --agent_model gpt-5 --agent_persona "You are ..." --agent_name "John" --do_eval

  # Mode 2 with self-hosted endpoint
  picon --agent_api_base http://localhost:8000/v1 --agent_model meta-llama/Llama-3-8B --agent_persona "You are ..."
"""
from picon.utils import setup_logging, write_json
from picon.api import run_interview, run_evaluation
from dotenv import load_dotenv
import argparse
import os
import time
import logging


def parse_args():
    parser = argparse.ArgumentParser(description="Run interrogation evaluation on any agent endpoint.")
    # Agent endpoint (the evaluation target)
    parser.add_argument('--agent_api_base', type=str, default=None,
                        help='OpenAI-compatible API endpoint URL. If None, litellm routes by model name.')
    parser.add_argument('--agent_api_key', type=str, default=None,
                        help='API key for the agent endpoint (optional).')
    parser.add_argument('--agent_model', type=str, default=None,
                        help='Model name at the agent endpoint. Required unless --agent_api_base is provided.')
    parser.add_argument('--agent_persona', type=str, default=None,
                        help='System prompt / persona description. String or path to .txt file.')
    parser.add_argument('--agent_name', type=str, default='Agent',
                        help='Interviewee name (used in output file naming).')
    # Interrogation agent models
    parser.add_argument('--questioner_model', type=str, default=None)
    parser.add_argument('--extractor_model', type=str, default=None)
    parser.add_argument('--web_search_model', type=str, default=None)
    parser.add_argument('--evaluator_model', type=str, default=None)
    parser.add_argument('--nhd_model', type=str, default=None)
    # Port settings (for interrogation agents, not the evaluation target)
    parser.add_argument('--questioner_port', type=int, default=None)
    parser.add_argument('--extractor_port', type=int, default=None)
    parser.add_argument('--web_search_port', type=int, default=None)
    parser.add_argument('--evaluator_port', type=int, default=None)
    parser.add_argument('--nhd_port', type=int, default=None)
    # Other configurations
    parser.add_argument('--num_turns', type=int, default=None)
    parser.add_argument('--num_sessions', type=int, default=None)
    parser.add_argument('--question_seed', type=int, default=42)
    parser.add_argument('--log_to_file', action='store_true')
    # Prompt paths
    parser.add_argument('--questioner_prompt_path', type=str, default=None)
    parser.add_argument('--entity_extractor_prompt_path', type=str, default=None)
    parser.add_argument('--web_search_prompt_path', type=str, default=None)
    parser.add_argument('--evaluator_prompt_path', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)
    parser.add_argument('--question_file_path', type=str, default=None)
    parser.add_argument('--eval_factors', type=str, nargs='+', default=None,
                        choices=['internal', 'external', 'intra', 'inter'])
    parser.add_argument('--do_eval', action='store_true')

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(log_to_file=args.log_to_file, process_name="main")
    load_dotenv()

    if not args.agent_model and not args.agent_api_base:
        raise SystemExit("Error: Either --agent_model or --agent_api_base must be provided.")

    logging.info(f"Target: {args.agent_name} @ {args.agent_api_base or 'litellm'} / {args.agent_model or '(default)'}")

    _skip = {"agent_api_base", "agent_api_key", "agent_model", "agent_name", "agent_persona",
             "do_eval", "eval_factors", "log_to_file"}
    interview_kwargs = {k: v for k, v in vars(args).items() if k not in _skip}
    result = run_interview(
        name=args.agent_name,
        model=args.agent_model,
        persona=args.agent_persona or "",
        api_base=args.agent_api_base,
        api_key=args.agent_api_key,
        **interview_kwargs,
    )
    persona_stats = result["persona_stats"]

    if args.do_eval and result["env"] is not None:
        persona_stats = run_evaluation(result, eval_factors=args.eval_factors)

    # Save summary
    from picon.config import DEFAULT_CONFIG
    out_dir = args.output_dir or DEFAULT_CONFIG["output_dir"]
    summary_path = f"{out_dir}/{args.agent_name.replace(' ', '_')}/summary_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)

    summary = {
        "agent_name": args.agent_name,
        "agent_model": args.agent_model or "(endpoint default)",
        "agent_api_base": args.agent_api_base,
        "run_timestamp": time.strftime('%Y-%m-%d_%H-%M-%S'),
        "config": {
            "questioner_model": args.questioner_model,
            "evaluator_model": args.evaluator_model,
            "nhd_model": args.nhd_model,
            "num_turns": args.num_turns,
            "num_sessions": args.num_sessions,
        },
        "results": persona_stats,
    }
    write_json(summary, summary_path)

    logging.info("=" * 60)
    logging.info(f"RESULT: {args.agent_name}")
    logging.info("=" * 60)
    logging.info(f"Success: {persona_stats.get('success')}")
    logging.info(f"AI Detected: {persona_stats.get('ai_detected')}")
    logging.info(f"Duration: {persona_stats.get('duration_min', 0):.2f} min")
    logging.info(f"Cost: ${persona_stats.get('total_cost', 0):.4f}")
    logging.info(f"Turns: {persona_stats.get('num_turns_completed', 0)}")
    logging.info(f"Summary saved to: {summary_path}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
