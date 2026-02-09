#!/usr/bin/env python3
"""
Compare LLaMA3 NRP results with original LLM and SciUnit ground truth
Fixed version that properly handles package name normalization
"""

import json
import pandas as pd
from pathlib import Path

def normalize_package_name(name):
    """Normalize package names for comparison (handle - vs _)"""
    # Convert both hyphen and underscore to a common format for comparison
    return name.lower().replace('-', '_').replace('.', '_')

def compare_all_results():
    """Compare all analysis results"""
    print("\n📊 COMPREHENSIVE DEPENDENCY ANALYSIS COMPARISON")
    print("="*80)

    # Read the LLaMA3 results
    results_file = Path("results/llama3_nrp_analysis/analysis_results.json")
    with open(results_file, 'r') as f:
        llama3_results = json.load(f)

    # Read existing CSV with original results
    csv_path = "results/comparison_reports/clean_dependency_comparison.csv"
    if Path(csv_path).exists():
        df = pd.read_csv(csv_path)
    else:
        # If clean CSV doesn't exist, we need the original data
        # For now, return empty since we don't have the original CSV
        print("❌ No existing CSV found. Please ensure clean_dependency_comparison.csv exists.")
        return

    # Create a dictionary mapping script names to LLaMA3 dependencies
    llama3_deps_dict = {}
    for result in llama3_results:
        script_name = result['script'].replace('.py', '')  # Remove .py extension
        deps = set(result.get('dependencies', []))
        llama3_deps_dict[script_name] = deps

    # Calculate metrics for each script
    comparison_data = []

    for _, row in df.iterrows():
        script = row['script']

        # Parse SciUnit dependencies
        sciunit_deps_str = row['sciunit_dependencies']
        if pd.notna(sciunit_deps_str) and sciunit_deps_str:
            sciunit_deps_raw = set([d.strip() for d in str(sciunit_deps_str).split(',')])
            # Normalize for comparison but keep originals for display
            sciunit_deps_norm = set([normalize_package_name(d) for d in sciunit_deps_raw])
        else:
            sciunit_deps_raw = set()
            sciunit_deps_norm = set()

        # Parse original LLM dependencies
        llm_deps_str = row['llm_dependencies']
        if pd.notna(llm_deps_str) and llm_deps_str:
            llm_deps_raw = set([d.strip() for d in str(llm_deps_str).split(',')])
            llm_deps_norm = set([normalize_package_name(d) for d in llm_deps_raw])
        else:
            llm_deps_raw = set()
            llm_deps_norm = set()

        # Get LLaMA3 dependencies
        llama3_deps_raw = llama3_deps_dict.get(script, set())
        llama3_deps_norm = set([normalize_package_name(d) for d in llama3_deps_raw])

        # Calculate metrics for LLaMA3 using normalized names
        if sciunit_deps_norm:
            # True positives: normalized dependencies found by LLaMA3 that are in SciUnit
            llama3_tp = len(sciunit_deps_norm & llama3_deps_norm)
            # False positives: normalized dependencies found by LLaMA3 that are not in SciUnit
            llama3_fp = len(llama3_deps_norm - sciunit_deps_norm)
            # False negatives: normalized dependencies in SciUnit that LLaMA3 missed
            llama3_fn = len(sciunit_deps_norm - llama3_deps_norm)

            llama3_precision = llama3_tp / (llama3_tp + llama3_fp) if (llama3_tp + llama3_fp) > 0 else 0
            llama3_recall = llama3_tp / (llama3_tp + llama3_fn) if (llama3_tp + llama3_fn) > 0 else 0
            llama3_f1 = 2 * (llama3_precision * llama3_recall) / (llama3_precision + llama3_recall) if (llama3_precision + llama3_recall) > 0 else 0
        else:
            llama3_tp = llama3_fp = llama3_fn = 0
            llama3_precision = llama3_recall = llama3_f1 = 0

        comparison_data.append({
            'script': script,
            'sciunit_count': len(sciunit_deps_raw),
            'llm_count': len(llm_deps_raw),
            'llama3_count': len(llama3_deps_raw),
            'llm_recall': row['recall'],
            'llama3_recall': llama3_recall,
            'llm_precision': row['precision'],
            'llama3_precision': llama3_precision,
            'llm_f1': row['f1_score'],
            'llama3_f1': llama3_f1,
            'llama3_tp': llama3_tp,
            'llama3_fp': llama3_fp,
            'llama3_fn': llama3_fn
        })

    # Create comparison DataFrame
    comp_df = pd.DataFrame(comparison_data)

    # Calculate aggregate metrics
    print("\n📈 AGGREGATE METRICS COMPARISON")
    print("-"*60)

    print(f"\n📊 Average Dependencies Found:")
    print(f"  SciUnit (Ground Truth): {comp_df['sciunit_count'].mean():.1f}")
    print(f"  Original LLM:          {comp_df['llm_count'].mean():.1f}")
    print(f"  LLaMA3 NRP:            {comp_df['llama3_count'].mean():.1f}")

    print(f"\n📊 Average True Positives (correct dependencies found):")
    print(f"  Original LLM: {comp_df['llm_recall'].mean() * comp_df['sciunit_count'].mean():.1f}")
    print(f"  LLaMA3 NRP:   {comp_df['llama3_tp'].mean():.1f}")

    print(f"\n📊 Average Recall (how many real dependencies were found):")
    print(f"  Original LLM: {comp_df['llm_recall'].mean():.4f}")
    print(f"  LLaMA3 NRP:   {comp_df['llama3_recall'].mean():.4f}")
    print(f"  Improvement:  {((comp_df['llama3_recall'].mean() - comp_df['llm_recall'].mean()) / comp_df['llm_recall'].mean() * 100) if comp_df['llm_recall'].mean() > 0 else 0:.1f}%")

    print(f"\n📊 Average Precision (how many found dependencies were correct):")
    print(f"  Original LLM: {comp_df['llm_precision'].mean():.4f}")
    print(f"  LLaMA3 NRP:   {comp_df['llama3_precision'].mean():.4f}")

    print(f"\n📊 Average F1 Score (balanced metric):")
    print(f"  Original LLM: {comp_df['llm_f1'].mean():.4f}")
    print(f"  LLaMA3 NRP:   {comp_df['llama3_f1'].mean():.4f}")

    # Find best performing scripts
    print(f"\n🏆 TOP 5 SCRIPTS BY LLAMA3 RECALL:")
    print("-"*60)
    top_scripts = comp_df.nlargest(5, 'llama3_recall')
    for _, row in top_scripts.iterrows():
        print(f"  {row['script']:12} - Recall: {row['llama3_recall']:.2f}, True Positives: {row['llama3_tp']:.0f}/{row['sciunit_count']:.0f} (Found {row['llama3_count']:.0f} total)")

    # Find scripts with biggest improvement
    comp_df['recall_improvement'] = comp_df['llama3_recall'] - comp_df['llm_recall']
    print(f"\n📈 TOP 5 MOST IMPROVED SCRIPTS:")
    print("-"*60)
    improved_scripts = comp_df.nlargest(5, 'recall_improvement')
    for _, row in improved_scripts.iterrows():
        print(f"  {row['script']:12} - Recall improved from {row['llm_recall']:.2f} to {row['llama3_recall']:.2f} (+{row['recall_improvement']:.2f})")

    # Show distribution of improvements
    print(f"\n📊 IMPROVEMENT DISTRIBUTION:")
    print("-"*60)
    improved_count = len(comp_df[comp_df['recall_improvement'] > 0])
    same_count = len(comp_df[comp_df['recall_improvement'] == 0])
    worse_count = len(comp_df[comp_df['recall_improvement'] < 0])

    print(f"  Scripts with improved recall: {improved_count} ({improved_count/len(comp_df)*100:.1f}%)")
    print(f"  Scripts with same recall:     {same_count} ({same_count/len(comp_df)*100:.1f}%)")
    print(f"  Scripts with worse recall:    {worse_count} ({worse_count/len(comp_df)*100:.1f}%)")

    # Create clean CSV with better structure
    create_clean_csv(df, llama3_deps_dict)

    return comp_df

