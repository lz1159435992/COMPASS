import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# --- Data ---
qf_lia_data = {
    'Z3': {'Solved': 5, 'Failed': 53},
    'On Failed Cases': {'Solved': 3, 'Failed': 45},
    'On Solved Cases': {'Solved': 2, 'Failed': 8}
}

qf_nia_data = {
    'Z3': {'Solved': 466, 'Failed': 1553},
    'On Failed Cases': {'Solved': 324, 'Failed': 1502},
    'On Solved Cases': {'Solved': 142, 'Failed': 51}
}

# Display labels for x-axis (drop 'On')
bar_categories = ['Z3', 'Failed Cases', 'Solved Cases']

# --- Styling (RQ1 Style) ---
font_size_base = 14
font_size_title = 18
solved_color = '#3988c5'
failed_color = '#abd0eb'
hatch_failed_cases = '//'
hatch_solved_cases = '\\'

plt.rcParams.update({'font.size': font_size_base, 'font.family': 'sans-serif'})

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 3.36), sharey=False)

bar_width = 0.7
ind = np.array([0.0, 1.5, 3.0])

def plot_subplot(ax, data, title):
    # Title removed to keep figure compact; caption will provide context

    # Z3 bar (no hatch)
    s_base = data['Z3']['Solved']
    f_base = data['Z3']['Failed']
    ax.bar(ind[0], s_base, bar_width, color=solved_color)
    ax.bar(ind[0], f_base, bar_width, bottom=s_base, color=failed_color)
    if s_base > 0: ax.text(ind[0], s_base/2, s_base, ha='center', va='center', color='white', fontsize=font_size_base - 2, fontweight='bold')
    if f_base > 0: ax.text(ind[0], s_base + f_base/2, f_base, ha='center', va='center', color='black', fontsize=font_size_base - 2, fontweight='bold')

    # On Failed Cases bar (hatch //)
    s_failed = data['On Failed Cases']['Solved']
    f_failed = data['On Failed Cases']['Failed']
    ax.bar(ind[1], s_failed, bar_width, color=solved_color, hatch=hatch_failed_cases,
           edgecolor='#999999', linewidth=0.6)
    ax.bar(ind[1], f_failed, bar_width, bottom=s_failed, color=failed_color, hatch=hatch_failed_cases,
           edgecolor='#999999', linewidth=0.6)
    if s_failed > 0: ax.text(ind[1], s_failed/2, s_failed, ha='center', va='center', color='white', fontsize=font_size_base - 2, fontweight='bold')
    if f_failed > 0: ax.text(ind[1], s_failed + f_failed/2, f_failed, ha='center', va='center', color='black', fontsize=font_size_base - 2, fontweight='bold')

    # On Solved Cases bar (hatch \\)
    s_solved = data['On Solved Cases']['Solved']
    f_solved = data['On Solved Cases']['Failed']
    ax.bar(ind[2], s_solved, bar_width, color=solved_color, hatch=hatch_solved_cases,
           edgecolor='#999999', linewidth=0.6)
    ax.bar(ind[2], f_solved, bar_width, bottom=s_solved, color=failed_color, hatch=hatch_solved_cases,
           edgecolor='#999999', linewidth=0.6)
    if s_solved > 0: ax.text(ind[2], s_solved/2, s_solved, ha='center', va='center', color='white', fontsize=font_size_base - 2, fontweight='bold')
    if f_solved > 0: ax.text(ind[2], s_solved + f_solved/2, f_solved, ha='center', va='center', color='black', fontsize=font_size_base - 2, fontweight='bold')

    # --- Formatting ---
    ax.set_xticks(ind)
    ax.set_xticklabels(bar_categories, fontsize=font_size_base)
    ax.margins(x=0.02)
    ax.set_xlim(ind[0] - 0.7, ind[-1] + 0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_color('grey')
    ax.tick_params(bottom=False, left=True)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE', linestyle='-', linewidth=0.8)
    ax.set_ylabel('Number of Cases', fontsize=font_size_base)

# Plot left and right subplots
plot_subplot(ax1, qf_lia_data, 'SMT-COMP Logic: QF_LIA')
plot_subplot(ax2, qf_nia_data, 'SMT-COMP Logic: QF_NIA')

# --- Legend: place above subplots to avoid overlap ---
legend_elements = [
    Patch(facecolor=solved_color, label='Outcome: Solved'),
    Patch(facecolor=failed_color, label='Outcome: Failed'),
    Patch(facecolor='white', edgecolor='#999999', hatch=hatch_failed_cases, label='Z3 Failed Cases'),
    Patch(facecolor='white', edgecolor='#999999', hatch=hatch_solved_cases, label='Z3 Solved Cases'),
]
fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.005),
           ncol=4, borderaxespad=0.2, fancybox=True, shadow=False, fontsize=font_size_base, frameon=False)

# Slightly reclaim top area while keeping legend close
plt.tight_layout(pad=0.45, rect=[0.0, 0.0, 1.0, 0.945])

# --- Save Figure ---
output_path = 'RQ2-scalability.pdf'
plt.savefig(output_path, format='pdf', bbox_inches='tight', pad_inches=0.005)

print(f"Chart created and saved to {output_path}")
