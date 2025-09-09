import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# --- Data ---
# Updated X-axis labels with model parameters
# Use compact in-figure x-ticks with numbering; introduce mapping in paper caption
categories = ["Z3", "C-1", "C-2", "C-3"]

# Z3's overall performance (baseline)
z3_total_solved = 72
z3_total_failed = 265

# COMPASS performance on the 265 cases Z3 FAILED
data_on_z3_failed = {
    'Solved': np.array([23, 19, 14]),
    'Failed': np.array([242, 246, 251])
}

# COMPASS performance on the 72 cases Z3 SOLVED
data_on_z3_solved = {
    'Solved': np.array([71, 67, 50]),
    'Failed': np.array([1, 5, 22])
}

# --- Styling ---
font_size_base = 28  # 2x of RQ2's base (14)
font_size_title = 36  # 2x of RQ2's title (18)

colors = {"Solved": "#3988c5", "Failed": "#abd0eb"}
# Hatches to distinguish the two case origins for COMPASS
hatches = ['//', '\\']

plt.rcParams.update({'font.size': font_size_base, 'font.family': 'sans-serif'})

# --- Plotting ---
fig, ax = plt.subplots(figsize=(10, 5.76576))

n_methods = len(categories)
bar_width = 0.09504
# Slightly increase group spacing by 5%
ind = np.arange(n_methods) * 0.21

def add_labels(bars, bottom_values, color='black'):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2., bottom_values[i] + height / 2.,
                    f'{int(height)}', ha='center', va='center',
                    color=color, fontsize=font_size_base - 2, fontweight='bold')

# 1. Plot Z3's single, centered bar (no hatch)
z3_succeed = ax.bar(ind[0], z3_total_solved, bar_width, color=colors['Solved'])
z3_failed = ax.bar(ind[0], z3_total_failed, bar_width, bottom=z3_total_solved, color=colors['Failed'])
add_labels(z3_succeed, np.array([0]), color='white')
add_labels(z3_failed, np.array([z3_total_solved]), color='black')

# 2. Plot COMPASS methods with two bars each
compass_indices = ind[1:]
# Bar for performance on Z3's FAILED cases
pos1 = compass_indices - bar_width / 2
s1_s = ax.bar(pos1, data_on_z3_failed['Solved'], bar_width, color=colors['Solved'],
              hatch=hatches[0], edgecolor='#999999', linewidth=0.5)
s1_f = ax.bar(pos1, data_on_z3_failed['Failed'], bar_width, bottom=data_on_z3_failed['Solved'], color=colors['Failed'],
              hatch=hatches[0], edgecolor='#999999', linewidth=0.5)
add_labels(s1_s, np.zeros_like(data_on_z3_failed['Solved'], dtype=float), color='white')
add_labels(s1_f, data_on_z3_failed['Solved'].astype(float), color='black')

# Bar for performance on Z3's SOLVED cases
pos2 = compass_indices + bar_width / 2
s2_s = ax.bar(pos2, data_on_z3_solved['Solved'], bar_width, color=colors['Solved'],
              hatch=hatches[1], edgecolor='#999999', linewidth=0.5)
s2_f = ax.bar(pos2, data_on_z3_solved['Failed'], bar_width, bottom=data_on_z3_solved['Solved'], color=colors['Failed'],
              hatch=hatches[1], edgecolor='#999999', linewidth=0.5)
add_labels(s2_s, np.zeros_like(data_on_z3_solved['Solved'], dtype=float), color='white')
add_labels(s2_f, data_on_z3_solved['Solved'].astype(float), color='black')

# --- Formatting ---
ax.set_ylabel('Number of Cases', fontsize=font_size_base)
ax.set_xticks(ind)
# Single-line labels with subscripts per request
pretty_labels = [
    'Z3',
    'COMPASS$_{1}$',
    'COMPASS$_{2}$',
    'COMPASS$_{3}$',
]
ax.set_xticklabels(pretty_labels, fontsize=font_size_base - 2)
ax.tick_params(axis='x', pad=6)
ax.set_ylim(top=ax.get_ylim()[1] * 1.015)

# --- Custom Legend ---
legend_elements = [
    Patch(facecolor=colors['Solved'], label='Outcome: Solved'),
    Patch(facecolor=colors['Failed'], label='Outcome: Failed'),
    Patch(facecolor='white', edgecolor='#999999', hatch=hatches[0], label="Z3's 265 Failed Cases"),
    Patch(facecolor='white', edgecolor='#999999', hatch=hatches[1], label="Z3's 72 Solved Cases"),
]
fig.legend(
    handles=legend_elements,
    loc='upper center',
    bbox_to_anchor=(0.5, 1.06),
    ncol=2,  # stacked two rows to reduce width
    borderaxespad=0.15,
    fancybox=True,
    shadow=False,
    fontsize=font_size_base,
    frameon=False,
    columnspacing=0.8,
    handlelength=1.2,
    handletextpad=0.4,
    labelspacing=0.3,
)

# --- Final Touches ---
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('grey')
ax.tick_params(bottom=False, left=False)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color='#EEEEEE', linestyle='-', linewidth=0.8)

plt.tight_layout(pad=0.3, rect=[0.0, 0.0, 1.0, 0.94])

# --- Save Figure ---
output_path = 'RQ1-effectiveness.pdf'
plt.savefig(output_path, format='pdf', bbox_inches='tight', pad_inches=0.0)

print(f"Chart updated and saved to {output_path}")
