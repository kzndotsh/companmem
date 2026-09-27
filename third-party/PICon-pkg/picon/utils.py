import json
import os
from typing import List, Any
import logging
import time
import select
import sys
import litellm
from litellm import completion
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from github import Github
except ImportError:
    Github = None

def read_json(file_path: str) -> Any:
    with open(file_path, "r") as f:
        return json.load(f)
def write_json(data: Any, file_path: str) -> None:
    if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
def read_jsonl(file_path: str) -> List[Any]:
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data
def write_jsonl(data: List[Any], file_path: str) -> None:
    if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

def get_completion(model: str, messages: list, temperature: float = 1.0, max_retries=3, **kwargs):
    litellm.drop_params = True
    for attempt in range(1, max_retries+1):
        try:
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            assert response.choices and len(response.choices) > 0, f"Invalid response from completion API: No choices : {response}"
            return response
        except Exception as e:
            logging.error(f"Error during completion: {e}")
            wait_time = 30
            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time) 
    logging.exception("Max retries reached. Raising exception.")
    raise RuntimeError("Failed to get completion after multiple attempts.")


def setup_logging(log_to_file: bool, process_name: str = None):
    if log_to_file:
        os.makedirs(f'logs/{time.strftime("%Y-%m-%d")}', exist_ok=True)
        log_filename = f'logs/{time.strftime("%Y-%m-%d")}/{process_name}_{time.strftime("%Y-%m-%d_%H-%M-%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s  %(levelname)s  %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ])
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s  %(levelname)s  %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    for noisy in ("LiteLLM", "httpx", "google", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)    


def batch_request(messages: List, model: str, display_name: str = None, sub_batch: bool = False, 
                  inline: bool = True, **kwargs):
    """
    Unified batch processing method that intelligently handles different providers and approaches.
    
    Args:
        messages: List of message lists to process
        model: Model name (determines provider automatically)
        display_name: Display name for the batch job
        sub_batch: Whether to split into sub-batches of 500
        inline: For Gemini, whether to use inline requests (True) or file upload (False)
        **kwargs: Additional parameters for specific providers
    
    Returns:
        List of results from batch processing
    """
    assert messages is not None, "Messages must be provided"
    
    # Determine provider from model name
    if any(provider in model.lower() for provider in ['gpt', 'openai']):
        provider = 'openai'
    elif any(provider in model.lower() for provider in ['gemini', 'google']):
        provider = 'gemini'
        model = model.split('/')[-1]  # Use only the model part for Gemini
    else:
        raise ValueError(f"Unsupported model: {model}. Cannot determine provider.")
    
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    results = []
    batch_size = 500 if sub_batch else len(messages)
    
    for i in range(0, len(messages), batch_size):
        batch_messages = messages[i:i + batch_size]
        
        if provider == 'openai':
            results.extend(_process_openai_batch(batch_messages, model, i, batch_size, temp_dir, **kwargs))
        elif provider == 'gemini':
            if inline:
                results.extend(_process_gemini_inline_batch(batch_messages, model, display_name, i, batch_size))
            else:
                results.extend(_process_gemini_file_batch(batch_messages, model, display_name, i, batch_size, temp_dir))
    
    return results


def _process_openai_batch(messages: List, model: str, batch_index: int, batch_size: int, temp_dir: str, **kwargs):
    """Process OpenAI batch requests"""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    filepath = f"{temp_dir}/request_{batch_index//batch_size}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"
    
    # Prepare JSONL file
    jsonl_chunks = []
    for j, message in enumerate(messages):
        jsonl_format = {
            "custom_id": f"request-{j}", 
            "method": "POST", 
            "url": "/v1/chat/completions", 
            "body": {
                "model": model, 
                "messages": message,
                #"reasoning": { "effort": "low" }
            }
        }
        jsonl_chunks.append(json.dumps(jsonl_format))
    
    with open(filepath, "w") as f:
        f.write("\n".join(jsonl_chunks))
    
    # Upload and create batch
    file_obj = client.files.create(
        file=open(filepath, "rb"),
        purpose="batch",
        expires_after={"anchor": "created_at", "seconds": 86400*2}
    )
    
    batch_job = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    batch_job.errors
    
    # Wait for completion and process results
    return _wait_and_process_openai_results(client, batch_job)


def _process_gemini_inline_batch(messages: List, model: str, display_name: str, batch_index: int, batch_size: int):
    """Process Gemini inline batch requests"""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    request_list = []
    for message in messages:
        contents = []
        system_instruction = {}
        for msg in message:
            if msg['role'] == 'system':
                system_instruction['parts'] = [{'text': msg['content']}]
            else:
                contents.append({
                    'parts': [{'text': msg['content']}],
                    'role': msg['role']
                })
        request_list.append({
            'contents': contents,
            'config': {
                'system_instruction': system_instruction,
                "thinking_config": {"thinking_budget":1024}
            }
        })
        
    batch_job = client.batches.create(
        model=model,
        src=request_list,
        config={'display_name': display_name or f"inline_batch_{time.strftime('%Y-%m-%d_%H-%M-%S')}"}
    )
    
    return _wait_and_process_gemini_results(client, batch_job, inline=True)


