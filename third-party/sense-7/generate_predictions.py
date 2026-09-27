#!/usr/bin/env python3
"""
Empathy Prediction Generation Script

This script generates empathy predictions for conversations using LLM-based classification.
It computes ground truth signals based on conversation turn annotations.

Ground Truth Signals:
- ground-truth: For each assistant turn, averages the 7 empathy dimensions,
  then averages those per-turn scores across all assistant turns.

Features:
- Parallel processing for efficiency
- Configurable iteration support for repeated experiments
- Standard OpenAI API integration (via helperOAI.py)

API Configuration:
- Set OPENAI_API_KEY environment variable or edit helperOAI.py
- Adjust model, temperature, and other parameters in helperOAI.py configuration section

"""

############# DEFAULT CONFIGURATION ###################
# Set default parameters here to run without command line arguments
DEFAULT_CONFIG = {
    "prompt_file": "empathy_judge.txt",  # Path to the prompt template file
    "max_workers": 1,  # Number of parallel workers for API calls
    "model": "gpt-4o",  # Model to use for empathy classification
    "session_name": "SENSE-7",  # Session name for results folder
    "iterations": [6],  # List of iterations to run, e.g., [1,2,3,4,5,6,7,8,9,10] for 10 iterations
}
######################################################

import time
import os
import pandas as pd
import json
import re
import concurrent.futures
from datetime import datetime
from tqdm import tqdm

# API client imports
from helperOAI import customCompletion, create_client

import importlib.util
import tempfile
import shutil

# Constants for empathy evaluation
EMPATHY_DIMENSIONS = ['Affective', 'Cognitive', 'Response', 'Prosocial', 'Interest', 'Contextual', 'Relational']
RATING_TO_NUMERIC = {
    'very good': 5,
    'good': 4,
    'neutral': 3,
    'poor': 2,
    'very poor': 1,
    'unknown': None,  # Skip unknown values
}


def parse_empathy_response(response_string: str):
    """
    Parse the model response to extract ThoughtChain (CoT) and empathy score (1-5).
    Returns (cot, empathy_score) where empathy_score is a string.
    """
    if response_string is None:
        return "", "3"

    s = str(response_string).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    if (s.startswith('```') and s.endswith('```')):
        s = s[3:-3].strip()

    cot = ""
    empathy_score = "3"

    try:
        s0_match = re.search(r'<S0>(.*?)</S0>', s, re.DOTALL | re.IGNORECASE)
        if s0_match:
            cot = s0_match.group(1).strip()

        s2_match = re.search(r'<S2>(.*?)</S2>', s, re.DOTALL | re.IGNORECASE)
        if s2_match:
            score_text = s2_match.group(1).strip()
            score_match = re.search(r'([1-5](?:\.\d+)?)', score_text)
            if score_match:
                empathy_score = score_match.group(1)
    except Exception as e:
        print(f"Warning: XML parsing failed: {e}")

    if not re.fullmatch(r"[1-5](?:\.\d+)?", str(empathy_score)):
        empathy_score = "3"

    return cot, empathy_score


def compute_ground_truth(chat_data):
    """
    Compute ground-truth:
    1) For each assistant turn, average the available 7D dimension scores
    2) Then average those per-turn averages across assistant turns
    """
    import numpy as np

    try:
        roles = chat_data.get('Role', [])
        if not roles:
            return np.nan

        per_turn_means = []
        skipped_values = set()

        for i, role in enumerate(roles):
            if role != 'assistant':
                continue

            per_turn_scores = []
            for dim in EMPATHY_DIMENSIONS:
                dim_values = chat_data.get(dim, [])
                if i < len(dim_values):
                    value = dim_values[i]
                    if pd.isna(value) or value is None or str(value).lower() == 'nan':
                        continue
                    
                    value_lower = str(value).lower().strip()
                    numeric_value = RATING_TO_NUMERIC.get(value_lower)
                    
                    if numeric_value is not None:
                        per_turn_scores.append(numeric_value)
                    elif value_lower != 'unknown':
                        # Track unexpected values for debugging
                        skipped_values.add(value_lower)

            if per_turn_scores:
                per_turn_means.append(np.mean(per_turn_scores))

        if skipped_values:
            print(f"Warning: Skipped unrecognized empathy values: {skipped_values}")

        if per_turn_means:
            return np.mean(per_turn_means)
        else:
            return np.nan

    except Exception as e:
        print(f"Warning: Error computing ground-truth: {e}")
        return np.nan


def clean_text_for_excel(text):
    """Clean text fields for Excel safety"""
    if text is None:
        return ""
    s = str(text)
    if s[:1] in ("=", "+", "-", "@"):
        s = "'" + s
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    return s


def sanitize_filename(name: str, max_len: int = 150) -> str:
    """Sanitize filename for safe writing"""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", str(name))
    name = re.sub(r"\s+", " ", name).strip().rstrip(" .")
    return name[:max_len]


