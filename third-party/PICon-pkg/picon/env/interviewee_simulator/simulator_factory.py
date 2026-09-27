from picon.env.interviewee_simulator.base_interviewee_simulator import BaseIntervieweeSimulator
from picon.env.interviewee_simulator.generic_agent_simulator import GenericAgentSimulator


def get_interviewee_simulator(baseline_name: str, **kwargs) -> BaseIntervieweeSimulator:
    """
    Unified factory: all baselines route to GenericAgentSimulator.

    The caller (main.py) is responsible for constructing the appropriate kwargs
    (persona, api_base, model, user_message_template, completion_kwargs, etc.)
    before calling this factory.
    """
    return GenericAgentSimulator(**kwargs)
