import json

# Read the notebook
with open(r'D:\LLM Dependency Manager\results_AAAI2026\AAAI2026_Reproducibility_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Figure 5: Runtime Dependency Explosion
figure5_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Figure 5: Runtime Dependency Explosion\n",
        "\n",
        "Shows the gap between claimed and runtime dependencies, highlighting the transitive dependency multiplier effect."
    ]
}

figure5_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Figure 5: Runtime Dependency Explosion (Claimed vs Runtime)\n",
        "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))\n",
        "\n",
        "# Calculate average dependencies by language\n",
        "lang_deps = df.groupby('language').agg({\n",
        "    'claimed_count': 'mean',\n",
        "    'runtime_count': 'mean'\n",
        "}).round(1)\n",
        "\n",
        "# Left panel: Claimed vs Runtime\n",
        "x = np.arange(len(lang_deps))\n",
        "width = 0.35\n",
        "\n",
        "bars1 = ax1.bar(x - width/2, lang_deps['claimed_count'], width, label='Claimed (Agent-Declared)', color='steelblue', edgecolor='black')\n",
        "bars2 = ax1.bar(x + width/2, lang_deps['runtime_count'], width, label='Runtime (Actual Installed)', color='coral', edgecolor='black')\n",
        "\n",
        "ax1.set_xlabel('Programming Language', fontsize=12, weight='bold')\n",
        "ax1.set_ylabel('Average Number of Dependencies', fontsize=12, weight='bold')\n",
        "ax1.set_title('Claimed vs Runtime Dependencies', fontsize=12)\n",
        "ax1.set_xticks(x)\n",
        "ax1.set_xticklabels(['Java', 'JavaScript', 'Python'], fontsize=10)\n",
        "ax1.legend(fontsize=10)\n",
        "ax1.grid(axis='y', alpha=0.3)\n",
        "\n",
        "# Add value labels on bars\n",
        "for bars in [bars1, bars2]:\n",
        "    for bar in bars:\n",
        "        height = bar.get_height()\n",
        "        ax1.text(bar.get_x() + bar.get_width()/2., height,\n",
        "                f'{height:.1f}', ha='center', va='bottom', fontsize=9)\n",
        "\n",
        "# Right panel: Multiplier effect\n",
        "multipliers = (lang_deps['runtime_count'] / lang_deps['claimed_count']).round(1)\n",
        "bars = ax2.bar(range(len(multipliers)), multipliers.values, color=['coral', 'gold', 'lightgreen'], edgecolor='black')\n",
        "\n",
        "ax2.set_xlabel('Programming Language', fontsize=12, weight='bold')\n",
        "ax2.set_ylabel('Multiplier (Runtime / Claimed)', fontsize=12, weight='bold')\n",
        "ax2.set_title('Transitive Dependency Explosion', fontsize=12)\n",
        "ax2.set_xticks(range(len(multipliers)))\n",
        "ax2.set_xticklabels(['Java', 'JavaScript', 'Python'], fontsize=10)\n",
        "ax2.grid(axis='y', alpha=0.3)\n",
        "\n",
        "# Add value labels\n",
        "for i, bar in enumerate(bars):\n",
        "    height = bar.get_height()\n",
        "    ax2.text(bar.get_x() + bar.get_width()/2., height,\n",
        "            f'{height:.1f}x', ha='center', va='bottom', fontsize=10, weight='bold')\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.savefig('figures/figure5_runtime_explosion.png', dpi=300, bbox_inches='tight')\n",
        "plt.savefig('figures/figure5_runtime_explosion.pdf', bbox_inches='tight')\n",
        "plt.show()\n",
        "\n",
        "print(f\"Runtime Dependency Multipliers:\")\n",
        "print(f\"  Java: {multipliers['java']:.1f}x\")\n",
        "print(f\"  JavaScript: {multipliers['javascript']:.1f}x\")\n",
        "print(f\"  Python: {multipliers['python']:.1f}x\")"
    ]
}

# Figure 6: Error Type Distribution
figure6_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Figure 6: Error Type Distribution by Agent\n",
        "\n",
        "Breakdown of failure types for each coding agent, showing different error patterns."
    ]
}

