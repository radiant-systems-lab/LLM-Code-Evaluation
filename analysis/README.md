# Analysis

All analysis scripts and outputs. Run `python regenerate_all.py` to reproduce.

## Script

**`regenerate_all.py`** reads the 9 raw CSVs from `../data/raw_csvs/` and generates all figures, tables, and key statistics. No other scripts are needed.

```bash
pip install pandas numpy matplotlib
python regenerate_all.py
```

## Figures

| File | Description | Paper Reference |
|------|-------------|-----------------|
| `figure1_success_heatmap` | Agent x Language success rate heatmap | Figure 1 |
| `figure2_language_comparison` | Grouped bar chart: success rates by language | Figure 2 |
| `figure3_agent_distribution` | Pie charts: success/partial/failed per agent | Figure 3 |
| `figure4_dependency_gaps` | Bar chart: % projects with missing dependencies | Figure 4 |
| `figure5_runtime_explosion` | Claimed vs runtime dependencies + multiplier | Figure 5 |
| `figure6_error_distribution` | Stacked bar: error types by agent | Figure 6 |

Each figure is generated in both PNG (300 DPI) and PDF format.

## Tables

| File | Description | Paper Reference |
|------|-------------|-----------------|
| `table1_agent_summary.csv` | Per-agent success/partial/failed counts | Table 1 |
| `table2_language_summary.csv` | Per-language success rates | Table 2 |
| `table3_agent_language.csv` | Agent x Language breakdown | Table 3 |
| `table4_completeness_gaps.csv` | Missing dependency counts per agent x language | Table 4 |
| `table5_error_classification.csv` | Error type distribution (6 categories) | Table 5 |
| `table6_overall_summary.csv` | Overall study metrics | Table 6 |
