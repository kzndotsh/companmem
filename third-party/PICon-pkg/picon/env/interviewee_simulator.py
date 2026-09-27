from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
import asyncio
import gc
import torch
import logging
import re
from transformers import AutoTokenizer
from picon.env.personas.human_simulacra.hs_agents import Top_agent
from picon.utils import get_completion
from picon.schemas import Action, IntervieweeResponse
from picon.config import get_prompt_path
import time
import nest_asyncio
from dotenv import load_dotenv
import os
from litellm.cost_calculator import completion_cost

nest_asyncio.apply()

class IntervieweeSimulator:
    def __init__(self, **kwargs):
        load_dotenv()
        assert kwargs.get('baseline_name') in ["characterai", "human_simulacra", "opencharacter", "human_interview", "consistent_llm"], "Invalid baseline name"
        self.type = kwargs.get('baseline_name')
        self.name = kwargs.get('name', None)

        self.__nhd_prompt = open(get_prompt_path("nhd_detector.txt"), "r").read()
        self.__nhd_model = kwargs['nhd_model']
        self.__nhd_port = kwargs.get('nhd_port', None)
        if self.__nhd_model.startswith("hosted_vllm/"):
            assert self.__nhd_port is not None, "NHD port must be provided for hosted_vllm models"
        self.cost = 0.0
        
        if self.type == "characterai":
            #### **character_id, user_id, name** are required ####
            
            assert 'character_id' in kwargs, "Character AI requires character_id parameter"
            assert 'user_id' in kwargs, "Character AI requires user_id parameter"
            
            self.char_id = kwargs['character_id']
            self.user_id = kwargs['user_id']
            
            try:
                asyncio.run(self._setup_client_and_chat(kwargs['user_id'], kwargs['character_id']))
                assert self.chat_id is not None, "Chat ID must be set after setup"
                logging.info(f"CharacterAI client and chat session established. Chat ID: {self.chat_id}")
            except SessionClosedError as e:
                logging.error(f"Session closed error: {e}")
                self.client_or_model = None
                self.chat_id = None
            
        
        elif self.type == "human_simulacra":
            #### **name** are required
            assert 'name' in kwargs, "Human Simulacra requires name parameter"
            assert 'simulator_model' in kwargs, "Human Simulacra requires simulator_model parameter"
            self.client_or_model = Top_agent(character_name=kwargs['name'], model=kwargs['simulator_model']) ### has its own chat history
            
        elif self.type == "opencharacter": 
            #### **model_path, persona, profile** are required ####
            
            assert 'model_path' in kwargs, "OpenCharacter requires (path-like, either huggingface repo OR local path) model parameter"
            assert 'persona' in kwargs, "OpenCharacter requires persona parameter"
            assert 'profile' in kwargs, "OpenCharacter requires profile parameter"
            assert 'simulator_model' in kwargs, "OpenCharacter requires simulator_model parameter"
            assert 'port' in kwargs, "OpenCharacter requires port parameter"
            
            self.client_or_model = kwargs['model_path']
            self.tokenizer = AutoTokenizer.from_pretrained(kwargs['model_path'])
            self.history = [{
                "role": "system",
                "content": ("You are an AI character with the following Persona.\n\n"
                    f"# Persona\n{kwargs['persona']}\n\n"
                    f'# Character Profile\n{kwargs["profile"]}\n\n'
                    "Please stay in character, be helpful and harmless."
                ),
            }]
            self.name = re.search(r'^Name:\s*(.+)$', kwargs['profile'], flags=re.MULTILINE).group(1).strip() if self.name is None else self.name
            self.simulator_model = kwargs['simulator_model']
            self.host = kwargs.get('simulator_host', 'localhost')
            self.port = kwargs['port']

        elif self.type == "consistent_llm":
            assert 'model_path' in kwargs, "Consistent LLM requires (path-like, either huggingface repo OR local path) model parameter"
            assert 'persona' in kwargs, "Consistent LLM requires persona parameter"
            assert 'name' in kwargs, "Consistent LLM requires name parameter"
            assert 'instruction' in kwargs, "Consistent LLM requires instruction parameter"
            assert 'counterpart_name' in kwargs, "Consistent LLM requires counterpart_name parameter"
            assert 'simulator_model' in kwargs, "Consistent LLM requires simulator_model parameter"
            assert 'port' in kwargs, "Consistent LLM requires port parameter"
            
            self.client_or_model = kwargs['model_path']
            self.simulator_model = kwargs['simulator_model']
            self.host = kwargs.get('simulator_host', 'localhost')
            self.tokenizer = AutoTokenizer.from_pretrained(kwargs['model_path'])
            self.persona = kwargs['persona']
            self.history = []
            self.instruction = kwargs['instruction']
            self.counterpart_name = kwargs['counterpart_name']
            self.prompt_flag = "Your conversation so far is below:\nConversation: \n"
            self.port = kwargs['port']
        
        else: # human_interview
            self.name = input("Enter your name: ") if self.name is None else self.name
            logging.info(f"Hi {self.name}, you will be the interviewee. Please read the instructions carefully before the interview starts.")

    def get_response(self, message: str) -> IntervieweeResponse:
        error_message = ""
        for attempt in range(3):  # Retry up to 3 times
            try:
                return self._get_response(message)
            except Exception as e:
                # if "AI Detected", immediately raise value error
                if str(e) == "AI Detected":
                    raise e
                logging.error(f"Error getting response: {e}. Attempt {attempt + 1} of 3.")
                error_message += f"Attempt {attempt + 1}: {str(e)}\n"
                time.sleep(2)  # Wait before retrying
        logging.error(f"All attempts failed. Errors:\n{error_message}")
        raise RuntimeError(f"Failed to get persona response after 3 attempts. Errors:\n{error_message}")

    def calculate_cost(self):
        if self.type == "human_simulacra":
            return self.client_or_model.calculate_cost() + self.cost
        else:
            return self.cost

    def _get_response(self, message: str) -> IntervieweeResponse:
        if self.type == "characterai":
            # Add a small delay before sending message
            time.sleep(0.5)  # 500ms delay
           
            response = asyncio.run(
                self.client_or_model.chat.send_message(
                    character_id=self.char_id, 
                    chat_id=self.chat_id, 
                    text=message
                )
            )
            response = response.get_primary_candidate().text
        
        elif self.type == "human_simulacra":
            response = self.client_or_model.send_message(message)
            logging.info(f"Human Simulacra response cost so far: {self.client_or_model.calculate_cost():.6f} USD")
        
        elif self.type == "opencharacter": # OpenCharacter
            self.history.append({
                "role": "user",
                "content": message
            })
            
            while True:
                input_ids = self.tokenizer.apply_chat_template(
                    self.history,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                )

                if input_ids.shape[1] + 1024 <= 8192:
                    break

                # drop oldest assistant-user pair but keep system prompt
                if len(self.history) > 3:
                    self.history = [self.history[0]] + self.history[3:]
                else:
                    # still too long even after pruning – fallback
                    self.history = [self.history[0]] + self.history[-2:]

            
            res = get_completion(
                model=self.simulator_model,
                messages=self.history,
                reasoning_effort="low",
                api_base=f"http://{self.host}:{self.port}/v1",
                max_tokens=1024,
                temperature=0.9,
                top_p=0.9,
            )
            
            response = res.choices[0].message.content.strip()
            self.history.append({
                "role": "assistant",
                "content": response
            })
        elif self.type == "consistent_llm" : # Consistent LLM & OpenCharacter (local vLLM)
            self.history.append(f"Interviewer: {message}")
            
            while True:
                input_message = self.persona + self.prompt_flag + '\n'.join(self.history) + self.instruction
                messages = [{
                    "role": "user",
                    "content": input_message
                }]
                input_ids = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                )

                if input_ids.shape[1]+1024 <= 8192: # assuming model max position is 8192
                    break
                
                self.history = self.history[2:]  # drop the oldest message
                
            res = get_completion(
                model=self.simulator_model,
                messages=[{"role":"system", "content": self.persona}, {"role":"user", "content": input_message}],
                reasoning_effort="low",
                api_base=f"http://{self.host}:{self.port}/v1",
                max_tokens=1024
            )
            # response = self.tokenizer.decode(output_ids[0][input_ids.shape[-1]:], skip_special_tokens=True)    
            response = res.choices[0].message.content.strip()
            self.history.append(f"{self.name}: {response}")
        else:  # human_interview
            response = input(f"Your Response: ")
        
        assert response is not None and response.strip() != "", "Received empty response from the interviewee."
        # nhd
        while True:
            completion_kwargs = dict(
                model=self.__nhd_model,
                messages=[{"role":"system", "content": self.__nhd_prompt}, {"role":"user", "content": f"Interviewer:{message}\nInterviewee: {response}"}],
                reasoning_effort="low",
                temperature=1.0 if self.__nhd_model.startswith("gpt") else 0.0,
            )
            if self.__nhd_model.startswith("hosted_vllm/"):
                completion_kwargs['api_base'] = f"http://localhost:{self.__nhd_port}/v1"
            res = get_completion(**completion_kwargs)
            self.cost += completion_cost(res) if not self.__nhd_model.startswith("hosted_vllm/") else 0.0
            res_ = res.choices[0].message.content.strip()
            if res_ in ['### PASS ###', '### FAIL ###']:
                break
            else:
                logging.warning("NHD Detector returned invalid response. Retrying...")
                logging.warning(f"Response was: {res_}")
        if res_ == '### FAIL ###':
            logging.warning("AI Detected! Terminating the interview: " + response)
            raise ValueError("AI Detected")
        
        return IntervieweeResponse(
            question=message,
            content=response
        )
   
    async def _setup_client_and_chat(self, user_id: str, char_id: str ):
        try:
            self.client_or_model = await get_client(user_id)
            
            me_task = asyncio.create_task(self.client_or_model.account.fetch_me())
            chat_task = asyncio.create_task(self.client_or_model.chat.create_chat(char_id))
            
            me, (chat, greeting_message) = await asyncio.gather(me_task, chat_task)
            
            self.chat_id = chat.chat_id
            
        except Exception as e:
            logging.error(f"Failed to set up the cai client: {e}")
            await self.client_or_model.close_session()
    def clear_model(self):
        if self.type == "opencharacter" or self.type == "consistent_llm": # no action needed for other types
            del self.client_or_model
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    
    async def close(self):
        if self.type == "characterai":
            if hasattr(self, 'client_or_model') and self.client_or_model is not None:
                await self.client_or_model.close_session()
                self.client_or_model = None
                self.chat_id = None
                