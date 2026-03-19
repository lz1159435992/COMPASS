#!/usr/bin/env python3
"""
COMPASS Experimental Results Visualization Script

This script displays the key experimental results from the COMPASS paper.
Run this script to view RQ1, RQ2, and RQ3 results in formatted tables.

Usage:
    python scripts/show_results.py [--rq RQ_NUMBER] [--save-plots]
    
Options:
    --rq RQ_NUMBER    Show results for specific RQ (1, 2, or 3). Default: all
    --save-plots      Save plots to files instead of displaying
"""

import argparse
import sys
from pathlib import Path

# Try to import optional dependencies
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Patch
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Plots will be disabled.")
    print("Install with: pip install matplotlib numpy")


# =============================================================================
# RQ1: Effectiveness Data
# =============================================================================

RQ1_SMTIMER_DATA = {
    "title": "RQ1: Multi-solver Results on SMTimer (hard satisfiable subset)",
    "headers": ["Solver", "Total", "Baseline Solved", "COMPASS Solved", 
                "Baseline Avg.Time(s)", "COMPASS Avg.Time(s)", "Retention(%)"],
    "data": [
        ["Z3", 449, 120, 96, 548.0, 210.6, 60.8],
        ["CVC5", 1073, 228, 360, 641.6, 69.9, 18.9],
        ["MathSAT", 1913, 29, 100, 798.5, 499.5, 37.9],
        ["BVParti", 33, 2, 0, 693.8, "-", 0.0],
    ]
}

RQ1_QFNIA_DATA = {
    "title": "RQ1: Multi-solver Results on SMT-COMP QF_NIA (hard satisfiable subset)",
    "headers": ["Solver", "Total", "Baseline Solved", "COMPASS Solved",
                "Baseline Avg.Time(s)", "COMPASS Avg.Time(s)", "Retention(%)"],
    "data": [
        ["Z3", 2019, 193, 467, 627.0, 225.3, 73.6],
        ["CVC5", 4849, 234, 1419, 612.7, 252.9, 65.0],
        ["MathSAT", 3598, 345, 505, 617.8, 230.4, 83.5],
        ["AriParti", 1926, 137, 59, 612.4, 240.6, 24.1],
    ]
}


# =============================================================================
# RQ2: Component Analysis Data
# =============================================================================

RQ2_LLM_ABLATION_DATA = {
    "title": "RQ2: LLM Ablation Study on SMTimer (Z3 backend, Total=449)",
    "headers": ["Model Variant", "Solved", "Success Rate(%)", "Avg.Time(s)", 
                "Both", "Only COMPASS", "Only Z3", "Retention(%)"],
    "data": [
        ["COMPASS_L3.1", 96, 21.4, 210.6, 73, 23, 47, 60.8],
        ["COMPASS_L3.3", 88, 19.6, 396.3, 69, 19, 51, 57.5],
        ["COMPASS_R1", 67, 14.9, 566.3, 53, 14, 67, 44.2],
    ]
}

RQ2_COMPONENT_ABLATION_DATA = {
    "title": "RQ2: Component Ablation Study on SMTimer (Z3 backend, Total=449)",
    "headers": ["Method", "Solved", "Success Rate(%)", "Avg.Time(s)"],
    "data": [
        ["Random+Random", 73, 16.3, 380.7],
        ["LLM only", 30, 6.7, 4.1],
        ["Random+LLM", 69, 15.4, 330.7],
        ["RL+Random", 89, 19.8, 411.7],
        ["RL+LLM (COMPASS)", 96, 21.4, 210.6],
    ]
}


# =============================================================================
# RQ3: Parallel Portfolio Data
# =============================================================================

RQ3_SMTIMER_DATA = {
    "title": "RQ3: Parallel Portfolio Results on SMTimer (43,914 instances)",
    "headers": ["Solver", "Strategy", "SAT Solved", "Unknown", 
                "SAT Avg.(s)", "Overall Avg.(s)", "Total(h)", "Total Red.(%)"],
    "data": [
        ["Z3", "Direct", 17476, 1679, 6.8, 20.9, 255.0, "-"],
        ["Z3", "Parallel", 17521, 1634, 6.8, 21.3, 259.6, -1.8],
        ["CVC5", "Direct", 17499, 958, 14.2, 31.3, 382.2, "-"],
        ["CVC5", "Parallel", 17816, 641, 13.6, 22.6, 275.8, 27.8],
        ["MathSAT", "Direct", 18449, 1995, 2.6, 60.8, 741.4, "-"],
        ["MathSAT", "Parallel", 18538, 1906, 4.8, 59.3, 723.2, 2.5],
    ]
}

