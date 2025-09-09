import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# --- Data for RQ3 ---
categories = ["Random+Random", "LLM", "Random+LLM", "RL+Random", "RL+LLM"]
succeed_data = np.array([62, 30, 62, 84, 94])
failed_data = np.array([275, 307, 275, 253, 243])

# --- Styling (Consistent with RQ1/RQ2) ---
font_size_base = 14
font_size_title = 18
colors = {"Solved": "#3988c5", "Failed": "#abd0eb"}

plt.rcParams.update({'font.size': font_size_base, 'font.family': 'sans-serif'})

# --- Plotting ---
# Reduce height by 20% (from 4.8 to 3.84)
fig, ax = plt.subplots(figsize=(10, 3.84))

n_categories = len(categories)
bar_width = 0.5
ind = np.arange(n_categories)

# Plotting the bars
succeed_bars = ax.bar(ind, succeed_data, bar_width, color=colors['Solved'], label='Solved')
failed_bars = ax.bar(ind, failed_data, bar_width, bottom=succeed_data, color=colors['Failed'], label='Failed')

# Add labels inside the bars and success rate on top
total_data = succeed_data + failed_data
for i in range(n_categories):
    # Add success rate on top of the bar
    if total_data[i] > 0:
        success_rate = (succeed_data[i] / total_data[i]) * 100
        ax.text(ind[i], total_data[i] + 5, f'{success_rate:.1f}%',
                ha='center', va='bottom', color='black', fontsize=font_size_base - 2, fontweight='bold')

    # Label for succeed bar
    if succeed_data[i] > 0:
        ax.text(ind[i], succeed_data[i] / 2, f'{succeed_data[i]}',
                ha='center', va='center', color='white', fontsize=font_size_base - 2, fontweight='bold')
    # Label for failed bar
    if failed_data[i] > 0:
        ax.text(ind[i], succeed_data[i] + failed_data[i] / 2, f'{failed_data[i]}',
                ha='center', va='center', color='black', fontsize=font_size_base - 2, fontweight='bold')

# --- Formatting ---
ax.set_ylabel('Number of Cases', fontsize=font_size_base)
ax.set_xticks(ind)
ax.set_xticklabels(categories, fontsize=font_size_base)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_color('grey')
ax.tick_params(bottom=False, left=True)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color='#EEEEEE', linestyle='-', linewidth=0.8)

# --- Legend ---
legend_elements = [
    Patch(facecolor=colors['Solved'], label='Outcome: Solved'),
    Patch(facecolor=colors['Failed'], label='Outcome: Failed')
]
ax.legend(handles=legend_elements,
          loc='upper right', bbox_to_anchor=(1, 0.95),
          fancybox=True, shadow=False, fontsize=font_size_base,
          labelspacing=0.4)  # reduce vertical spacing by 20% (default ~0.5)

plt.tight_layout(pad=0.5)

# --- Save Figure ---
output_path = 'RQ3-effectiveness.pdf'
plt.savefig(output_path, format='pdf', bbox_inches='tight', pad_inches=0.02)

print(f"Chart created and saved to {output_path}")