def safe_write_results(df: pd.DataFrame, base_dir: str, base_name: str) -> str:
    """Write DataFrame to XLSX if engine available; else CSV"""
    os.makedirs(base_dir, exist_ok=True)
    xlsx_path = os.path.join(base_dir, base_name + ".xlsx")
    csv_path = os.path.join(base_dir, base_name + ".csv")

    has_openpyxl = importlib.util.find_spec("openpyxl") is not None
    has_xlsxwriter = importlib.util.find_spec("xlsxwriter") is not None

    if has_openpyxl or has_xlsxwriter:
        engine = "openpyxl" if has_openpyxl else "xlsxwriter"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp_path = tmp.name
        try:
            with pd.ExcelWriter(tmp_path, engine=engine) as writer:
                df.to_excel(writer, index=False, sheet_name="results")
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
            shutil.move(tmp_path, xlsx_path)
            print(f"Saved results to: {xlsx_path}")
            return xlsx_path
        except Exception as e:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            print(f"Error saving XLSX: {e}; falling back to CSV.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="") as tmpf:
        df.to_csv(tmpf, index=False)
        tmp_fpath = tmpf.name
    if os.path.exists(csv_path):
        os.remove(csv_path)
    shutil.move(tmp_fpath, csv_path)
    print(f"Saved results to: {csv_path}")
    return csv_path


def create_chat(index, data):
    """Create chat list from message data"""
    message_data = data['Messages'][index]
    
    if isinstance(message_data, str):
        try:
            chat = json.loads(message_data)
            return chat
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Warning: Failed to parse JSON for index {index}: {e}")
            return []
    
    if isinstance(message_data, dict) and 'Role' in message_data and 'Content' in message_data:
        role = message_data['Role']
        content = message_data['Content']
        chat = []
        for r, message in zip(role, content):
            if r == 'error':
                continue
            chat.append({"role": r, "content": message})
        return chat
    
    print(f"Warning: Unexpected message format for index {index}: {type(message_data)}")
    return []


def process_single_conversation(params):
    """Process a single conversation for empathy classification"""
    try:
        idx, data, prompt_template, model, client = params
        
        if idx >= len(data['Messages']):
            raise IndexError(f"Index {idx} out of bounds")
        
        chat_list = create_chat(idx, data)
        
        # Format chat as JSON
        json_messages = []
        for msg in chat_list:
            role = msg["role"].lower()
            content = str(msg["content"]).replace('\n', ' ').replace('\r', ' ').strip()
            content = ' '.join(content.split())
            json_messages.append({"role": role, "content": content})
        
        chat_formatted = json.dumps(json_messages, separators=(',', ':'), ensure_ascii=False)
        
        # Create prompt
        user_input = prompt_template.replace("{chat}", chat_formatted)
        user_input = user_input.replace("~~EXAMPLES~~", "")
        
        api_start = time.time()
        response_string, reqtime, logprobs = customCompletion(
            model, user_input, api_start, client=client
        )
        
        cot, empathy_score = parse_empathy_response(response_string)
        
        # DEBUG: Print raw response for debugging
        print(f"\n{'='*60}")
        print(f"Index: {idx} - Took {reqtime:.2f}s - Score: {empathy_score}")
        print(f"Raw Response:\n{response_string}")
        print(f"{'='*60}\n")
        
        return idx, cot, empathy_score, reqtime, user_input, response_string, model, chat_formatted
        
    except Exception as e:
        error_msg = f"Error processing conversation {idx}: {e}"
        print(error_msg)
        return idx, error_msg, "PROCESSING_FAILED", 0.0, "", "", model, ""


def run_single_iteration(iteration, config):
    """Run a single iteration of prediction generation"""
    print(f"\n{'='*60}")
    print(f"Starting Iteration {iteration}")
    print(f"{'='*60}\n")
    
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Session: {config['session_name']}, Iteration: {iteration}")

    # Use script directory as base to ensure data is loaded from repo folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load data from Excel file
    excel_file_path = os.path.join(script_dir, 'sense-7_dataset.xlsx')
    print(f"Loading data from {excel_file_path}...")
    df_tasks = pd.read_excel(excel_file_path, sheet_name='Tasks')
    df_messages = pd.read_excel(excel_file_path, sheet_name='Messages')
    df_messages["Content"] = df_messages["Content"].fillna("pending")
    
    data = df_tasks.to_dict(orient='list')
    
    messages = []
    for taskid in data['TaskId']:
        df_messages_taskid = df_messages[df_messages['TaskId'] == taskid]
        df_messages_taskid = df_messages_taskid[['Role', 'Content', 'Retry', 
                'EmpathyOverall', 'Affective', 'Cognitive', 'Response', 'Prosocial',
                'Interest', 'Contextual', 'Relational', 'Comment']]
        messages.append(df_messages_taskid.to_dict(orient='list'))
    
    data['Messages'] = messages
    print("Data loaded successfully")
    

    # Load prompt template
    prompt_file_path = os.path.join(script_dir, config["prompt_file"])
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # Pre-compute GT for all conversations
    print("Pre-computing ground-truth...")
    print("=" * 60)
    gt_scores = []
    empty_count = 0
    empty_indices = []
    all_unrecognized_values = set()  # Track all unrecognized values across dataset
    
    for idx, chat_data in enumerate(data['Messages']):
        score = compute_ground_truth(chat_data)
        gt_scores.append(score)
        
        # Check if score is NaN/empty
        if pd.isna(score):
            empty_count += 1
            empty_indices.append(idx)
    
    data['ground-truth'] = gt_scores
    
    print("=" * 60)
    print(f"Pre-computed GT for {len(gt_scores)} conversations")
    print(f"Empty/NaN ground-truth values: {empty_count} ({empty_count/len(gt_scores)*100:.1f}%)")
    if empty_count > 0:
        print(f"Empty indices (first 20): {empty_indices[:20]}")
    
    if all_unrecognized_values:
        print(f"\n⚠️  UNRECOGNIZED EMPATHY VALUES FOUND:")
        for val in sorted(all_unrecognized_values):
            print(f"  - {val}")
        print(f"Total unrecognized values: {len(all_unrecognized_values)}")
    else:
        print(f"\n✓ All empathy values recognized (valid scale: very poor, poor, neutral, good, very good)")
    print("=" * 60)

    # Create API client
    client = create_client(config["model"])

    # Prepare parameters for parallel processing
    params = [(idx, data, prompt_template, config["model"], client) 
              for idx in range(len(data['Messages']))]
    
    # Process conversations in parallel
    print(f"Processing {len(params)} conversations with {config['max_workers']} workers...")
    results = [None] * len(params)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        futures = [executor.submit(process_single_conversation, param) for param in params]
        
        with tqdm(total=len(futures), desc=f"Iteration {iteration}", unit="conv") as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        idx = result[0]
                        results[idx] = result
                except Exception as e:
                    print(f"Error in future: {e}")
                finally:
                    pbar.update(1)
    
    # Extract results
    COT, IS_EMPATHY, PROMPTS, RAW_OUTPUTS = [], [], [], []
    PROCESSING_TIMES, MODELS, ONLY_CHAT = [], [], []
    
    for idx, result in enumerate(results):
        if result is not None:
            _, cot, empathy, reqtime, prompt, output, model, chat = result
            COT.append(cot)
            IS_EMPATHY.append(empathy)
            PROMPTS.append(prompt)
            RAW_OUTPUTS.append(output)
            PROCESSING_TIMES.append(round(reqtime*100)/100)
            MODELS.append(model)
            ONLY_CHAT.append(chat)
        else:
            COT.append("PROCESSING_FAILED")
            IS_EMPATHY.append("PROCESSING_FAILED")
            PROMPTS.append("")
            RAW_OUTPUTS.append("")
            PROCESSING_TIMES.append(0.0)
            MODELS.append(config["model"])
            ONLY_CHAT.append("")

    # Create results DataFrame
    df_save = pd.DataFrame()
    df_save["CoT"] = COT
    df_save["TaskId"] = df_tasks["TaskId"].astype(str).tolist()
    df_save["PID"] = df_tasks["PID"].tolist()
    df_save["IS_EMPATHY"] = IS_EMPATHY
    df_save["Chat"] = data['Messages']
    df_save["OnlyChat"] = [clean_text_for_excel(chat) for chat in ONLY_CHAT]
    df_save["Prompt"] = [clean_text_for_excel(p) for p in PROMPTS]
    df_save["Output"] = [clean_text_for_excel(o) for o in RAW_OUTPUTS]
    df_save["Processing Time"] = PROCESSING_TIMES
    df_save["Model"] = MODELS
    df_save["ground-truth"] = gt_scores
    df_save = df_save.replace('', "EMPTY")

    # Save results
    prompt_file_name = config["prompt_file"].replace('.txt', '').replace('.', '_')
    settings = f"{config['model']}-{prompt_file_name}-iter{iteration}"
    base_name = sanitize_filename(settings)
    # Use script directory as base to ensure results are saved in repo folder
    results_dir = os.path.join(script_dir, f"predictions_{config['session_name']}")
    safe_write_results(df_save, results_dir, base_name)

    end_time = datetime.now()
    total_duration = end_time - start_time
    print(f"\nIteration {iteration} completed in {total_duration.total_seconds()/60:.2f} minutes")


def main():
    """Main function to run prediction generation"""
    print("="*60)
    print("Empathy Prediction Generation")
    print("="*60)
    print(f"Configuration:")
    for key, value in DEFAULT_CONFIG.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    # Run all iterations
    for iteration in DEFAULT_CONFIG["iterations"]:
        run_single_iteration(iteration, DEFAULT_CONFIG)
    
    print("\n" + "="*60)
    print("All iterations completed!")
    print("="*60)


if __name__ == "__main__":
    main()
