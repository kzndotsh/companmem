# Empathy Dataset LLM - Evaluation Scripts

This repository contains scripts for generating and evaluating LLM-based empathy predictions from conversational data.

This is the official repository for the paper:
**"SENSE-7: Taxonomy and Dataset for Measuring User Perceptions of Empathy in Sustained Human-AI Conversations"**  
arXiv: [2509.16437](https://arxiv.org/abs/2509.16437)

## Overview

This repository provides tools to:
1. **Generate predictions**: Use LLMs to classify conversation empathy levels based on turn-level annotations
2. **Evaluate predictions**: Compute metrics and aggregate results across all files

## Repository Structure

```
repo/
├── sense-7_dataset.xlsx             # Dataset with Tasks and Messages sheets
├── generate_predictions.py          # Main script for generating predictions
├── evaluate_predictions.py          # Main script for evaluating predictions
├── helperOAI.py                     # OpenAI API helper functions
├── empathy_judge.txt                # Prompt template
├── requirements.txt                 # Python dependencies
├── dataset_card.pdf                 # Dataset card
└── README.md                        # This file
```

## Requirements

### Python Version
- Python 3.8 or higher

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scikit-learn`, `scipy`: Metrics and statistics
- `openai`: OpenAI API client
- `tqdm`: Progress bars
- `openpyxl` or `xlsxwriter`: Excel file support (for reading dataset and saving predictions)

### OpenAI API Setup

This code requires access to OpenAI API. Set up your API key:

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

2. Set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. Or edit `helperOAI.py` and set `OPENAI_API_KEY` directly in the configuration section


## Dataset

The dataset is provided in `sense-7_dataset.xlsx` with multiple sheets. The following two sheets are used for the classification analysis:

- **Tasks**: Contains a list of conversational task and pre-/post-conversation metadata
  - PID: Participant identifier
  - Model: LLM version used for AI assistant
  - TaskId: Unique conversation identifier
  - PreTaskChoice: Pre-task conversation topic choice
  - PreTaskImportance: Pre-task rating of importance of the conversation task (1 = Not at all important; 5 = Extremely important)
  - PreTaskDesiredEmpathy: Pre-task rating of desired empathy (1 = Minimal empathy; 3 = High empathy)
  - PostTaskExperience_Successful: Post-task rating of success in completing the task (1 = Strongly disagree; 5 = Strongly agree)
  - PostTaskExperience_Engaged: Post-task rating of being engaged in the conversation (1 = Strongly disagree; 5 = Strongly agree)
  - PostTaskExperience_PositiveInteraction: Post-task rating of having positive interaction with the AI (1 = Strongly disagree; 5 = Strongly agree)
  - PostTaskExperience_UseAgain: Post-task rating of willingness to use the AI agent again for task (1 = Strongly disagree; 5 = Strongly agree)
  - PostTaskEmpathy_*: Post-task ratings for 7 dimensions of empathy (1 = Strongly disagree; 5 = Strongly agree)

- **Messages**: Contains conversation turns with empathy annotations
  - MessageId: Order of the conversational turn
  - TimeOffsetSeconds: Number of seconds since the start of the conversation (i.e., participant input)
  - Role: user/assistant
  - Content: Message text
  - EmpathyOverall: Overall empathy rating per turn (1 = Very poor; 5 = Very good)
  - 7 dimension ratings per turn: Affective, Cognitive, Response, Prosocial, Interest, Contextual, Relational (1 = Very poor; 5 = Very good)

For a full description, see the [Dataset Card (PDF)](./dataset_card.pdf).

## Usage

### 1. Generate Predictions

Run the prediction generation script:

```bash
python generate_predictions.py
```

**Configuration**: Edit the `DEFAULT_CONFIG` dictionary at the top of `generate_predictions.py`:

```python
DEFAULT_CONFIG = {
    "prompt_file": "empathy_judge.txt",           # Prompt template
    "max_workers": 50,                            # Parallel workers
    "model": "gpt-4o",                            # Model name
    "session_name": "SENSE-7",                    # Results folder name
    "iterations": [1],                            # Iterations to run
}
```

**Running Multiple Iterations**: To run 10 iterations, set:
```python
"iterations": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
```

**Output**: Results are saved to `predictions_{session_name}/` folder:
- Each iteration creates a separate file with predictions
- Files named: `{model}-{prompt}-iter{N}.xlsx`

### 2. Evaluate Predictions

After generating predictions, run the evaluation script:

```bash
python evaluate_predictions.py
```

**Configuration**: Edit the `DEFAULT_CONFIG` dictionary at the top of `evaluate_predictions.py`:

```python
DEFAULT_CONFIG = {
    "session_name": "SENSE-7",                   # Must match generate_predictions
    "gt_column": "ground-truth",                 # Ground truth column
    "pred_column": "IS_EMPATHY",                 # Prediction column
}
```

**Output**: The script prints detailed metrics for each file and overall statistics:
- Individual file metrics: Accuracy, Macro F1, Within-1 Accuracy, MAE, Spearman correlation
- Overall statistics: Mean and standard deviation across all files

## Ground Truth Signals

The scripts compute the following ground truth signals from conversation annotations:

### ground-truth (Primary Signal)
For each assistant turn, averages the 7 empathy dimensions (Affective, Cognitive, Response, Prosocial, Interest, Contextual, Relational), then averages those per-turn scores across all assistant turns. This is a "turn-first" averaging approach that ensures balanced weighting across conversation turns.

**Computation**:
1. For each assistant turn, compute mean of 7 dimensions
2. Average the per-turn means across all assistant turns

This signal is used as the primary ground truth for evaluation.

## Evaluation Metrics

The evaluation script computes the following metrics:

### Classification Metrics (on rounded 1-5 labels)
- **Accuracy**: Overall correct predictions
- **Macro F1**: Average F1 score across classes
- **Within-1 Accuracy (W1-Acc)**: Percentage of predictions within ±1 of ground truth
- **Per-class Sensitivity/Specificity**: True positive and true negative rates per class

### Regression Metrics (on continuous values)
- **MAE (Mean Absolute Error)**: Average absolute difference
- **Spearman Correlation**: Rank correlation with p-value

## Results Aggregation

The evaluation script automatically processes all prediction files and prints aggregated metrics:
1. Computes metrics for each individual file
2. Calculates mean and standard deviation across all files
3. Prints results to console with:
   - Individual file metrics (Accuracy, Macro F1, Within-1 Accuracy, MAE, Spearman correlation)
   - Overall statistics showing mean ± std for each metric


## Customization

### Custom Prompt Templates

Create your own prompt template file (e.g., `my_prompt.txt`) and update:
```python
"prompt_file": "my_prompt.txt",
```

The template should include:
- `{chat}` placeholder for conversation JSON
- Clear instructions for empathy rating (1-5 scale)
- XML output format with `<S0>` (reasoning) and `<S2>` (score)

### Different Ground Truth Signals

To evaluate against a different ground truth column:
```python
"gt_column": "ground-truth",  # Primary ground truth signal
```


## Citation

If you use this code or dataset, please cite:

```bibtex
@misc{suh2025sense7taxonomydatasetmeasuring,
      title={SENSE-7: Taxonomy and Dataset for Measuring User Perceptions of Empathy in Sustained Human-AI Conversations}, 
      author={Jina Suh and Lindy Le and Erfan Shayegani and Gonzalo Ramos and Judith Amores and Desmond C. Ong and Mary Czerwinski and Javier Hernandez},
      year={2025},
      eprint={2509.16437},
      archivePrefix={arXiv},
      primaryClass={cs.HC},
      url={https://arxiv.org/abs/2509.16437}, 
}
```

## License

This project is licensed under the **Community Data License Agreement – Permissive, Version 2.0 (CDLA-P 2.0)**.  
See the [LICENSE.md](./LICENSE.md) file for the full text.

[![License: CDLA-Permissive-2.0](https://img.shields.io/badge/License-CDLA--P--2.0-blue.svg)](https://cdla.dev/permissive-2-0/)

## Privacy & Cookies

This project is subject to the [Microsoft Privacy Statement](https://go.microsoft.com/fwlink/?LinkId=521839).

## Contact

For questions or issues, please contact:
sense7data@microsoft.com

