#!/usr/bin/env python3
"""
分析SMT求解时间分布 - 健壮版本
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import re

def fix_json_file(json_file):
    """尝试修复JSON文件中的格式问题"""
    print(f"尝试修复JSON文件: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试直接解析
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("尝试修复...")
        
        # 尝试一些常见的修复方法
        # 1. 移除可能的尾随逗号
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # 2. 确保文件以正确的结构结束
        if not content.strip().endswith('}'):
            content = content.strip() + '\n  }\n}'
        
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError as e2:
            print(f"修复失败: {e2}")
            return None

def analyze_solve_times_robust(json_file):
    """健壮的求解时间分析"""
    
    # 尝试读取和修复JSON文件
    data = fix_json_file(json_file)
    if data is None:
        print("无法解析JSON文件")
        return None
    
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

def create_comparison_summary(predictor_data, rl_data):
    """创建两个数据集的对比总结"""
    print("\n" + "="*60)
    print("📊 PREDICTOR vs RL 对比分析")
    print("="*60)
    
    # 基本统计对比
    print("\n=== 基本统计对比 ===")
    print(f"{'指标':<20} {'Predictor':<15} {'RL':<15} {'差异':<15}")
    print("-" * 65)
    
    pred_stats = predictor_data['statistics']
    rl_stats = rl_data['statistics']
    
    total_pred = pred_stats.get('total_files', 0)
    total_rl = rl_stats.get('total_files', 0)
    print(f"{'总文件数':<20} {total_pred:<15,} {total_rl:<15,} {total_rl-total_pred:<15,}")
    
    success_pred = pred_stats.get('successful_files', 0)
    success_rl = rl_stats.get('successful_files', 0)
    print(f"{'成功求解':<20} {success_pred:<15,} {success_rl:<15,} {success_rl-success_pred:<15,}")
    
    rate_pred = pred_stats.get('success_rate', 0)
    rate_rl = rl_stats.get('success_rate', 0)
    print(f"{'成功率':<20} {rate_pred:<15.2%} {rate_rl:<15.2%} {rate_rl-rate_pred:<15.2%}")
    
    # 时间统计对比
    print("\n=== 求解时间对比 ===")
    pred_times = predictor_data['solve_times']
    rl_times = rl_data['solve_times']
    
    print(f"{'指标':<20} {'Predictor':<15} {'RL':<15} {'改进':<15}")
    print("-" * 65)
    print(f"{'平均时间(秒)':<20} {np.mean(pred_times):<15.3f} {np.mean(rl_times):<15.3f} {(np.mean(pred_times)-np.mean(rl_times))/np.mean(pred_times)*100:<14.1f}%")
    print(f"{'中位数(秒)':<20} {np.median(pred_times):<15.3f} {np.median(rl_times):<15.3f} {(np.median(pred_times)-np.median(rl_times))/np.median(pred_times)*100:<14.1f}%")
    print(f"{'95%分位数(秒)':<20} {np.percentile(pred_times, 95):<15.3f} {np.percentile(rl_times, 95):<15.3f} {(np.percentile(pred_times, 95)-np.percentile(rl_times, 95))/np.percentile(pred_times, 95)*100:<14.1f}%")
    
    # 快速求解对比
    fast_pred = np.sum(pred_times < 1) / len(pred_times) * 100
    fast_rl = np.sum(rl_times < 1) / len(rl_times) * 100
    print(f"{'快速求解率(%)':<20} {fast_pred:<15.1f} {fast_rl:<15.1f} {fast_rl-fast_pred:<14.1f}pp")
    
    # 超时对比
    timeout_pred = np.sum(pred_times >= 1200) / len(pred_times) * 100
    timeout_rl = np.sum(rl_times >= 1200) / len(rl_times) * 100
    print(f"{'超时率(%)':<20} {timeout_pred:<15.2f} {timeout_rl:<15.2f} {timeout_rl-timeout_pred:<14.2f}pp")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"正在分析: {json_file}")
        analysis_data = analyze_solve_times_robust(json_file)
        
        # 如果是RL文件，尝试加载predictor文件进行对比
        if 'rl' in json_file.lower():
            predictor_file = json_file.replace('_rl.json', '_predictor.json')
            try:
                print(f"\n正在加载对比文件: {predictor_file}")
                predictor_data = analyze_solve_times_robust(predictor_file)
                if predictor_data:
                    create_comparison_summary(predictor_data, analysis_data)
            except Exception as e:
                print(f"无法加载对比文件: {e}")
    else:
        print("请提供JSON文件路径作为参数")
        print("用法: python analyze_solve_times_robust.py <json_file>")
