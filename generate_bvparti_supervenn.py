#!/usr/bin/env python3
"""
生成BVParti的SuperVenn分析图
基于现有的Z3和CVC5 SuperVenn图的风格
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib_venn import venn2, venn2_circles
import numpy as np

def load_bvparti_data(file_path: str):
    """加载BVParti实验数据"""
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_supervenn_data(data):
    """分析SuperVenn数据"""
    
    baseline_solved = set()
    rl_llm_solved = set()
    
    for constraint_path, result in data.items():
        # 数据格式: [status, baseline_time, baseline_solved, timeout, rl_time, rl_solved, total_time, rl_status, baseline_solutions, rl_solutions]
        baseline_status = result[0]
        baseline_solved_flag = result[2]
        rl_solved_flag = result[5]
        rl_status = result[7]
        rl_solutions = result[9]
        
        # 判断求解成功
        baseline_success = (baseline_solved_flag == 1) or (baseline_status not in ["unknown", "failed"])
        rl_llm_success = (rl_solved_flag == 1) or (rl_status not in ["unknown", "failed"]) or (len(rl_solutions) > 0 and len(rl_solutions[0]) > 0)
        
        if baseline_success:
            baseline_solved.add(constraint_path)
        
        if rl_llm_success:
            rl_llm_solved.add(constraint_path)
    
    # 计算集合
    baseline_only = baseline_solved - rl_llm_solved
    rl_llm_only = rl_llm_solved - baseline_solved
    both_solved = baseline_solved & rl_llm_solved
    
    return {
        'baseline_only': baseline_only,
        'rl_llm_only': rl_llm_only,
        'both_solved': both_solved,
        'baseline_total': len(baseline_solved),
        'rl_llm_total': len(rl_llm_solved),
        'total_constraints': len(data)
    }

def create_supervenn_plot(stats, output_path):
    """创建SuperVenn图"""
    
    # 设置图形
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 计算数据
    baseline_only_count = len(stats['baseline_only'])
    rl_llm_only_count = len(stats['rl_llm_only'])
    both_count = len(stats['both_solved'])
    
    # 创建Venn图
    venn = venn2(subsets=(baseline_only_count, rl_llm_only_count, both_count), 
                 set_labels=('BVParti Baseline', 'RL+LLM Enhanced'), ax=ax)
    
    # 设置颜色
    if venn.get_patch_by_id('10'):  # baseline only
        venn.get_patch_by_id('10').set_facecolor('#ff9999')
        venn.get_patch_by_id('10').set_alpha(0.7)
    
    if venn.get_patch_by_id('01'):  # RL+LLM only
        venn.get_patch_by_id('01').set_facecolor('#66b3ff')
        venn.get_patch_by_id('01').set_alpha(0.7)
    
    if venn.get_patch_by_id('11'):  # both
        venn.get_patch_by_id('11').set_facecolor('#99ff99')
        venn.get_patch_by_id('11').set_alpha(0.7)
    
    # 设置标签字体大小
    for text in venn.set_labels:
        if text:
            text.set_fontsize(12)
            text.set_fontweight('bold')
    
    for text in venn.subset_labels:
        if text:
            text.set_fontsize(14)
            text.set_fontweight('bold')
    
    # 添加圆圈边框
    venn_circles = venn2_circles(subsets=(baseline_only_count, rl_llm_only_count, both_count), ax=ax)
    for circle in venn_circles:
        circle.set_linewidth(2)
        circle.set_edgecolor('black')
    
    # 设置标题
    ax.set_title('BVParti: Baseline vs RL+LLM Enhanced Solving Capability\n' + 
                f'Total Constraints: {stats["total_constraints"]} | ' +
                f'Baseline: {stats["baseline_total"]} | RL+LLM: {stats["rl_llm_total"]}',
                fontsize=14, fontweight='bold', pad=20)
    
    # 添加统计信息
    stats_text = f"""
