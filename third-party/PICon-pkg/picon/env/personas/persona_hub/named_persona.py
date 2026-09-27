import json
import random
import torch
from torch.utils.data import Subset
from openai import OpenAI
from dotenv import load_dotenv
import litellm
from datasets import load_dataset
from picon.utils import get_completion
load_dotenv()

def generate_named_persona_data(persona_text):
    """
    LLM으로부터 이름과 문장이 포함된 JSON 구조를 응답받습니다.
    """
    prompt = (
        f"Based on the following persona description, assign a natural human name. "
        f"Return the result in JSON format with keys 'name' and 'persona'.\n\n"
        "DO NOT change the persona description.\n\n"
        f"Original Persona: {persona_text}\n"
        f"Example Output: {{\"name\": \"Anny\", \"persona\": \"Anny is a Political Analyst...\"}}"
    )

    try:
        response = get_completion(
            model="gpt-5.1", # 또는 'gpt-5.1' (사용 가능한 경우)
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }, # JSON 모드 활성화
            temperature=0.8
        )
        # 응답 문자열을 파이썬 딕셔너리로 변환
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error processing: {e}")
        return {"name": "Unknown", "persona": persona_text}

# 2. 데이터 샘플링
dataset =  load_dataset("proj-persona/PersonaHub", "persona", split="train")
total_indices = list(range(len(dataset)))
random_indices = random.sample(total_indices, 200)

save_path = "./named_personas_with_key.jsonl"

# 3. 파일 저장
print(f"작업 시작... 저장 위치: {save_path}")

with open(save_path, 'w', encoding='utf-8') as f:
    for i, idx in enumerate(random_indices):
        original_persona = dataset[idx]['persona']
        
        # 이름과 문장 데이터 생성
        result_data = generate_named_persona_data(original_persona)
        
        # JSONL 형식으로 저장
        f.write(json.dumps(result_data, ensure_ascii=False) + '\n')
        
        if (i + 1) % 10 == 0:
            print(f"진행도: {i + 1}/200 완료")

print("모든 저장이 완료되었습니다.")