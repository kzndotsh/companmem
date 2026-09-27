from typing import List, Dict, Any
import re
import time
from pydantic import BaseModel, Field, ValidationError
import logging
import litellm
from picon.utils import get_completion
import os
import json
import time
from picon.schemas import Action
from picon.agents.base_agent import Agent
litellm.drop_params = True

class KGAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            role=kwargs.get('role', "kg_agent"),
            system_message=kwargs.get('system_message', "Extract knowledge triplets from the given text."),
            model=kwargs['model']
        )
        self.kg: List[Dict[str, Any]] = []  # to store extracted triplets
    
    def act(self, message: str) -> Action:
        class TripletResponse(BaseModel):
            subject: str
            predicate: str
            object: str = Field(description="The object of the triplet; can be empty string if no object is found", default="")
            timestamp: str = Field(description="(optional) Time information associated with the triplet", default="")

        class TripletExtraction(BaseModel):
            triplets: List[TripletResponse] 
        self.memory.append({"role": "user", "content": message})
        for attempt in range(3):
            try:
                res = get_completion(
                    model=self.model,
                    messages=self.memory,
                    temperature=1.0 if self.model.startswith("gpt") else 0.0,
                    response_format=TripletExtraction,
                )
                self._calculate_cost(res)
                res_ext = TripletExtraction.model_validate_json(res.choices[0].message.content)  # validate response format
                triplets = [extracted.model_dump() for extracted in res_ext.triplets]
                self.memory.append({"role":"assistant", "content":str(triplets)})
                self.kg.extend(triplets)
                return Action(
                    agent=self.role,
                    action_type="respond",
                    content = res_ext.triplets # list of TripletResponse
                )
            
            except (ValidationError, json.JSONDecodeError) as e:
                logging.exception(f"Response validation error: {e}")
                logging.info("Retrying extraction...")
                time.sleep(1)  # brief pause before retrying
        logging.error("Failed to extract triplets after multiple attempts.")
        return Action(
            agent=self.role,
            action_type="next_agent",
            target_agent="questioner"
        )    
  