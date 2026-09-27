#!/usr/bin/env python3
"""
Empathy Prediction Evaluation Script

This script evaluates empathy predictions by:
1. Computing classification and regression metrics for each file
2. Aggregating results across all files with mean and standard deviation
3. Printing detailed statistics to console

Metrics Computed:
- Accuracy, Macro F1, Within-1 Accuracy
- MAE (Mean Absolute Error)
- Spearman correlation and p-value

Output:
- Prints metrics for each evaluated file
- Prints overall statistics with mean ± standard deviation across all files

"""

############# DEFAULT CONFIGURATION ###################
DEFAULT_CONFIG = {
    "session_name": "SENSE-7",  # Session name (matches generate_predictions.py)
    "gt_column": "ground-truth",  # Ground truth column to evaluate
    "pred_column": "IS_EMPATHY",  # Prediction column name
}
######################################################

import os
import glob
import numpy as np
import pandas as pd

try:
    from sklearn.metrics import f1_score, accuracy_score
    from scipy.stats import spearmanr
    SKLEARN_AVAILABLE = True
except:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Some metrics will not be computed.")


def load_predictions_file(file_path):
    """Load a predictions file (CSV or XLSX)"""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, engine='openpyxl')
        else:
            print(f"Unsupported file format: {ext}")
            return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def prepare_labels(df, gt_col, pred_col):
    """Prepare ground truth and prediction labels for evaluation"""
    # Convert to numeric and round to integers
    gt_numeric = pd.to_numeric(df[gt_col], errors='coerce')
    pred_numeric = pd.to_numeric(df[pred_col], errors='coerce')
    
    # Round to nearest integer and clip to 1-5
    gt_rounded = gt_numeric.round().clip(1, 5)
    pred_rounded = pred_numeric.round().clip(1, 5)
    
    # Keep only valid rows
    valid_mask = gt_rounded.notna() & pred_rounded.notna()
    gt_valid = gt_rounded[valid_mask].astype(int).astype(str)
    pred_valid = pred_rounded[valid_mask].astype(int).astype(str)
    
    # Get unique classes from both GT and predictions
    classes = sorted(set(gt_valid.unique()) | set(pred_valid.unique()))
    
    return gt_valid.tolist(), pred_valid.tolist(), classes


def compute_file_metrics(y_true, y_pred, classes, gt_numeric, pred_numeric):
    """Compute overall file-level metrics"""
    metrics = {}
    
    # Classification metrics
    if SKLEARN_AVAILABLE:
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['macro_f1'] = f1_score(y_true, y_pred, labels=classes, average='macro', zero_division=0)
        
        # Within-1 accuracy
        y_true_int = np.array([int(y) for y in y_true])
        y_pred_int = np.array([int(y) for y in y_pred])
        within_1 = np.abs(y_true_int - y_pred_int) <= 1
        metrics['w1_acc'] = np.mean(within_1)
    
    # Regression metrics (from continuous values)
    valid_mask = gt_numeric.notna() & pred_numeric.notna()
    if valid_mask.sum() >= 2:
        gt_vals = gt_numeric[valid_mask].values
        pred_vals = pred_numeric[valid_mask].values
        
        metrics['mae'] = float(np.mean(np.abs(pred_vals - gt_vals)))
        
        # Correlation
        try:
            spearman_r, spearman_p = spearmanr(gt_vals, pred_vals)
            metrics['spearman_correlation'] = spearman_r
            metrics['spearman_p_value'] = spearman_p
        except:
            pass
    
    return metrics