RQ3_QFNIA_DATA = {
    "title": "RQ3: Parallel Portfolio Results on SMT-COMP QF_NIA (10,043 instances)",
    "headers": ["Solver", "Strategy", "SAT Solved", "Unknown",
                "SAT Avg.(s)", "Overall Avg.(s)", "Total(h)", "Total Red.(%)"],
    "data": [
        ["Z3", "Direct", 6811, 2440, 32.9, 315.9, 881.4, "-"],
        ["Z3", "Parallel", 7135, 2116, 32.8, 279.1, 778.7, 11.7],
        ["CVC5", "Direct", 4736, 5029, 50.2, 626.5, 1747.9, "-"],
        ["CVC5", "Parallel", 6000, 3765, 83.0, 501.4, 1398.8, 20.0],
        ["MathSAT", "Direct", 6127, 3567, 55.9, 462.9, 1291.5, "-"],
        ["MathSAT", "Parallel", 6344, 3350, 43.6, 430.4, 1200.8, 7.0],
    ]
}


# =============================================================================
# Display Functions
# =============================================================================

def print_table(table_data):
    """Print a formatted table."""
    print(f"\n{table_data['title']}")
    print("=" * 80)
    
    headers = table_data['headers']
    data = table_data['data']
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print data rows
    for row in data:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))
    
    print()


def show_rq1(save_plots=False):
    """Display RQ1 results."""
    print("\n" + "=" * 80)
    print("RQ1: Effectiveness of COMPASS")
    print("=" * 80)
    print("\nQuestion: How effectively does COMPASS improve the solving capability")
    print("of diverse SMT solver architectures on hard satisfiable constraints?")
    
    print_table(RQ1_SMTIMER_DATA)
    print_table(RQ1_QFNIA_DATA)
    
    print("\nAnswer to RQ1:")
    print("-" * 40)
    print("COMPASS improves effectiveness for several major solver families,")
    print("with the strongest gain on CVC5, which solves 506.4% more QF_NIA instances.")
    print("The results show that COMPASS is often complementary to the baseline solver,")
    print("although its benefits are less stable on partitioning-based backends.")
    
    if HAS_MATPLOTLIB and save_plots:
        plot_rq1()


def show_rq2(save_plots=False):
    """Display RQ2 results."""
    print("\n" + "=" * 80)
    print("RQ2: Key Components Responsible for COMPASS's Effectiveness")
    print("=" * 80)
    print("\nQuestion: How do RL-guided variable selection and LLM value proposal")
    print("contribute to the overall effectiveness and efficiency?")
    
    print_table(RQ2_LLM_ABLATION_DATA)
    print_table(RQ2_COMPONENT_ABLATION_DATA)
    
    print("\nAnswer to RQ2:")
    print("-" * 40)
    print("Effectiveness is governed primarily by RL-guided variable selection.")
    print("The LLM contributes modestly to coverage but improves efficiency")
    print("when paired with good variable choices.")
    print("LLaMA 3.1 achieves the best overall performance.")
    
    if HAS_MATPLOTLIB and save_plots:
        plot_rq2()


def show_rq3(save_plots=False):
    """Display RQ3 results."""
    print("\n" + "=" * 80)
    print("RQ3: Parallel Portfolio Utility")
    print("=" * 80)
    print("\nQuestion: Can COMPASS improve practical deployment performance")
    print("when used as a parallel portfolio component?")
    
    print_table(RQ3_SMTIMER_DATA)
    print_table(RQ3_QFNIA_DATA)
    
    print("\nAnswer to RQ3:")
    print("-" * 40)
    print("COMPASS is effective as a parallel portfolio component on general-purpose")
    print("SMT solvers. Across six solver-dataset pairs, it increases SAT solved")
    print("and reduces unknown results, while reducing total time by 2.5%-27.8%")
    print("in five pairs (one minor increase of 1.8%).")
    
    if HAS_MATPLOTLIB and save_plots:
        plot_rq3()


# =============================================================================
# Plotting Functions
# =============================================================================