figure6_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Figure 6: Error Type Distribution by Agent\n",
        "fig, ax = plt.subplots(figsize=(15, 8))\n",
        "\n",
        "# Get failed projects and categorize errors\n",
        "failed_df = df[df['execution_success'].isin([False, 'false', 'False', 'partial', 'Partial'])].copy()\n",
        "\n",
        "# Map errors to categories\n",
        "def categorize_error(row):\n",
        "    error_type = str(row['error_type']).lower()\n",
        "    if 'dependency' in error_type or 'missing' in error_type:\n",
        "        return 'Dependency Issues'\n",
        "    elif 'bug' in error_type or 'syntax' in error_type:\n",
        "        return 'Code Bugs'\n",
        "    elif 'config' in error_type or 'partial' in error_type:\n",
        "        return 'Configuration'\n",
        "    elif 'runtime' in error_type or 'env' in error_type:\n",
        "        return 'Environment'\n",
        "    elif 'notprocessed' in error_type:\n",
        "        return 'Not Processed'\n",
        "    else:\n",
        "        return 'Other'\n",
        "\n",
        "failed_df['error_category'] = failed_df.apply(categorize_error, axis=1)\n",
        "\n",
        "# Create stacked bar chart data\n",
        "error_counts = failed_df.groupby(['llm_name', 'error_category']).size().unstack(fill_value=0)\n",
        "\n",
        "# Define colors for error categories\n",
        "colors = {\n",
        "    'Dependency Issues': '#e74c3c',\n",
        "    'Code Bugs': '#e67e22',\n",
        "    'Configuration': '#f39c12',\n",
        "    'Environment': '#3498db',\n",
        "    'Not Processed': '#95a5a6',\n",
        "    'Other': '#7f8c8d'\n",
        "}\n",
        "\n",
        "# Plot stacked bars\n",
        "agents = ['claude', 'codex', 'gemini']\n",
        "x = np.arange(len(agents))\n",
        "bottom = np.zeros(len(agents))\n",
        "\n",
        "for category in ['Dependency Issues', 'Code Bugs', 'Configuration', 'Environment', 'Not Processed', 'Other']:\n",
        "    if category in error_counts.columns:\n",
        "        values = [error_counts.loc[agent, category] if agent in error_counts.index else 0 for agent in agents]\n",
        "        ax.bar(x, values, width=0.6, bottom=bottom, label=category, \n",
        "               color=colors.get(category, '#95a5a6'), edgecolor='black')\n",
        "        bottom += values\n",
        "\n",
        "ax.set_xlabel('Coding Agent', fontsize=12, weight='bold')\n",
        "ax.set_ylabel('Number of Failed Projects', fontsize=12, weight='bold')\n",
        "ax.set_title('Error Type Distribution by Agent', fontsize=12)\n",
        "ax.set_xticks(x)\n",
        "ax.set_xticklabels(['Claude Code', 'GitHub Copilot', 'Gemini Code Assist'], fontsize=10)\n",
        "ax.legend(fontsize=10, loc='upper right')\n",
        "ax.grid(axis='y', alpha=0.3)\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.savefig('figures/figure6_error_distribution.png', dpi=300, bbox_inches='tight')\n",
        "plt.savefig('figures/figure6_error_distribution.pdf', bbox_inches='tight')\n",
        "plt.show()\n",
        "\n",
        "print(\"\\nError Distribution Summary:\")\n",
        "print(error_counts)"
    ]
}

# Insert the new cells after the last figure (which should be around index -3 or -4)
# Find the position after Figure 4
insert_position = len(nb['cells']) - 1  # Insert before the last cell

# Insert Figure 5
nb['cells'].insert(insert_position, figure5_markdown)
nb['cells'].insert(insert_position + 1, figure5_code)

# Insert Figure 6
nb['cells'].insert(insert_position + 2, figure6_markdown)
nb['cells'].insert(insert_position + 3, figure6_code)

# Save the updated notebook
with open(r'D:\LLM Dependency Manager\results_AAAI2026\AAAI2026_Reproducibility_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Successfully added Figure 5 and Figure 6 to the notebook!")
print(f"Total cells in notebook: {len(nb['cells'])}")
