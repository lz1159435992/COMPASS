#!/usr/bin/env python3
"""
分析SMTimer_z3_result_predictor.json中的求解时间分布
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import sys

def analyze_solve_times(json_file):
    """分析求解时间分布"""
    
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取元数据
    metadata = data.get('metadata', {})
    statistics = metadata.get('statistics', {})
    timing = metadata.get('timing', {})
    
    print("=== 基本统计信息 ===")
    print(f"总文件数: {statistics.get('total_files', 0):,}")
    print(f"成功求解: {statistics.get('successful_files', 0):,}")
    print(f"错误文件: {statistics.get('error_files', 0):,}")
    print(f"SAT结果: {statistics.get('sat_files', 0):,}")
    print(f"UNSAT结果: {statistics.get('unsat_files', 0):,}")
    print(f"成功率: {statistics.get('success_rate', 0):.2%}")
    print()
    
    print("=== 时间统计 ===")
    print(f"平均求解时间: {timing.get('average_solve_time', 0):.3f}秒")
    print(f"最大求解时间: {timing.get('max_solve_time', 0):.3f}秒")
    print(f"最小求解时间: {timing.get('min_solve_time', 0):.6f}秒")
    print()
    
    # 提取所有成功的求解时间
    solve_times = []
    sat_times = []
    unsat_times = []
    error_count = 0
    
    results = data.get('results', {})
    for file_path, result in results.items():
        solve_time = result.get('solve_time', -1)
        result_type = result.get('result', '')
        
        if solve_time > 0:  # 排除错误情况（solve_time = -1）
            solve_times.append(solve_time)
            if result_type == 'sat':
                sat_times.append(solve_time)
            elif result_type == 'unsat':
                unsat_times.append(solve_time)
        else:
            error_count += 1
    
    solve_times = np.array(solve_times)
    sat_times = np.array(sat_times)
    unsat_times = np.array(unsat_times)
    
    print("=== 详细时间分布分析 ===")
    print(f"有效求解时间样本数: {len(solve_times):,}")
    print(f"SAT样本数: {len(sat_times):,}")
    print(f"UNSAT样本数: {len(unsat_times):,}")
    print()
    
    # 时间分布统计
    def print_time_stats(times, label):
        if len(times) == 0:
            print(f"{label}: 无数据")
            return
            
        print(f"=== {label} 时间分布 ===")
        print(f"样本数: {len(times):,}")
        print(f"平均值: {np.mean(times):.3f}秒")
        print(f"中位数: {np.median(times):.3f}秒")
        print(f"标准差: {np.std(times):.3f}秒")
        print(f"最小值: {np.min(times):.6f}秒")
        print(f"最大值: {np.max(times):.3f}秒")
        
        # 百分位数
        percentiles = [25, 50, 75, 90, 95, 99]
        print("百分位数:")
        for p in percentiles:
            print(f"  {p}%: {np.percentile(times, p):.3f}秒")
        print()
    
    print_time_stats(solve_times, "总体")
    print_time_stats(sat_times, "SAT")
    print_time_stats(unsat_times, "UNSAT")
    
    # 时间区间分布
    print("=== 时间区间分布 ===")
    time_ranges = [
        (0, 0.01, "< 0.01秒"),
        (0.01, 0.1, "0.01-0.1秒"),
        (0.1, 1, "0.1-1秒"),
        (1, 10, "1-10秒"),
        (10, 60, "10-60秒"),
        (60, 300, "1-5分钟"),
        (300, 1200, "5-20分钟"),
        (1200, float('inf'), "> 20分钟")
    ]
    
    for min_time, max_time, label in time_ranges:
        count = np.sum((solve_times >= min_time) & (solve_times < max_time))
        percentage = count / len(solve_times) * 100 if len(solve_times) > 0 else 0
        print(f"{label}: {count:,} ({percentage:.1f}%)")
    
    print()
    
    # 超时分析（假设1200秒为超时）
    timeout_threshold = 1200
    timeout_count = np.sum(solve_times >= timeout_threshold)
    print(f"=== 超时分析 (>= {timeout_threshold}秒) ===")
    print(f"超时样本数: {timeout_count:,}")
    print(f"超时率: {timeout_count / len(solve_times) * 100:.2f}%" if len(solve_times) > 0 else "N/A")
    
    # 快速求解分析（< 1秒）
    fast_count = np.sum(solve_times < 1)
    print(f"\n=== 快速求解分析 (< 1秒) ===")
    print(f"快速求解样本数: {fast_count:,}")
    print(f"快速求解率: {fast_count / len(solve_times) * 100:.2f}%" if len(solve_times) > 0 else "N/A")
    
    return {
        'solve_times': solve_times,
        'sat_times': sat_times,
        'unsat_times': unsat_times,
        'statistics': statistics,
        'timing': timing
    }

def create_plots(analysis_data):
    """创建可视化图表"""
    solve_times = analysis_data['solve_times']
    sat_times = analysis_data['sat_times']
    unsat_times = analysis_data['unsat_times']
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('SMT求解时间分布分析', fontsize=16)
    
    # 1. 总体时间分布直方图（对数尺度）
    ax1 = axes[0, 0]
    ax1.hist(solve_times, bins=50, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('求解时间 (秒)')
    ax1.set_ylabel('频次')
    ax1.set_title('总体求解时间分布')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # 2. SAT vs UNSAT 时间比较
    ax2 = axes[0, 1]
    if len(sat_times) > 0 and len(unsat_times) > 0:
        ax2.hist([sat_times, unsat_times], bins=30, alpha=0.7, 
                label=['SAT', 'UNSAT'], color=['green', 'red'])
        ax2.set_xlabel('求解时间 (秒)')
        ax2.set_ylabel('频次')
        ax2.set_title('SAT vs UNSAT 时间分布')
        ax2.legend()
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
    
    # 3. 累积分布函数
    ax3 = axes[1, 0]
    sorted_times = np.sort(solve_times)
    cumulative = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
    ax3.plot(sorted_times, cumulative, linewidth=2)
    ax3.set_xlabel('求解时间 (秒)')
    ax3.set_ylabel('累积概率')
    ax3.set_title('累积分布函数')
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    
    # 4. 箱线图比较
    ax4 = axes[1, 1]
    if len(sat_times) > 0 and len(unsat_times) > 0:
        box_data = [sat_times, unsat_times]
        ax4.boxplot(box_data, labels=['SAT', 'UNSAT'])
        ax4.set_ylabel('求解时间 (秒)')
        ax4.set_title('SAT vs UNSAT 箱线图')
        ax4.set_yscale('log')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('solve_time_analysis.png', dpi=300, bbox_inches='tight')
    print("图表已保存为 solve_time_analysis.png")
    
    return fig

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "AriParti_sync/scripts/batch_output/bv_default/SMTimer_z3_result_predictor.json"
    
    print("正在分析求解时间分布...")
    analysis_data = analyze_solve_times(json_file)
    
    # 创建可视化图表
    try:
        create_plots(analysis_data)
    except Exception as e:
        print(f"创建图表时出错: {e}")
        print("可能需要安装matplotlib: pip install matplotlib")