def plot_rq1():
    """Generate RQ1 plots."""
    if not HAS_MATPLOTLIB:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # SMTimer plot
    ax1 = axes[0]
    solvers = ["Z3", "CVC5", "MathSAT", "BVParti"]
    baseline_solved = [120, 228, 29, 2]
    compass_solved = [96, 360, 100, 0]
    
    x = np.arange(len(solvers))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, baseline_solved, width, label='Baseline', color='#abd0eb')
    bars2 = ax1.bar(x + width/2, compass_solved, width, label='COMPASS', color='#3988c5')
    
    ax1.set_ylabel('Solved Count')
    ax1.set_title('SMTimer (hard sat subset)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(solvers)
    ax1.legend()
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color='#EEEEEE')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    
    # QF_NIA plot
    ax2 = axes[1]
    solvers = ["Z3", "CVC5", "MathSAT", "AriParti"]
    baseline_solved = [193, 234, 345, 137]
    compass_solved = [467, 1419, 505, 59]
    
    x = np.arange(len(solvers))
    bars1 = ax2.bar(x - width/2, baseline_solved, width, label='Baseline', color='#abd0eb')
    bars2 = ax2.bar(x + width/2, compass_solved, width, label='COMPASS', color='#3988c5')
    
    ax2.set_ylabel('Solved Count')
    ax2.set_title('SMT-COMP QF_NIA (hard sat subset)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(solvers)
    ax2.legend()
    ax2.set_axisbelow(True)
    ax2.yaxis.grid(True, color='#EEEEEE')
    
    for bar in bars1:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('RQ1_effectiveness.pdf', format='pdf', bbox_inches='tight')
    print("Saved: RQ1_effectiveness.pdf")


def plot_rq2():
    """Generate RQ2 plots."""
    if not HAS_MATPLOTLIB:
        return
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    methods = ["Random+Random", "LLM only", "Random+LLM", "RL+Random", "RL+LLM"]
    solved = [73, 30, 69, 89, 96]
    failed = [376, 419, 380, 360, 353]
    
    x = np.arange(len(methods))
    width = 0.5
    
    bars1 = ax.bar(x, solved, width, label='Solved', color='#3988c5')
    bars2 = ax.bar(x, failed, width, bottom=solved, label='Failed/Timeout', color='#abd0eb')
    
    ax.set_ylabel('Number of Cases')
    ax.set_title('RQ2: Component Ablation Study (SMTimer, Z3 backend, Total=449)')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    
    # Add success rate labels
    for i, (s, f) in enumerate(zip(solved, failed)):
        total = s + f
        if total > 0:
            rate = s / total * 100
            ax.annotate(f'{rate:.1f}%', xy=(i, total + 5), ha='center', va='bottom',
                       fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('RQ2_component_ablation.pdf', format='pdf', bbox_inches='tight')
    print("Saved: RQ2_component_ablation.pdf")


def plot_rq3():
    """Generate RQ3 plots."""
    if not HAS_MATPLOTLIB:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # SMTimer
    ax1 = axes[0]
    solvers = ["Z3", "CVC5", "MathSAT"]
    direct_sat = [17476, 17499, 18449]
    parallel_sat = [17521, 17816, 18538]
    
    x = np.arange(len(solvers))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, direct_sat, width, label='Direct', color='#abd0eb')
    bars2 = ax1.bar(x + width/2, parallel_sat, width, label='Parallel', color='#3988c5')
    
    ax1.set_ylabel('SAT Solved Count')
    ax1.set_title('SMTimer (43,914 instances)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(solvers)
    ax1.legend()
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color='#EEEEEE')
    
    # QF_NIA
    ax2 = axes[1]
    direct_sat = [6811, 4736, 6127]
    parallel_sat = [7135, 6000, 6344]
    
    x = np.arange(len(solvers))
    bars1 = ax2.bar(x - width/2, direct_sat, width, label='Direct', color='#abd0eb')
    bars2 = ax2.bar(x + width/2, parallel_sat, width, label='Parallel', color='#3988c5')
    
    ax2.set_ylabel('SAT Solved Count')
    ax2.set_title('SMT-COMP QF_NIA (10,043 instances)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(solvers)
    ax2.legend()
    ax2.set_axisbelow(True)
    ax2.yaxis.grid(True, color='#EEEEEE')
    
    plt.tight_layout()
    plt.savefig('RQ3_parallel_portfolio.pdf', format='pdf', bbox_inches='tight')
    print("Saved: RQ3_parallel_portfolio.pdf")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="COMPASS Experimental Results Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/show_results.py              # Show all RQ results
    python scripts/show_results.py --rq 1       # Show only RQ1 results
    python scripts/show_results.py --save-plots # Save plots to PDF files
        """
    )
    parser.add_argument('--rq', type=int, choices=[1, 2, 3],
                        help='Show results for specific RQ (1, 2, or 3)')
    parser.add_argument('--save-plots', action='store_true',
                        help='Save plots to PDF files')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("COMPASS: Reinforcement Learning and LLM-Guided Variable Concretization")
    print("        for Efficient SMT Solving")
    print("=" * 80)
    
    if args.rq is None:
        # Show all RQs
        show_rq1(args.save_plots)
        show_rq2(args.save_plots)
        show_rq3(args.save_plots)
    elif args.rq == 1:
        show_rq1(args.save_plots)
    elif args.rq == 2:
        show_rq2(args.save_plots)
    elif args.rq == 3:
        show_rq3(args.save_plots)
    
    print("\n" + "=" * 80)
    print("End of Results")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
