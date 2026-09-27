from litellm.cost_calculator import completion_cost
from picon.utils import get_completion
from picon.schemas import Action, IntervieweeResponse
from picon.config import get_prompt_path
import logging
from dotenv import load_dotenv
import time
import os


class BaseIntervieweeSimulator:
    def __init__(self, **kwargs):
        load_dotenv()
        self.type = kwargs.get('baseline_name')
        self.name = kwargs.get('name', None)
        self.__nhd_prompt = open(get_prompt_path("nhd_detector.txt"), "r").read()
        self.__nhd_model = kwargs.get('nhd_model', 'gpt-5-nano')
        self.__nhd_port = kwargs.get('nhd_port', None)
        if self.__nhd_model.startswith("hosted_vllm/"):
            assert self.__nhd_port is not None, "NHD port must be provided for hosted_vllm models"
        self.cost = 0.0
        
        
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
    
    ##########################################################################
    ##                                                                      ##
    ##                            HELPER METHODS                            ##
    ##                                                                      ##
    ##########################################################################

    def get_max_token(self):
        if self.client_or_model.startswith("hosted_vllm/"):
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.client_or_model[len("hosted_vllm/"):])
            self.tokenizer = tokenizer
            return tokenizer.model_max_length
        else:
            from litellm import get_model_info, token_counter
            self.tokenizer = token_counter
            return get_model_info(self.client_or_model)['max_input_tokens']

    def _count_tokens(self, messages):
        if self.client_or_model.startswith("hosted_vllm/"):
            input_ids = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                return_tensors="pt",
                add_generation_prompt=True,
            )
            return input_ids.shape[1]+1024
        else:
            return self.tokenizer(model=self.client_or_model, messages=messages)

    def _truncate_history(self):
        """
        when the history is too long (> self.max_tokens), we need to truncate the history to fit the max tokens limit of the model
        """
        while self._count_tokens(self.history) > self.max_tokens and len(self.history) > 2:
            # Remove the oldest non-system message pair ([1] and [2]) to preserve the system prompt at [0]
            self.history.pop(1)
            self.history.pop(1)

    def _get_response(self, message: str) -> IntervieweeResponse:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def _ai_check(self, message: str, response: str):
        assert response is not None and response.strip() != "", "Received empty response from the interviewee."
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
    
    def calculate_cost(self) -> float:
        return self.cost