def evaluate_single_file(file_path, gt_col, pred_col):
    """Evaluate a single prediction file"""
    print(f"\nEvaluating: {os.path.basename(file_path)}")
    
    df = load_predictions_file(file_path)
    if df is None:
        return None
    
    # Check columns exist
    if gt_col not in df.columns or pred_col not in df.columns:
        print(f"  Skipping: missing {gt_col} or {pred_col}")
        return None
    
    # Prepare labels
    y_true, y_pred, classes = prepare_labels(df, gt_col, pred_col)
    
    if len(y_true) == 0:
        print("  Skipping: no valid rows")
        return None
    
    print(f"  Valid samples: {len(y_true)}, Classes: {classes}")
    
    # Get original numeric values for regression metrics
    gt_numeric = pd.to_numeric(df[gt_col], errors='coerce')
    pred_numeric = pd.to_numeric(df[pred_col], errors='coerce')
    
    # Compute metrics
    file_metrics = compute_file_metrics(y_true, y_pred, classes, gt_numeric, pred_numeric)
    
    # Print summary with all metrics
    print(f"  Accuracy:              {file_metrics.get('accuracy', 0):.4f}")
    print(f"  Macro F1:              {file_metrics.get('macro_f1', 0):.4f}")
    print(f"  Within-1 Accuracy:     {file_metrics.get('w1_acc', 0):.4f}")
    print(f"  MAE:                   {file_metrics.get('mae', 0):.4f}")
    if 'spearman_correlation' in file_metrics:
        print(f"  Spearman Correlation:  {file_metrics.get('spearman_correlation', 0):.4f}")
    if 'spearman_p_value' in file_metrics:
        print(f"  Spearman p-value:      {file_metrics.get('spearman_p_value', 0):.4f}")
    
    # Add filename to metrics
    file_metrics['filename'] = os.path.splitext(os.path.basename(file_path))[0]
    
    return file_metrics


def print_overall_statistics(all_results):
    """Print overall statistics across all files"""
    print("\n" + "="*60)
    print("OVERALL STATISTICS ACROSS ALL FILES")
    print("="*60)
    
    if not all_results:
        print("No results to display")
        return
    
    # Create DataFrame with all individual file results
    results_df = pd.DataFrame(all_results)
    
    # Move filename column to first position
    cols = ['filename'] + [col for col in results_df.columns if col != 'filename']
    results_df = results_df[cols]
    
    total_files = len(results_df)
    print(f"Total files: {total_files}")
    print(f"\nMetric Averages (±Std Dev):")
    
    # Compute statistics for numeric columns
    for col in results_df.columns:
        if col != 'filename' and pd.api.types.is_numeric_dtype(results_df[col]):
            mean_val = results_df[col].mean()
            std_val = results_df[col].std()
            
            print(f"  {col:25s}: {mean_val:.4f} (±{std_val:.4f})")
    
    print("="*60)




def main():
    """Main evaluation function"""
    print("="*60)
    print("EMPATHY PREDICTION EVALUATION")
    print("="*60)
    print(f"Configuration:")
    for key, value in DEFAULT_CONFIG.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    config = DEFAULT_CONFIG
    # Use script directory as base to ensure results are always saved in repo folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, f"predictions_{config['session_name']}")
    metrics_dir = os.path.join(results_dir, "results")
    
    # Create metrics directory
    os.makedirs(metrics_dir, exist_ok=True)
    
    # Find all prediction files
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    xlsx_files = glob.glob(os.path.join(results_dir, "*.xlsx"))
    all_files = csv_files + xlsx_files
    
    # Filter out metrics files
    prediction_files = [f for f in all_files if not f.endswith('_metrics.csv') and 'results' not in f]
    
    if not prediction_files:
        print(f"\nNo prediction files found in {results_dir}")
        return
    
    print(f"\nFound {len(prediction_files)} prediction files")
    
    # Evaluate each file
    results = []
    for file_path in sorted(prediction_files):
        result = evaluate_single_file(
            file_path,
            config['gt_column'],
            config['pred_column']
        )
        if result:
            results.append(result)
    
    print(f"\nSuccessfully evaluated {len(results)}/{len(prediction_files)} files")
    
    # Print overall statistics
    if results:
        print_overall_statistics(results)
    

if __name__ == "__main__":
    main()
