"""Regenerate all figures and tables from updated raw CSVs.

Fixes applied based on reviewer feedback:
1. Figure 5: Shows exact avg values (not rounded) so bar ratios match multiplier panel
2. Table 6: Uses ratio-of-averages weighted by total language counts for consistency with Figure 5
3. Equation 17 values printed separately (per-project mean±std) with clear labeling
4. All multiplier calculations clearly documented
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# =====================================================================
# CONFIGURATION - Update these paths to match your directory structure
# =====================================================================
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE, '..', 'data', 'raw_csvs')
FIG_DIR = os.path.join(BASE, 'figures')
TBL_DIR = os.path.join(BASE, 'tables')

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

# =====================================================================
# LOAD AND NORMALIZE DATA
# =====================================================================
frames = []
for f in sorted(os.listdir(CSV_DIR)):
    if f.endswith('.csv'):
        tmp = pd.read_csv(os.path.join(CSV_DIR, f))
        frames.append(tmp)
df = pd.concat(frames, ignore_index=True)

df.columns = [c.strip().lower() for c in df.columns]
df['llm_name'] = df['llm_name'].str.strip().str.lower()
df['language'] = df['language'].str.strip().str.lower()

def norm_success(v):
    s = str(v).strip().lower()
    if s in ('true', '1', 'yes'):
        return 'success'
    if s in ('partial',):
        return 'partial'
    return 'failed'

df['outcome'] = df['execution_success'].apply(norm_success)
df['claimed_count'] = pd.to_numeric(df['claimed_count'], errors='coerce').fillna(0).astype(int)
df['runtime_count'] = pd.to_numeric(df['runtime_count'], errors='coerce').fillna(0).astype(int)

agent_map = {'claude': 'Claude', 'codex': 'Codex', 'gemini': 'Gemini'}
lang_map = {'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript'}
agents_order = ['claude', 'codex', 'gemini']
langs_order = ['python', 'java', 'javascript']

print(f"Loaded {len(df)} rows from {len(frames)} CSVs")

# =====================================================================
# HELPERS
# =====================================================================
def count_missing_deps(subset):
    """Count projects with missing deps using broader method."""
    cg = pd.to_numeric(subset['completeness_gap'], errors='coerce').fillna(0)
    et = subset['error_type'].astype(str).str.lower()
    return ((cg > 0) | (et.str.contains('completeness'))).sum()

def categorize_error(row):
    """Categorize error types into 6 categories."""
    et = str(row.get('error_type', '')).strip().lower()
    if 'dependency' in et or 'missing' in et or 'completeness' in et:
        return 'Dependency'
    elif 'bug' in et or 'syntax' in et:
        return 'Code Bugs'
    elif 'config' in et:
        return 'Configuration'
    elif 'runtime' in et or 'env' in et or 'build' in et:
        return 'Environment'
    elif 'notprocessed' in et:
        return 'Not Processed'
    else:
        return 'Other'

# =====================================================================
# TABLES 1-5 (unchanged from previous version)
# =====================================================================

# Table 1: Per agent
t1_rows = []
for agent in agents_order:
    sub = df[df['llm_name'] == agent]
    total = len(sub)
    succ = (sub['outcome'] == 'success').sum()
    part = (sub['outcome'] == 'partial').sum()
    fail = (sub['outcome'] == 'failed').sum()
    rate = round(succ / total * 100, 1) if total > 0 else 0
    t1_rows.append([agent_map[agent], total, succ, part, fail, rate])
succ_all = (df['outcome'] == 'success').sum()
part_all = (df['outcome'] == 'partial').sum()
fail_all = (df['outcome'] == 'failed').sum()
t1_rows.append(['Overall', 300, succ_all, part_all, fail_all, round(succ_all/300*100, 1)])
t1 = pd.DataFrame(t1_rows, columns=['Agent', 'Total', 'Success', 'Partial', 'Failed', 'Rate (%)'])
t1.to_csv(os.path.join(TBL_DIR, 'table1_agent_summary.csv'), index=False)
print("Table 1 written:")
print(t1.to_string(index=False))
print()

# Table 2: Per language
t2_rows = []
for lang in langs_order:
    sub = df[df['language'] == lang]
    total = len(sub)
    succ = (sub['outcome'] == 'success').sum()
    fail = total - succ
    rate = round(succ / total * 100, 1) if total > 0 else 0
    t2_rows.append([lang_map[lang], total, succ, fail, rate])
t2 = pd.DataFrame(t2_rows, columns=['Language', 'Total', 'Success', 'Failed', 'Success Rate (%)'])
t2.to_csv(os.path.join(TBL_DIR, 'table2_language_summary.csv'), index=False)
print("Table 2 written")

# Table 3: Per agent x language
t3_rows = []
for agent in agents_order:
    for lang in langs_order:
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        succ = (sub['outcome'] == 'success').sum()
        fail = total - succ
        rate = round(succ / total * 100, 1) if total > 0 else 0
        t3_rows.append([agent_map[agent], lang_map[lang], total, succ, fail, rate])
t3 = pd.DataFrame(t3_rows, columns=['Agent', 'Language', 'Total', 'Success', 'Failed', 'Rate (%)'])
t3.to_csv(os.path.join(TBL_DIR, 'table3_agent_language.csv'), index=False)
print("Table 3 written")

# Table 4: Completeness gaps (BROADER METHOD)
t4_rows = []
for agent in agents_order:
    for lang in langs_order:
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        missing = count_missing_deps(sub)
        pct = round(missing / total * 100, 1) if total > 0 else 0
        cg = pd.to_numeric(sub['completeness_gap'], errors='coerce').fillna(0)
        avg_m = round(cg[cg > 0].mean(), 2) if (cg > 0).any() else 0
        max_m = int(cg.max()) if (cg > 0).any() else 0
        t4_rows.append([agent_map[agent], lang_map[lang], f"{missing} ({pct}%)", avg_m, max_m])
t4 = pd.DataFrame(t4_rows, columns=['Agent', 'Language', 'Projects with Missing Deps', 'Avg Missing Deps', 'Max Gap'])
t4.to_csv(os.path.join(TBL_DIR, 'table4_completeness_gaps.csv'), index=False)
total_missing = count_missing_deps(df)
print(f"Table 4 written (total: {total_missing}/300 = {round(total_missing/300*100,1)}%)")

# Table 5: Error classification
non_success = df[df['outcome'].isin(['failed', 'partial'])].copy()
non_success['error_cat'] = non_success.apply(categorize_error, axis=1)
all_cats = ['Code Bugs', 'Configuration', 'Not Processed', 'Dependency', 'Environment', 'Other']
t5_rows = []
for cat in all_cats:
    c = (non_success['error_cat'] == cat).sum()
    pct = round(c / len(non_success) * 100, 1)
    t5_rows.append([cat, c, f"{pct}%"])
t5_rows.append(['Total', len(non_success), '100%'])
t5 = pd.DataFrame(t5_rows, columns=['Error Type', 'Count', '%'])
t5.to_csv(os.path.join(TBL_DIR, 'table5_error_classification.csv'), index=False)
print("Table 5 written:")
print(t5.to_string(index=False))
print()

# =====================================================================
# RUNTIME MULTIPLIER CALCULATIONS (CONSISTENT METHOD)
# =====================================================================
# We use RATIO OF AVERAGES as the primary metric throughout:
#   multiplier = avg_runtime / avg_claimed (per language)
# This is what Figure 5 displays and is the most intuitive measure.
# We also compute per-project mean±std for Equation 17 in the paper,
# which captures project-level variation.

print("=" * 80)
print("RUNTIME MULTIPLIER ANALYSIS")
print("=" * 80)

lang_stats = {}
for lang in langs_order:
    sub = df[(df['language'] == lang) & (df['claimed_count'] > 0) & (df['runtime_count'] > 0)]
    avg_claimed = sub['claimed_count'].mean()
    avg_runtime = sub['runtime_count'].mean()
    ratio_of_avgs = avg_runtime / avg_claimed if avg_claimed > 0 else 0

    per_proj = sub['runtime_count'] / sub['claimed_count']
    mean_mult = per_proj.mean()
    std_mult = per_proj.std()

    lang_stats[lang] = {
        'n': len(sub),
        'avg_claimed': avg_claimed,       # exact, not rounded
        'avg_runtime': avg_runtime,       # exact, not rounded
        'ratio_of_avgs': ratio_of_avgs,   # for Figure 5
        'mean_mult': mean_mult,           # for Equation 17
        'std_mult': std_mult,             # for Equation 17
    }

    print(f"\n  {lang_map[lang]} (N={len(sub)}):")
    print(f"    Avg claimed = {avg_claimed:.1f}, Avg runtime = {avg_runtime:.1f}")
    print(f"    Ratio of averages (Figure 5): {ratio_of_avgs:.1f}x")
    print(f"    Per-project mean ± std (Eq 17): {mean_mult:.1f} ± {std_mult:.1f}x")

# Weighted average for Table 6 (using ratio-of-averages, weighted by total lang counts)
wa = (120 * lang_stats['python']['ratio_of_avgs'] +
      105 * lang_stats['javascript']['ratio_of_avgs'] +
      75 * lang_stats['java']['ratio_of_avgs']) / 300
print(f"\n  Weighted avg (ratio-of-avgs): {wa:.1f}x")

# Overall ratio
all_with = df[(df['claimed_count'] > 0) & (df['runtime_count'] > 0)]
overall_avg_claimed = all_with['claimed_count'].mean()
overall_avg_runtime = all_with['runtime_count'].mean()
overall_ratio = overall_avg_runtime / overall_avg_claimed
print(f"  Overall ratio: avg_runtime({overall_avg_runtime:.1f}) / avg_claimed({overall_avg_claimed:.1f}) = {overall_ratio:.1f}x")

# For the paper, we use the rounded weighted average
paper_multiplier = round(wa)
print(f"\n  >>> PAPER REPORTS: {paper_multiplier}x <<<")

# Table 6
t6_rows = [
    ['Total Projects Analyzed', 300],
    ['Successful Executions', f"{succ_all} ({round(succ_all/300*100,1)}%)"],
    ['Partial Executions', f"{part_all} ({round(part_all/300*100,1)}%)"],
    ['Failed Executions', f"{fail_all} ({round(fail_all/300*100,1)}%)"],
    ['Projects with Incomplete Dependencies', f"{total_missing} ({round(total_missing/300*100,1)}%)"],
    ['Average Runtime Multiplier', f"{paper_multiplier}x"],
]
t6 = pd.DataFrame(t6_rows, columns=['Metric', 'Value'])
t6.to_csv(os.path.join(TBL_DIR, 'table6_overall_summary.csv'), index=False)
print("\nTable 6 written")

# =====================================================================
# FIGURES 1-4 (unchanged from previous version)
# =====================================================================

# Figure 1: Heatmap
fig, ax = plt.subplots(figsize=(10, 5))
heatdata = np.zeros((3, 3))
for i, agent in enumerate(agents_order):
    for j, lang in enumerate(langs_order):
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        succ = (sub['outcome'] == 'success').sum()
        heatdata[i, j] = round(succ / total * 100, 1) if total > 0 else 0
cmap = plt.cm.RdYlGn
im = ax.imshow(heatdata, cmap=cmap, vmin=0, vmax=100, aspect='auto')
ax.set_xticks(range(3))
ax.set_xticklabels([lang_map[l] for l in langs_order], fontsize=12, weight='bold')
ax.set_yticks(range(3))
ax.set_yticklabels([agent_map[a] for a in agents_order], fontsize=12, weight='bold')
ax.set_xlabel('Programming Language', fontsize=12, weight='bold')
ax.set_ylabel('Coding Agent', fontsize=12, weight='bold')
ax.set_title('Execution Success Rates', fontsize=14, weight='bold')
for i in range(3):
    for j in range(3):
        color = 'white' if heatdata[i, j] < 50 else 'black'
        ax.text(j, i, f"{heatdata[i,j]:.1f}%", ha='center', va='center', fontsize=14, weight='bold', color=color)
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Success Rate (%)', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure1_success_heatmap.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure1_success_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()
print("Figure 1 done")

# Figure 2: Language bars
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(3)
width = 0.25
colors = ['#5B9BD5', '#ED7D31', '#70AD47']
for i, agent in enumerate(agents_order):
    rates = []
    for lang in langs_order:
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        succ = (sub['outcome'] == 'success').sum()
        rates.append(round(succ / total * 100, 1) if total > 0 else 0)
    bars = ax.bar(x + i * width, rates, width, label=agent_map[agent], color=colors[i], edgecolor='black', linewidth=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{rate}%", ha='center', va='bottom', fontsize=9, weight='bold')
ax.set_xlabel('Programming Language', fontsize=12, weight='bold')
ax.set_ylabel('Success Rate (%)', fontsize=12, weight='bold')
ax.set_title('Reproducibility by Language', fontsize=14, weight='bold')
ax.set_xticks(x + width)
ax.set_xticklabels([lang_map[l] for l in langs_order], fontsize=11)
ax.set_ylim(0, 110)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure2_language_comparison.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure2_language_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()
print("Figure 2 done")

# Figure 3: Pie charts
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
pie_colors = ['#2ECC71', '#F39C12', '#E74C3C']
for idx, agent in enumerate(agents_order):
    sub = df[df['llm_name'] == agent]
    succ = (sub['outcome'] == 'success').sum()
    part = (sub['outcome'] == 'partial').sum()
    fail = (sub['outcome'] == 'failed').sum()
    sizes = [succ, part, fail]
    labels_list = [f"Success\n{succ}", f"Partial\n{part}", f"Failed\n{fail}"]
    nonzero = [(s, l, c) for s, l, c in zip(sizes, labels_list, pie_colors) if s > 0]
    sz = [x[0] for x in nonzero]
    lb = [x[1] for x in nonzero]
    cl = [x[2] for x in nonzero]
    wedges, texts, autotexts = axes[idx].pie(sz, labels=lb, colors=cl, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
    for at in autotexts:
        at.set_fontsize(9)
        at.set_weight('bold')
    axes[idx].set_title(f"{agent_map[agent]}\n(100 projects)", fontsize=11, weight='bold')
fig.suptitle('Project Outcomes by Agent', fontsize=14, weight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure3_agent_distribution.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure3_agent_distribution.png'), dpi=300, bbox_inches='tight')
plt.close()
print("Figure 3 done")

# Figure 4: Completeness gaps
fig, ax = plt.subplots(figsize=(12, 6))
bar_data = []
bar_labels = []
bar_colors_list = []
agent_colors = {'claude': '#5B9BD5', 'codex': '#ED7D31', 'gemini': '#70AD47'}
for agent in agents_order:
    for lang in langs_order:
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        missing = count_missing_deps(sub)
        pct = round(missing / total * 100, 1) if total > 0 else 0
        bar_data.append(pct)
        bar_labels.append(f"{agent_map[agent]}\n{lang_map[lang]}")
        bar_colors_list.append(agent_colors[agent])
bars = ax.bar(range(len(bar_data)), bar_data, color=bar_colors_list, edgecolor='black', linewidth=0.5)
for i, (bar, val) in enumerate(zip(bars, bar_data)):
    if val > 0:
        agent = agents_order[i // 3]
        lang = langs_order[i % 3]
        sub = df[(df['llm_name'] == agent) & (df['language'] == lang)]
        total = len(sub)
        count = count_missing_deps(sub)
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f"{val}%\n({count}/{total})", ha='center', va='bottom', fontsize=8, weight='bold')
ax.set_xticks(range(len(bar_labels)))
ax.set_xticklabels(bar_labels, fontsize=9, rotation=45, ha='right')
ax.set_ylabel('Projects with Missing Deps (%)', fontsize=12, weight='bold')
ax.set_xlabel('Agent x Language', fontsize=12, weight='bold')
ax.set_title('Dependency Completeness Gaps', fontsize=14, weight='bold')
ax.grid(axis='y', alpha=0.3)
handles = [mpatches.Patch(color=c, label=agent_map[a]) for a, c in agent_colors.items()]
ax.legend(handles=handles, fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure4_dependency_gaps.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure4_dependency_gaps.png'), dpi=300, bbox_inches='tight')
plt.close()
print("Figure 4 done")

# =====================================================================
# FIGURE 5: Runtime Dependency Explosion (FIXED - exact values, consistent)
# =====================================================================
# FIX: Use exact (non-rounded) values for bar labels so that
# bar_runtime / bar_claimed = multiplier shown in right panel
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

claimed_vals = [round(lang_stats[l]['avg_claimed'], 1) for l in langs_order]
runtime_vals = [round(lang_stats[l]['avg_runtime'], 1) for l in langs_order]
# Use ratio of averages for the multiplier panel (consistent with bar values)
multipliers = [round(lang_stats[l]['ratio_of_avgs'], 1) for l in langs_order]
lang_labels = [lang_map[l] for l in langs_order]

# Left panel: Claimed vs Runtime bars (EXACT values, 1 decimal)
x = np.arange(3)
width = 0.35
bars1 = ax1.bar(x - width/2, claimed_vals, width, label='Claimed (Agent-Declared)', color='steelblue', edgecolor='black')
bars2 = ax1.bar(x + width/2, runtime_vals, width, label='Runtime (Actual Installed)', color='coral', edgecolor='black')
ax1.set_xlabel('Programming Language', fontsize=12, weight='bold')
ax1.set_ylabel('Average Number of Dependencies', fontsize=12, weight='bold')
ax1.set_title('Claimed vs Runtime Dependencies', fontsize=12, weight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(lang_labels, fontsize=10)
ax1.legend(fontsize=9)
ax1.grid(axis='y', alpha=0.3)
# Show exact values on bars (1 decimal place)
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        # Show integer if whole number, else 1 decimal
        label = f'{h:.0f}' if h == int(h) else f'{h:.1f}'
        ax1.text(bar.get_x() + bar.get_width()/2, h, label,
                 ha='center', va='bottom', fontsize=9, color='red', weight='bold')

# Right panel: Multiplier (ratio of averages)
bar_colors = ['coral', 'gold', 'lightgreen']
mbars = ax2.bar(range(3), multipliers, color=bar_colors, edgecolor='black')
ax2.set_xlabel('Programming Language', fontsize=12, weight='bold')
ax2.set_ylabel('Multiplier (Runtime / Claimed)', fontsize=12, weight='bold')
ax2.set_title('Transitive Dependency Explosion', fontsize=12, weight='bold')
ax2.set_xticks(range(3))
ax2.set_xticklabels(lang_labels, fontsize=10)
ax2.grid(axis='y', alpha=0.3)
for i, bar in enumerate(mbars):
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}x',
             ha='center', va='bottom', fontsize=11, weight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure5_runtime_explosion.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure5_runtime_explosion.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"\nFigure 5 done:")
for l in langs_order:
    s = lang_stats[l]
    print(f"  {lang_map[l]}: claimed={s['avg_claimed']:.1f}, runtime={s['avg_runtime']:.1f}, ratio={s['ratio_of_avgs']:.1f}x, per-proj={s['mean_mult']:.1f}±{s['std_mult']:.1f}x")

# =====================================================================
# FIGURE 6: Error Type Distribution
# =====================================================================
fig, ax = plt.subplots(figsize=(10, 7))
failed_df = df[df['outcome'].isin(['failed', 'partial'])].copy()
failed_df['error_cat'] = failed_df.apply(categorize_error, axis=1)
all_cats_fig = ['Dependency', 'Code Bugs', 'Configuration', 'Environment', 'Not Processed', 'Other']
cat_colors = {
    'Dependency': '#E74C3C', 'Code Bugs': '#E67E22', 'Configuration': '#F39C12',
    'Environment': '#3498DB', 'Not Processed': '#95A5A6', 'Other': '#BDC3C7',
}
x = np.arange(3)
bottom = np.zeros(3)
for cat in all_cats_fig:
    vals = []
    for agent in agents_order:
        sub = failed_df[failed_df['llm_name'] == agent]
        vals.append((sub['error_cat'] == cat).sum())
    if sum(vals) > 0:
        ax.bar(x, vals, width=0.6, bottom=bottom, label=cat, color=cat_colors.get(cat, '#95A5A6'), edgecolor='black', linewidth=0.5)
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(x[i], bottom[i] + v/2, str(v), ha='center', va='center', fontsize=10, weight='bold', color='white')
        bottom += np.array(vals)
ax.set_xlabel('Coding Agent', fontsize=12, weight='bold')
ax.set_ylabel('Failed Projects', fontsize=12, weight='bold')
ax.set_title('Error Types by Agent', fontsize=14, weight='bold')
ax.set_xticks(x)
ax.set_xticklabels([agent_map[a] for a in agents_order], fontsize=11)
ax.legend(fontsize=9, loc='upper right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'figure6_error_distribution.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(FIG_DIR, 'figure6_error_distribution.png'), dpi=300, bbox_inches='tight')
plt.close()
print("\nFigure 6 done:")
for cat in all_cats_fig:
    c = (failed_df['error_cat'] == cat).sum()
    print(f"  {cat}: {c} ({round(c/len(failed_df)*100,1)}%)")

# =====================================================================
# PRINT ALL KEY STATISTICS FOR PAPER
# =====================================================================
print()
print("=" * 80)
print("KEY STATISTICS FOR PAPER")
print("=" * 80)
print(f"Overall: {succ_all}/300 = {round(succ_all/300*100,1)}% success")
print(f"Partial: {part_all}, Failed: {fail_all}")
print(f"Projects with incomplete deps: {total_missing}/300 = {round(total_missing/300*100,1)}%")

print(f"\n--- Figure 5 values (ratio of averages) ---")
for l in langs_order:
    s = lang_stats[l]
    print(f"  {lang_map[l]}: claimed={s['avg_claimed']:.1f}, runtime={s['avg_runtime']:.1f}, multiplier={s['ratio_of_avgs']:.1f}x")

print(f"\n--- Equation 17 values (per-project mean ± std) ---")
for l in langs_order:
    s = lang_stats[l]
    print(f"  {lang_map[l]}: {s['mean_mult']:.1f} ± {s['std_mult']:.1f}x")

print(f"\n--- Table 6 weighted average ---")
print(f"  Method: ratio-of-averages, weighted by total language counts (120/105/75)")
print(f"  = {wa:.1f}x (reported as {paper_multiplier}x)")

print(f"\n--- Intro numbers ---")
print(f"  Avg claimed (all with data): {overall_avg_claimed:.1f}")
print(f"  Avg runtime (all with data): {overall_avg_runtime:.1f}")
print(f"  Rounded for intro: 'requiring an average of {round(overall_avg_runtime)} packages at runtime instead of the {round(overall_avg_claimed)} typically declared'")

# SciUnit example
py_succ = df[(df['language'] == 'python') & (df['outcome'] == 'success')]
py_with_rt = py_succ[py_succ['runtime_count'] > 0]
print(f"\n--- Python SciUnit ---")
print(f"  Successful: {len(py_succ)}, with runtime>0: {len(py_with_rt)}")
print(f"  Avg claimed: {py_succ['claimed_count'].mean():.1f}")
print(f"  Avg runtime (where>0): {py_with_rt['runtime_count'].mean():.1f}")

print("\n=== ALL FIGURES AND TABLES REGENERATED ===")