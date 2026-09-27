from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict, List
from picon.schemas import Action
import logging
from litellm.cost_calculator import completion_cost

class Agent(ABC):
    def __init__(self, role: str, **kwargs):
        self.role = role
        self.system_message = kwargs.get('system_message', "")
        self.memory: List = [
            {"role": "system", "content": self.system_message}
        ]
        if 'model' not in kwargs:
            raise ValueError("model must be specified for the agent.")
        self.model = kwargs['model']
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', None)
        self.cost = 0.0

    @abstractmethod
    def act(self, message: str | Dict | Any) -> Action:
        """Decide on an action based on the current state."""
        pass
    
    def reset(self):
        """Reset the agent's internal state."""
        self.memory = self.memory[:1]  # keep only the system message
    
    def _calculate_cost(self, response):
        self.cost += completion_cost(response) if not self.model.startswith("hosted_vllm/") else 0.0