def _process_gemini_file_batch(messages: List, model: str, display_name: str, batch_index: int, batch_size: int, temp_dir: str):
    """Process Gemini file-based batch requests"""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    request_list = []
    for message in messages:
        contents = []
        system_instruction = {}
        for msg in message:
            if msg['role'] == 'system':
                system_instruction['parts'] = [{'text': msg['content']}]
            else:
                contents.append({
                    'parts': [{'text': msg['content']}],
                    'role': msg['role']
                })
        request_list.append({
            'contents': contents,
            'config': {
                'system_instruction': system_instruction,
                "thinking_config": {"thinking_budget":1024}
            }
        })
    
    # Prepare JSONL file
    jsonl_chunks = [{
        "key": f"request_{batch_index//batch_size}_{j}",
        "request": req
    } for j, req in enumerate(request_list)]
    
    filepath = f"{temp_dir}/request_{batch_index//batch_size}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"
    with open(filepath, "w") as f:
        f.write("\n".join(json.dumps(chunk) for chunk in jsonl_chunks))
    
    # Upload file and create batch
    uploaded_file = client.files.upload(
        file=filepath,
        config=genai_types.UploadFileConfig(
            display_name=display_name or f"batch_file_{time.strftime('%Y-%m-%d_%H-%M-%S')}",
            mime_type="jsonl"
        )
    )
    
    batch_job = client.batches.create(
        model=model,
        src=uploaded_file.name,
        config={'display_name': display_name or f"batch_job_{time.strftime('%Y-%m-%d_%H-%M-%S')}"}
    )    
    
    return _wait_and_process_gemini_results(client, batch_job, inline=False)


def _wait_and_process_openai_results(client: OpenAI, batch_job):
    """Wait for OpenAI batch completion and process results"""
    results = []
    while True:
        job = client.batches.retrieve(batch_job.id)
        state = job.status
        logging.info(f"Current state: {state}")
        # logging.info(f"job: {job}")
        # logging.info(f"job.errors: {job.errors}")
        if state == "completed":
            logging.info("✅ Job succeeded!")
            logging.info(f"Output file ID: {job.output_file_id}")
            try:
                retrieved_file_obj = client.files.content(job.output_file_id)
                for line in retrieved_file_obj.iter_lines():
                    result = json.loads(line)
                    
                    text = result.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
                    results.append(text)
                break
            except Exception as e:
                logging.error(f"Error retrieving or processing output file: {e}")
                err_stream = client.files.content(job.error_file_id)
                for line in err_stream.iter_lines():
                    if not line:
                        continue
                    record = json.loads(line)
                    with open("./error_record.json", "w") as f:
                        f.write(json.dumps(record, indent=2))
                raise
        elif state in ("failed", "cancelled"):
            logging.error(f"Batch job failed with status: {state} - {job.errors}")
            raise RuntimeError(f"Batch job failed: {state}")
        
        else:
            time.sleep(10)
    
    return results


def _wait_and_process_gemini_results(client, batch_job, inline=True):
    """Wait for Gemini batch completion and process results"""
    results = []
    while True:
        job = client.batches.get(name=batch_job.name)
        state = job.state.name
        logging.info(f"Current state: {state}")
        
        if state == "JOB_STATE_SUCCEEDED":
            logging.info("✅ Job succeeded!")
            
            if inline and job.dest and job.dest.inlined_responses:
                for inline_resp in job.dest.inlined_responses:
                    if inline_resp.response and inline_resp.response.text:
                        results.append(inline_resp.response.text)
            elif not inline and job.dest and job.dest.file_name:
                result_file_name = job.dest.file_name
                file_content = client.files.download(file=result_file_name)
                content = file_content.decode('utf-8')
                for line in content.splitlines():
                    result = json.loads(line)
                    text = result['response']['candidates'][0]['content']['parts'][0]['text']
                    results.append(text)
            
            break
        elif state in ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED"):
            raise RuntimeError(f"Batch job failed: {state} - {job.error.details}")
        else:
            time.sleep(10)
    
    return results

def get_user_input_with_timeout(timeout: int) -> str:
    sys.stdout.flush()
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        user_input = sys.stdin.readline().strip().lower()
        return user_input
    else:
        return ''  # No input within the timeout period
    
def upload_to_github(filepath, content):
    if not isinstance(content, str):
        content = json.dumps(content, indent=4, ensure_ascii=False)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error("GITHUB_TOKEN environment variable is not set!")
        raise ValueError("GITHUB_TOKEN not configured")
    
    logging.info(f"Attempting GitHub upload with token: {token[:8]}...{token[-4:] if len(token) > 12 else ''}")
    
    g = Github(token)
    repo = g.get_repo("sujeongim/real_human_interview")
    try:
        # Ensure filepath ends with .json
        if not filepath.endswith('.json'):
            filepath += '.json'
        
        # 파일이 이미 존재하는지 확인
        contents = None
        try:
            contents = repo.get_contents(filepath, ref="main")
        except Exception:
            pass  # 파일이 없으면 예외 발생 → create_file로 진행

        if contents is None:
            # 파일이 없으면 새로 생성
            repo.create_file(filepath, "Add new interview result", content, branch="main")
            logging.info(f"File created successfully at {filepath}!")
        else:
            # 파일이 있으면 업데이트(덮어쓰기)
            repo.update_file(filepath, "Update interview result", content, contents.sha, branch="main")
            logging.info(f"File updated successfully at {filepath}!")
    except Exception as e:
        logging.error(f"An error occurred while uploading {filepath}: {e}", exc_info=True)
        raise  # Re-raise the exception so caller knows upload failed
        
def download_from_github(filepath):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo("sujeongim/real_human_interview")
    try:
        # .json 확장자 자동 추가
        if not filepath.endswith('.json'):
            filepath += '.json'
        contents = repo.get_contents(filepath, ref="main")
        file_data = contents.decoded_content.decode('utf-8')
        print(f"File {filepath} downloaded successfully!")
        return file_data
    except Exception as e:
        print(f"An error occurred while downloading {filepath}: {e}")
        return None