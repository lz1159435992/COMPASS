#!/usr/bin/env python3
"""
分析QF_NIA_test.json文件的分布情况
统计求解结果、时间分布等
"""

import json
import os
import sys
from collections import defaultdict
import numpy as np

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def analyze_qf_nia_results(data):
    """分析QF_NIA结果"""
    print("=" * 80)
    print("QF_NIA Test Results Analysis")
    print("=" * 80)
    
    # 统计变量
    total_constraints = len(data)
    solved_constraints = 0
    unsolved_constraints = 0
    sat_results = 0
    unsat_results = 0
    unknown_results = 0
    error_results = 0
    
    # 时间分布统计
    time_distribution = defaultdict(int)
    all_solve_times = []
    
    # 求解器统计
    solver_stats = defaultdict(int)
    
    # 状态统计
    status_stats = defaultdict(int)
    
    print(f"Total constraints: {total_constraints}")
    print("-" * 80)
    
    for constraint_path, result in data.items():
        if isinstance(result, list) and len(result) >= 2:
            # 提取结果信息
            result_status = result[0] if len(result) > 0 else 'unknown'
            solve_time = result[1] if len(result) > 1 else 0
            
            # 统计求解状态
            if result_status == 'sat':
                sat_results += 1
                solved_constraints += 1
            elif result_status == 'unsat':
                unsat_results += 1
                solved_constraints += 1
            elif result_status == 'unknown':
                unknown_results += 1
                unsolved_constraints += 1
            else:
                error_results += 1
                unsolved_constraints += 1
            
            # 统计状态
            status_stats[result_status] += 1
            
            # 时间分布统计
            if isinstance(solve_time, (int, float)) and solve_time > 0:
                all_solve_times.append(solve_time)
                
                # 时间分段统计
                if solve_time <= 10:
                    time_distribution['0-10s'] += 1
                elif solve_time <= 30:
                    time_distribution['10-30s'] += 1
                elif solve_time <= 60:
                    time_distribution['30-60s'] += 1
                elif solve_time <= 120:
                    time_distribution['60-120s'] += 1
                elif solve_time <= 300:
                    time_distribution['120-300s'] += 1
                elif solve_time <= 600:
                    time_distribution['300-600s'] += 1
                elif solve_time <= 1200:
                    time_distribution['600-1200s'] += 1
                else:
                    time_distribution['>1200s'] += 1
    
    # 打印总体统计
    print("Overall Statistics:")
    print(f"  Total constraints: {total_constraints}")
    print(f"  Solved constraints: {solved_constraints} ({solved_constraints/total_constraints*100:.1f}%)")
    print(f"  Unsolved constraints: {unsolved_constraints} ({unsolved_constraints/total_constraints*100:.1f}%)")
    print()
    
    print("Result Distribution:")
    print(f"  SAT: {sat_results} ({sat_results/total_constraints*100:.1f}%)")
    print(f"  UNSAT: {unsat_results} ({unsat_results/total_constraints*100:.1f}%)")
    print(f"  UNKNOWN: {unknown_results} ({unknown_results/total_constraints*100:.1f}%)")
    print(f"  ERROR: {error_results} ({error_results/total_constraints*100:.1f}%)")
    print()
    
    # 时间分布统计
    if all_solve_times:
        print("Time Distribution (for solved constraints):")
        sorted_time_ranges = [
            '0-10s', '10-30s', '30-60s', '60-120s', 
            '120-300s', '300-600s', '600-1200s', '>1200s'
        ]
        
        for time_range in sorted_time_ranges:
            count = time_distribution[time_range]
            if count > 0:
                print(f"  {time_range}: {count} constraints")
        
        print()
        print("Time Statistics:")
        print(f"  Mean solve time: {np.mean(all_solve_times):.2f}s")
        print(f"  Median solve time: {np.median(all_solve_times):.2f}s")
        print(f"  Min solve time: {np.min(all_solve_times):.2f}s")
        print(f"  Max solve time: {np.max(all_solve_times):.2f}s")
        print(f"  Std solve time: {np.std(all_solve_times):.2f}s")
    
    # 成功率统计
    if solved_constraints > 0:
        success_rate = solved_constraints / total_constraints * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return {
        'total': total_constraints,
        'solved': solved_constraints,
        'unsolved': unsolved_constraints,
        'sat': sat_results,
        'unsat': unsat_results,
        'unknown': unknown_results,
        'error': error_results,
        'time_distribution': dict(time_distribution),
        'time_stats': {
            'mean': np.mean(all_solve_times) if all_solve_times else 0,
            'median': np.median(all_solve_times) if all_solve_times else 0,
            'min': np.min(all_solve_times) if all_solve_times else 0,
            'max': np.max(all_solve_times) if all_solve_times else 0,
            'std': np.std(all_solve_times) if all_solve_times else 0
        }
    }