def create_clean_csv(df_original, llama3_deps_dict, hybrid_deps_dict=None):
    """Create a clean, well-structured CSV with all results including hybrid"""
    clean_data = []

    for _, row in df_original.iterrows():
        script = row['script']

        # Parse SciUnit dependencies (Ground Truth)
        sciunit_deps_str = row['sciunit_dependencies']
        if pd.notna(sciunit_deps_str) and sciunit_deps_str:
            sciunit_deps = set([d.strip() for d in str(sciunit_deps_str).split(',')])
            sciunit_deps_norm = set([normalize_package_name(d) for d in sciunit_deps])
        else:
            sciunit_deps = set()
            sciunit_deps_norm = set()

        # Parse original LLM dependencies
        llm_deps_str = row['llm_dependencies']
        if pd.notna(llm_deps_str) and llm_deps_str:
            llm_deps = set([d.strip() for d in str(llm_deps_str).split(',')])
            llm_deps_norm = set([normalize_package_name(d) for d in llm_deps])
        else:
            llm_deps = set()
            llm_deps_norm = set()

        # Get LLaMA3 dependencies
        llama3_deps = llama3_deps_dict.get(script, set())
        llama3_deps_norm = set([normalize_package_name(d) for d in llama3_deps])

        # Get Hybrid dependencies if available
        hybrid_deps = hybrid_deps_dict.get(script, set()) if hybrid_deps_dict else set()
        hybrid_deps_norm = set([normalize_package_name(d) for d in hybrid_deps])

        # Calculate intersections using normalized names
        llm_tp_norm = sciunit_deps_norm & llm_deps_norm
        llama3_tp_norm = sciunit_deps_norm & llama3_deps_norm

        # Find which original dependencies match the normalized true positives
        llm_true_positives = set()
        for dep in llm_deps:
            if normalize_package_name(dep) in llm_tp_norm:
                llm_true_positives.add(dep)

        llama3_true_positives = set()
        for dep in llama3_deps:
            if normalize_package_name(dep) in llama3_tp_norm:
                llama3_true_positives.add(dep)

        # Calculate unique dependencies
        only_sciunit = sciunit_deps - llm_deps - llama3_deps
        only_llm = llm_deps - sciunit_deps - llama3_deps
        only_llama3 = llama3_deps - sciunit_deps - llm_deps
        llm_and_llama3_only = (llm_deps & llama3_deps) - sciunit_deps

        # Calculate metrics with FP and FN
        llm_tp_count = len(llm_tp_norm)
        llm_fp_count = len(llm_deps_norm - sciunit_deps_norm)  # False positives: found but not in ground truth
        llm_fn_count = len(sciunit_deps_norm - llm_deps_norm)  # False negatives: missed from ground truth
        llm_precision = llm_tp_count / len(llm_deps_norm) if len(llm_deps_norm) > 0 else 0
        llm_recall = llm_tp_count / len(sciunit_deps_norm) if len(sciunit_deps_norm) > 0 else 0
        llm_f1 = 2 * (llm_precision * llm_recall) / (llm_precision + llm_recall) if (llm_precision + llm_recall) > 0 else 0

        llama3_tp_count = len(llama3_tp_norm)
        llama3_fp_count = len(llama3_deps_norm - sciunit_deps_norm)  # False positives
        llama3_fn_count = len(sciunit_deps_norm - llama3_deps_norm)  # False negatives
        llama3_precision = llama3_tp_count / len(llama3_deps_norm) if len(llama3_deps_norm) > 0 else 0
        llama3_recall = llama3_tp_count / len(sciunit_deps_norm) if len(sciunit_deps_norm) > 0 else 0
        llama3_f1 = 2 * (llama3_precision * llama3_recall) / (llama3_precision + llama3_recall) if (llama3_precision + llama3_recall) > 0 else 0

        # Calculate hybrid metrics if available
        if hybrid_deps:
            hybrid_tp_norm = sciunit_deps_norm & hybrid_deps_norm
            hybrid_tp_count = len(hybrid_tp_norm)
            hybrid_fp_count = len(hybrid_deps_norm - sciunit_deps_norm)
            hybrid_fn_count = len(sciunit_deps_norm - hybrid_deps_norm)
            hybrid_precision = hybrid_tp_count / len(hybrid_deps_norm) if len(hybrid_deps_norm) > 0 else 0
            hybrid_recall = hybrid_tp_count / len(sciunit_deps_norm) if len(sciunit_deps_norm) > 0 else 0
            hybrid_f1 = 2 * (hybrid_precision * hybrid_recall) / (hybrid_precision + hybrid_recall) if (hybrid_precision + hybrid_recall) > 0 else 0
        else:
            hybrid_tp_count = hybrid_fp_count = hybrid_fn_count = 0
            hybrid_precision = hybrid_recall = hybrid_f1 = 0

        data_row = {
            'script': script,
            'sciunit_count': len(sciunit_deps),
            'llm_count': len(llm_deps),
            'llama3_count': len(llama3_deps),
            'hybrid_count': len(hybrid_deps) if hybrid_deps else 0,
            'sciunit_dependencies': ', '.join(sorted(sciunit_deps)),
            'llm_dependencies': ', '.join(sorted(llm_deps)),
            'llama3_dependencies': ', '.join(sorted(llama3_deps)),
            'hybrid_dependencies': ', '.join(sorted(hybrid_deps)) if hybrid_deps else '',
            'llm_true_positives': ', '.join(sorted(llm_true_positives)),
            'llama3_true_positives': ', '.join(sorted(llama3_true_positives)),
            'only_sciunit': ', '.join(sorted(only_sciunit)),
            'only_llm': ', '.join(sorted(only_llm)),
            'only_llama3': ', '.join(sorted(only_llama3)),
            'llm_tp_count': llm_tp_count,
            'llm_fp_count': llm_fp_count,
            'llm_fn_count': llm_fn_count,
            'llm_precision': round(llm_precision, 4),
            'llm_recall': round(llm_recall, 4),
            'llm_f1': round(llm_f1, 4),
            'llama3_tp_count': llama3_tp_count,
            'llama3_fp_count': llama3_fp_count,
            'llama3_fn_count': llama3_fn_count,
            'llama3_precision': round(llama3_precision, 4),
            'llama3_recall': round(llama3_recall, 4),
            'llama3_f1': round(llama3_f1, 4),
            'hybrid_tp_count': hybrid_tp_count,
            'hybrid_fp_count': hybrid_fp_count,
            'hybrid_fn_count': hybrid_fn_count,
            'hybrid_precision': round(hybrid_precision, 4),
            'hybrid_recall': round(hybrid_recall, 4),
            'hybrid_f1': round(hybrid_f1, 4)
        }
        clean_data.append(data_row)

    # Save clean CSV
    df_clean = pd.DataFrame(clean_data)
    df_clean.to_csv("results/comparison_reports/clean_dependency_comparison.csv", index=False)
    print(f"\n💾 Clean CSV saved to: results/comparison_reports/clean_dependency_comparison.csv")

    # Save summary metrics
    summary = {
        'metric': ['Dependencies Found', 'True Positives', 'False Positives', 'False Negatives', 'Precision', 'Recall', 'F1 Score'],
        'sciunit': [
            df_clean['sciunit_count'].mean(),
            df_clean['sciunit_count'].mean(),
            0.0,  # SciUnit has no false positives
            0.0,  # SciUnit has no false negatives
            1.000,
            1.000,
            1.000
        ],
        'original_llm': [
            df_clean['llm_count'].mean(),
            df_clean['llm_tp_count'].mean(),
            df_clean['llm_fp_count'].mean(),
            df_clean['llm_fn_count'].mean(),
            df_clean['llm_precision'].mean(),
            df_clean['llm_recall'].mean(),
            df_clean['llm_f1'].mean()
        ],
        'llama3_nrp': [
            df_clean['llama3_count'].mean(),
            df_clean['llama3_tp_count'].mean(),
            df_clean['llama3_fp_count'].mean(),
            df_clean['llama3_fn_count'].mean(),
            df_clean['llama3_precision'].mean(),
            df_clean['llama3_recall'].mean(),
            df_clean['llama3_f1'].mean()
        ]
    }

    df_summary = pd.DataFrame(summary)
    df_summary.to_csv('results/comparison_reports/summary_metrics.csv', index=False)
    print(f"📊 Summary metrics saved to: results/comparison_reports/summary_metrics.csv")

if __name__ == "__main__":
    compare_all_results()