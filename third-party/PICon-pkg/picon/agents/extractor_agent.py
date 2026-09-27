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

class ExtractorAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            role=kwargs.get('role', "extractor"),
            system_message=kwargs.get('system_message', ""),
            model=kwargs['model'],
            port=kwargs.get('port', None),
            host=kwargs.get('host', 'localhost')
        )
    
    def act(self, message: str) -> Action:
        class ExtractorResponse(BaseModel):
            entity: str | None = None
            claims: List[str] | None = None
            rationale: str | None = None # rationale for the claim (optional)
        
        class EntityClaim(BaseModel):
            extracted: List[ExtractorResponse] | None = None
        self.memory.append({"role": "user", "content": message})
        for attempt in range(3):
            try:
                completion_kwargs = dict(
                    model=self.model,
                    messages=self.memory,
                    temperature=0.0 if not (self.model.startswith("gpt") or self.model.startswith("anthropic/")) else 1.0,
                    response_format=EntityClaim,
                    reasoning_effort="low"
                )
                if self.model.startswith("hosted_vllm/"):
                    assert self.port is not None, "Port must be specified for hosted_vllm models."
                    completion_kwargs['api_base'] = f"http://{self.host}:{self.port}/v1"
                res = get_completion(
                    **completion_kwargs
                )
                self._calculate_cost(res)
                res_ext = EntityClaim.model_validate_json(res.choices[0].message.content)  # validate response format
                if not res_ext.extracted or len(res_ext.extracted) == 0 or not any(item.entity for item in res_ext.extracted):
                    logging.warning("Extractor did not find any entities or claims. Skipping to next agent.")
                    self.memory.append({"role":"assistant", "content":"No entities extracted."})
                    return Action(
                        agent=self.role,
                        action_type="next_agent",
                        target_agent="questioner"
                    )
                
                filtered_res_ext = [item for item in res_ext.extracted if item.entity]
                
                self.memory.append({"role":"assistant", "content":str([extracted.model_dump_json() for extracted in filtered_res_ext])})
                return Action(
                    agent=self.role,
                    action_type="respond",
                    content = filtered_res_ext # list of ExtractorResponse
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


            


        