def analyze_constraint_complexity(data):
    """分析约束复杂度分布"""
    print("\n" + "=" * 80)
    print("Constraint Complexity Analysis")
    print("=" * 80)
    
    # 统计约束特征
    variable_counts = []
    constraint_counts = []
    file_sizes = []
    
    for constraint_path, result in data.items():
        try:
            # 尝试从文件路径推断信息
            file_name = os.path.basename(constraint_path)
            
            # 统计文件大小（如果文件存在）
            if os.path.exists(constraint_path):
                file_size = os.path.getsize(constraint_path)
                file_sizes.append(file_size)
            
            # 分析求解时间作为复杂度指标
            if isinstance(result, list) and len(result) > 1:
                solve_time = result[1]
                if isinstance(solve_time, (int, float)) and solve_time > 0:
                    # 基于求解时间分类复杂度
                    if solve_time <= 10:
                        complexity = "Easy"
                    elif solve_time <= 60:
                        complexity = "Medium"
                    elif solve_time <= 300:
                        complexity = "Hard"
                    else:
                        complexity = "Very Hard"
                    
                    print(f"  {file_name}: {solve_time:.2f}s ({complexity})")
        
        except Exception as e:
            continue
    
    if file_sizes:
        print(f"\nFile Size Statistics:")
        print(f"  Mean file size: {np.mean(file_sizes):.0f} bytes")
        print(f"  Median file size: {np.median(file_sizes):.0f} bytes")
        print(f"  Min file size: {np.min(file_sizes):.0f} bytes")
        print(f"  Max file size: {np.max(file_sizes):.0f} bytes")

def analyze_time_percentiles(data):
    """分析时间百分位数"""
    print("\n" + "=" * 80)
    print("Time Percentile Analysis")
    print("=" * 80)
    
    all_times = []
    for constraint_path, result in data.items():
        if isinstance(result, list) and len(result) > 1:
            solve_time = result[1]
            if isinstance(solve_time, (int, float)) and solve_time > 0:
                all_times.append(solve_time)
    
    if all_times:
        all_times.sort()
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        
        print("Time Percentiles:")
        for p in percentiles:
            index = int(len(all_times) * p / 100)
            if index < len(all_times):
                time_value = all_times[index]
                print(f"  {p}th percentile: {time_value:.2f}s")
        
        # 分析不同时间段的约束数量
        print("\nTime Range Analysis:")
        ranges = [
            (0, 1, "0-1s"),
            (1, 5, "1-5s"),
            (5, 10, "5-10s"),
            (10, 30, "10-30s"),
            (30, 60, "30-60s"),
            (60, 120, "60-120s"),
            (120, 300, "120-300s"),
            (300, 600, "300-600s"),
            (600, 1200, "600-1200s"),
            (1200, float('inf'), ">1200s")
        ]
        
        for min_time, max_time, label in ranges:
            count = sum(1 for t in all_times if min_time <= t < max_time)
            if count > 0:
                percentage = count / len(all_times) * 100
                print(f"  {label}: {count} constraints ({percentage:.1f}%)")

def main():
    """主函数"""
    file_path = "QF_NIA_test.json"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return
    
    print(f"Analyzing file: {file_path}")
    
    # 加载数据
    data = load_json_file(file_path)
    if data is None:
        return
    
    # 分析结果
    stats = analyze_qf_nia_results(data)
    
    # 分析约束复杂度
    analyze_constraint_complexity(data)
    
    # 分析时间百分位数
    analyze_time_percentiles(data)
    
    # 保存统计结果
    output_file = "qf_nia_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    print(f"\nAnalysis results saved to: {output_file}")

if __name__ == "__main__":
    main() 