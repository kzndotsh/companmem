import os
import time
from typing import List, Dict, Any
from picon.agents.agent_factory import get_agent
from picon.schemas import State, Action, Observation, Turn, ToolOutput
from picon.utils import read_json, write_json
import logging
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))


class WebSearchTestEnv:
    def __init__(
        self,
        model: str,
        interview_data_path: str,
        tools: Dict = {},
        **kwargs
    ):
        self.model = model
        self.start_time = time.time()
        self.env_cost = 0.0
        self.interview_data_path = interview_data_path
        self.tools = tools

        self.agent = get_agent(
            "web_search",
            get_prompt_path("websearch_prompt.txt"),
            model=model,
            port=kwargs.get('port', None),
            host=kwargs.get('host', 'localhost'),
            tools=[tool.get_info() for tool in tools.values()] if tools else []
        )

        data = read_json(interview_data_path)
        if "session_1" in data:
            data = data["session_1"]

        # Build (extraction, history_so_far) pairs from the interview data.
        # Each turn may have an extractor action followed by web_search actions.
        # We replay every extractor output as a web_search input.
        self.samples: List[Dict] = []
        history_so_far: List[Dict] = []

        for turn in data["history"]:
            if not turn.get("environment_observation"):
                continue

            first_obs = turn["environment_observation"][0]
            if first_obs.get("observation_type") != "interviewee_response":
                continue

            response = first_obs["response"]
            qa_pair = {
                "question": response.get("question", ""),
                "answer": response.get("content", "")
            }

            # Find extractor action in this turn (action_type == "respond" with list content)
            for agent_action in turn.get("agent_action", []):
                if (
                    agent_action.get("action_type") == "respond"
                    and isinstance(agent_action.get("content"), list)
                ):
                    for extraction in agent_action["content"]:
                        if isinstance(extraction, dict) and "entity" in extraction:
                            self.samples.append({
                                "extraction": extraction,
                                "history": list(history_so_far),
                            })

            history_so_far.append(qa_pair)

        logging.info(f"Loaded {len(self.samples)} extraction samples from {interview_data_path}")

    def reset(self) -> State:
        self.state = State(current_turn=0, history=[])
        return self.state

    def invoke_tool(self, action: Action) -> ToolOutput | None:
        if action.action_type != "tool_call":
            return None
        tool_name = action.tool_call.tool_name
        if tool_name not in self.tools:
            logging.error(f"Tool '{tool_name}' not found.")
            return None
        tool = self.tools[tool_name]
        tool_output = tool.invoke(**action.tool_call.arguments)
        logging.info(f"[TOOL OUTPUT] {tool_name}: {str(tool_output)[:200]}...")
        return ToolOutput(
            tool_call_id=action.tool_call.details.get('tool_calls', [{}])[0].get('id', ''),
            tool_name=tool_name,
            arguments=action.tool_call.arguments,
            output=tool_output
        )

    def step(self):
        """Process one extraction sample: call web_search agent and invoke the tool."""
        if self.state.current_turn >= len(self.samples):
            logging.info("All samples have been processed.")
            return self.state, True

        sample = self.samples[self.state.current_turn]
        extraction = sample["extraction"]
        history = sample["history"]

        logging.info(
            f"[TURN {self.state.current_turn}] Entity: {extraction.get('entity')} | "
            f"Claims: {extraction.get('claims')}"
        )

        action = self.agent.act(extraction, history)
        logging.info(
            f"[ACTION] WebSearch: {action.action_type}"
            + (f" - {action.tool_call.tool_name}({action.tool_call.arguments})" if action.action_type == "tool_call" else "")
        )

        observations = []
        if action.action_type == "tool_call":
            tool_output = self.invoke_tool(action)
            if tool_output:
                observations.append(Observation(
                    observation_type="tool_output",
                    tool_output=[tool_output]
                ))

        turn = Turn(
            type='main_interrogation',
            agent_action=[action],
            environment_observation=observations
        )
        self.state.history.append(turn)
        self.state.current_turn += 1

        return self.state, False

    def save_state(self, path: str, termination_status: str = "Successfully completed"):
        """Save the current state to a json file."""
        final_result = {
            "agents_info": "web_search_agent",
            "model": self.model,
            "source_data_path": self.interview_data_path,
            "total_cost": self.agent.cost + self.env_cost,
            "duration": f"{(time.time() - self.start_time)/60:.2f} min",
            "termination_status": termination_status,
            "history": [obj.model_dump() for obj in self.state.history],
        }
        write_json(final_result, path)
        logging.info(f"Saving final result to {path}")
        logging.info(f"Total cost: ${final_result['total_cost']}, Duration: {final_result['duration']}")


if __name__ == "__main__":
    import os
    from argparse import ArgumentParser
    from picon.utils import setup_logging
    from picon.tools.web_search import GoogleClaimSearch
    from picon.tools.address_locator import GoogleGeocodeValidate

    setup_logging(log_to_file=True, process_name="web_search_test_env")
    load_dotenv()

    parser = ArgumentParser(description="Web Search Agent Test Environment")
    parser.add_argument("--model", type=str, default="gemini/gemini-2.5-flash", help="Model to use")
    parser.add_argument("--interview_data_path", type=str, required=True, help="Path to interview data JSON file")
    parser.add_argument("--port", type=int, default=None, help="Port for hosted_vllm models")
    args = parser.parse_args()

    tools = {}
    if os.getenv("GOOGLE_CLAIM_SEARCH") and os.getenv("GOOGLE_CX_ID"):
        tools["google_claim_search"] = GoogleClaimSearch(
            api_key=os.getenv("GOOGLE_CLAIM_SEARCH"),
            cx=os.getenv("GOOGLE_CX_ID"),
        )
    if os.getenv("GOOGLE_GEOCODE"):
        tools["google_geocode_validate"] = GoogleGeocodeValidate(
            api_key=os.getenv("GOOGLE_GEOCODE")
        )

    env = WebSearchTestEnv(
        model=args.model,
        interview_data_path=args.interview_data_path,
        tools=tools,
        port=args.port,
    )
    state = env.reset()
    done = False
    while not done:
        state, done = env.step()

    out_path = (
        f"data/prompt_engineering/web_search/"
        f"web_search_{time.strftime('%Y%m%d_%H%M%S')}"
        f"_{args.model.split('/')[-1]}"
        f"_{os.path.basename(args.interview_data_path).split('.')[0]}.json"
    )
    env.save_state(out_path)