Key Statistics:
• Baseline Only: {baseline_only_count} constraints
• RL+LLM Only: {rl_llm_only_count} constraints  
• Both Solved: {both_count} constraints
• Success Rate Improvement: {stats['baseline_total']} → {stats['rl_llm_total']} (+{stats['rl_llm_total'] - stats['baseline_total']})
• Relative Improvement: {((stats['rl_llm_total'] - stats['baseline_total']) / max(stats['baseline_total'], 1) * 100):.1f}%
"""
    
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ SuperVenn图已保存到: {output_path}")

def create_detailed_analysis_plot(stats, output_path):
    """创建详细分析图"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 左图：成功率对比
    categories = ['Baseline\nBVParti', 'RL+LLM\nEnhanced']
    success_rates = [stats['baseline_total'], stats['rl_llm_total']]
    colors = ['#ff9999', '#66b3ff']
    
    bars1 = ax1.bar(categories, success_rates, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Number of Solved Constraints', fontsize=12, fontweight='bold')
    ax1.set_title('BVParti: Solving Capability Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, max(success_rates) * 1.2)
    
    # 添加数值标签
    for bar, value in zip(bars1, success_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 添加改进箭头和百分比
    improvement = stats['rl_llm_total'] - stats['baseline_total']
    relative_improvement = (improvement / max(stats['baseline_total'], 1)) * 100
    
    ax1.annotate(f'+{improvement}\n(+{relative_improvement:.1f}%)', 
                xy=(0.5, max(success_rates) * 0.8), xytext=(0.5, max(success_rates) * 0.9),
                ha='center', va='center', fontsize=12, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # 右图：SuperVenn分解
    categories = ['Baseline\nOnly', 'RL+LLM\nOnly', 'Both\nSolved']
    values = [len(stats['baseline_only']), len(stats['rl_llm_only']), len(stats['both_solved'])]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    bars2 = ax2.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Number of Constraints', fontsize=12, fontweight='bold')
    ax2.set_title('BVParti: SuperVenn Analysis Breakdown', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)
    
    # 添加数值标签
    for bar, value in zip(bars2, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 详细分析图已保存到: {output_path}")

def main():
    """主函数"""
    
    # 文件路径
    bvparti_file = "/home/lz/PycharmProjects/Pearl/test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0728.txt"
    
    print("🔍 生成BVParti SuperVenn分析图...")
    
    # 加载和分析数据
    data = load_bvparti_data(bvparti_file)
    stats = analyze_supervenn_data(data)
    
    print(f"📊 分析结果:")
    print(f"   - 总约束数: {stats['total_constraints']}")
    print(f"   - 基线求解: {stats['baseline_total']}")
    print(f"   - RL+LLM求解: {stats['rl_llm_total']}")
    print(f"   - 仅基线: {len(stats['baseline_only'])}")
    print(f"   - 仅RL+LLM: {len(stats['rl_llm_only'])}")
    print(f"   - 两者都解: {len(stats['both_solved'])}")
    
    # 生成图表
    create_supervenn_plot(stats, "paper/pics/supervenn-bvparti-comparison.pdf")
    create_detailed_analysis_plot(stats, "paper/pics/bvparti-detailed-analysis.pdf")
    
    # 生成LaTeX代码
    latex_code = f"""
% BVParti SuperVenn图的LaTeX代码
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.8\\textwidth]{{pics/supervenn-bvparti-comparison.pdf}}
\\caption{{SuperVenn analysis of BVParti baseline vs RL+LLM enhanced solving capability. The diagram shows {len(stats['baseline_only'])} constraints solved exclusively by baseline, {len(stats['rl_llm_only'])} constraints solved exclusively by RL+LLM enhancement, and {len(stats['both_solved'])} constraints solved by both methods. Total improvement: {stats['baseline_total']} → {stats['rl_llm_total']} (+{stats['rl_llm_total'] - stats['baseline_total']} constraints, {((stats['rl_llm_total'] - stats['baseline_total']) / max(stats['baseline_total'], 1) * 100):.1f}\\% relative improvement).}}
\\label{{fig:supervenn-bvparti}}
\\end{{figure}}
"""
    
    with open("bvparti_supervenn_latex.txt", "w") as f:
        f.write(latex_code)
    
    print(f"✅ LaTeX代码已保存到: bvparti_supervenn_latex.txt")
    print(f"🎉 BVParti SuperVenn分析图生成完成！")

if __name__ == "__main__":
    main()
