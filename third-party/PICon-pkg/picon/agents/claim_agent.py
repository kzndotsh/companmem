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

class ClaimExtractorAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            role=kwargs.get('role', "extractor"),
            system_message=kwargs.get('system_message', ""),
            model=kwargs['model']
        )
    
    def act(self, message: str) -> Action:
        class ExtractorResponse(BaseModel):
            claim: str | None = None
            rationale: str | None = None # rationale for the claim (optional)
        
        class Claim(BaseModel):
            extracted: List[ExtractorResponse] | None = None
        self.memory.append({"role": "user", "content": message})
        for attempt in range(3):
            try:
                res = get_completion(
                    model=self.model,
                    messages=self.memory,
                    temperature=0.0,
                    response_format=Claim,
                )
                res_ext = Claim.model_validate_json(res.choices[0].message.content)  # validate response format
                if not res_ext.extracted or len(res_ext.extracted) == 0:
                    logging.warning("Extractor did not find any entities or claims. Skipping to next agent.")
                    self.memory.append({"role":"assistant", "content":"No entities extracted."})
                    return Action(
                        agent=self.role,
                        action_type="next_agent",
                        target_agent="questioner"
                    )
                self.memory.append({"role":"assistant", "content":str([extracted.model_dump_json() for extracted in res_ext.extracted])})
                return Action(
                    agent=self.role,
                    action_type="respond",
                    content = res_ext.extracted # list of ExtractorResponse
                )
            
            except (ValidationError, json.JSONDecodeError) as e:
                logging.exception(f"Response validation error: {e}")
                logging.info("Retrying extraction...")
                time.sleep(1)  # brief pause before retrying
        logging.error("Failed to extract entity and claim after multiple attempts.")
        return Action(
            agent=self.role,
            action_type="next_agent",
            target_agent="questioner"
        )    
