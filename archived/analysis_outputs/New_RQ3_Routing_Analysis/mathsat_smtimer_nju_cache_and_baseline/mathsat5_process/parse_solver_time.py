#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def parse_log_file(log_file_path):
    """
    解析日志文件，提取求解相关的时间信息
    
    Args:
        log_file_path: 日志文件路径
        
    Returns:
        dict: 包含各种时间统计的字典
    """
    # 初始化结果字典
    result = {
        'file_path': None,
        'total_execution_time': 0,
        'total_solve_time_reported': 0,
        'total_solve_time_calculated': 0,
        'unknown_solve_time': 0,
        'sat_solve_time': 0,
        'unsat_solve_time': 0,
        'error_solve_time': 0,
        'llm_time': 0,
        'solve_count': {
            'total': 0,
            'sat': 0,
            'unsat': 0,
            'unknown': 0,
            'error': 0
        },
        'raw_times': [],  # 用于存储原始时间记录，用于去重前后的比较
        'deduplicated_times': []  # 用于存储去重后的时间记录
    }
    
    # 正则表达式模式
    file_pattern = r'开始处理文件 \d+/\d+: (.+)'
    solve_result_pattern = r'求解结果: (\w+), 本次求解耗时: (\d+\.\d+)秒'
    related_assertion_pattern = r'变量 .+ 的相关断言求解(成功|失败): (\w+)，耗时: (\d+\.\d+)秒，当前累计求解时间: (\d+\.\d+)秒'
    llm_time_pattern = r'LLM调用耗时: (\d+\.\d+)秒，累计LLM时间: (\d+\.\d+)秒'
    cumulative_solve_time_pattern = r'当前累计求解时间: (\d+\.\d+)秒'
    final_result_pattern = r'约束已成功求解! 最终求解耗时: (\d+\.\d+)秒, 当前累计求解时间: (\d+\.\d+)秒'
    
    # 上一次记录的累计求解时间
    last_cumulative_time = 0
    
    # 使用集合跟踪已处理的日志行，避免重复处理
    processed_solve_logs = set()
    processed_assertion_logs = set()
    
    # 更智能的去重：通过跟踪时间戳或上下文来识别重复
    # 使用字典跟踪不同类型的求解结果和时间，通过上下文进行去重
    context_dict = {}
    
    # 原始总求解时间（未去重）
    raw_total_solve_time = 0
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 提取文件路径
        file_match = re.search(file_pattern, content)
        if file_match:
            result['file_path'] = file_match.group(1)
        
        # 提取所有求解结果和时间
        solve_matches = re.finditer(solve_result_pattern, content)
        for match in solve_matches:
            # 提取整个匹配行以检查重复
            match_line = match.group(0)
            
            # 获取该行的上下文（前后各50个字符）以更好地检测重复
            start_pos = max(0, match.start() - 50)
            end_pos = min(len(content), match.end() + 50)
            context = content[start_pos:end_pos]
            
            # 记录原始时间用于比较
            result_type = match.group(1)
            solve_time = float(match.group(2))
            raw_total_solve_time += solve_time
            result['raw_times'].append((result_type, solve_time))
            
            # 使用更强大的上下文检测重复
            context_hash = hash(context)
            if context_hash in context_dict:
                # 如果上下文已经处理过，可能是重复的日志条目
                continue
            
            context_dict[context_hash] = True
            
            # 如果该行已处理过，跳过
            if match_line in processed_solve_logs:
                continue
            
            processed_solve_logs.add(match_line)
            
            # 记录去重后的时间用于比较
            result['deduplicated_times'].append((result_type, solve_time))
            
            # 更新计数
            result['solve_count']['total'] += 1
            if result_type in result['solve_count']:
                result['solve_count'][result_type] += 1
            
            # 更新时间
            if result_type == 'sat':
                result['sat_solve_time'] += solve_time
            elif result_type == 'unsat':
                result['unsat_solve_time'] += solve_time
            elif result_type == 'unknown':
                result['unknown_solve_time'] += solve_time
            else:
                result['error_solve_time'] += solve_time
        
        # 提取相关断言求解时间
        assertion_matches = re.finditer(related_assertion_pattern, content)
        for match in assertion_matches:
            # 提取整个匹配行以检查重复
            match_line = match.group(0)
            
            # 获取该行的上下文
            start_pos = max(0, match.start() - 50)
            end_pos = min(len(content), match.end() + 50)
            context = content[start_pos:end_pos]
            
            # 记录原始时间
            result_type = match.group(2)  # sat, unsat, unknown等
            solve_time = float(match.group(3))
            raw_total_solve_time += solve_time
            result['raw_times'].append((result_type, solve_time))
            
            # 使用上下文检测重复
            context_hash = hash(context)
            if context_hash in context_dict:
                continue
            
            context_dict[context_hash] = True
            
            # 如果该行已处理过，跳过
            if match_line in processed_assertion_logs:
                continue
            
            processed_assertion_logs.add(match_line)
            
            # 记录去重后的时间
            result['deduplicated_times'].append((result_type, solve_time))
            
            # 更新计数
            result['solve_count']['total'] += 1
            if result_type in result['solve_count']:
                result['solve_count'][result_type] += 1
            
            # 更新时间
            if result_type == 'sat':
                result['sat_solve_time'] += solve_time
            elif result_type == 'unsat':
                result['unsat_solve_time'] += solve_time
            elif result_type == 'unknown':
                result['unknown_solve_time'] += solve_time
            else:
                result['error_solve_time'] += solve_time
        
        # 提取LLM时间
        llm_matches = re.finditer(llm_time_pattern, content)
        last_llm_time = 0
        for match in llm_matches:
            current_llm_time = float(match.group(1))
            cumulative_llm_time = float(match.group(2))
            last_llm_time = cumulative_llm_time
        result['llm_time'] = last_llm_time  # 使用最后一个累计值
        
        # 提取最终累计求解时间
        final_matches = re.finditer(final_result_pattern, content)
        for match in final_matches:
            final_solve_time = float(match.group(1))
            total_cumulative_time = float(match.group(2))
            result['total_solve_time_reported'] = total_cumulative_time
        
        # 如果没有找到最终求解时间，则查找最后一次记录的累计求解时间
        if result['total_solve_time_reported'] == 0:
            cumulative_matches = re.finditer(cumulative_solve_time_pattern, content)
            for match in cumulative_matches:
                cumulative_time = float(match.group(1))
                last_cumulative_time = cumulative_time
            result['total_solve_time_reported'] = last_cumulative_time
    
    # 计算真正的总求解时间（所有类型结果的求解时间之和）
    result['total_solve_time_calculated'] = (
        result['sat_solve_time'] + 
        result['unsat_solve_time'] + 
        result['unknown_solve_time'] + 
        result['error_solve_time']
    )
    
    # 如果计算的时间大于报告的时间太多（超过10倍），可能是有重复记录，尝试使用报告的时间
    if result['total_solve_time_calculated'] > result['total_solve_time_reported'] * 10 and result['total_solve_time_reported'] > 0:
        print(f"警告: 计算的总求解时间 ({result['total_solve_time_calculated']}秒) 远大于报告的时间 ({result['total_solve_time_reported']}秒)，"
              f"可能存在重复日志记录，将使用报告的时间作为总求解时间")
        
        # 记录去重前后的时间差异
        result['time_reduction'] = {
            'before_deduplication': raw_total_solve_time,
            'after_deduplication': result['total_solve_time_calculated'],
            'reported_time': result['total_solve_time_reported']
        }
        
        result['total_solve_time_calculated'] = result['total_solve_time_reported']
    else:
        result['time_reduction'] = {
            'before_deduplication': raw_total_solve_time,
            'after_deduplication': result['total_solve_time_calculated'],
            'reported_time': result['total_solve_time_reported']
        }
    
    # 检查报告的时间和计算的时间是否有明显差异
    time_diff = abs(result['total_solve_time_reported'] - result['total_solve_time_calculated'])
    if time_diff > 0.1 and time_diff / max(result['total_solve_time_reported'], 0.1) > 0.1:  # 允许10%的误差
        print(f"警告: 报告的求解时间 ({result['total_solve_time_reported']}秒) "
              f"与计算的求解时间 ({result['total_solve_time_calculated']}秒) 不匹配，差异: {time_diff}秒")
    
    return result

def process_log_directory(log_dir, output_file=None, verbose=True):
    """
    处理整个日志目录，分析所有日志文件
    
    Args:
        log_dir: 日志目录路径
        output_file: 输出文件路径
        verbose: 是否打印详细信息
        
    Returns:
        dict: 包含汇总统计和详细结果的字典
    """
    results = []
    files_processed = 0
    
    # 遍历日志目录中的所有文件
    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.log'):
                log_path = os.path.join(root, file)
                try:
                    result = parse_log_file(log_path)
                    result['log_file'] = log_path
                    results.append(result)
                    files_processed += 1
                    if verbose and files_processed % 10 == 0:
                        print(f"已处理 {files_processed} 个日志文件...")
                except Exception as e:
                    if verbose:
                        print(f"处理文件 {log_path} 时出错: {str(e)}")
    
    # 汇总统计
    total_reported = sum(r['total_solve_time_reported'] for r in results)
    total_calculated = sum(r['total_solve_time_calculated'] for r in results)
    total_unknown = sum(r['unknown_solve_time'] for r in results)
    total_sat = sum(r['sat_solve_time'] for r in results)
    total_unsat = sum(r['unsat_solve_time'] for r in results)
    total_error = sum(r['error_solve_time'] for r in results)
    total_llm = sum(r['llm_time'] for r in results)
    
    # 统计求解结果计数
    solve_counts = {
        'total': sum(r['solve_count']['total'] for r in results),
        'sat': sum(r['solve_count']['sat'] for r in results),
        'unsat': sum(r['solve_count']['unsat'] for r in results),
        'unknown': sum(r['solve_count']['unknown'] for r in results),
        'error': sum(r['solve_count']['error'] for r in results)
    }
    
    # 文件有差异的统计
    files_with_diff = [r for r in results if abs(r['total_solve_time_reported'] - r['total_solve_time_calculated']) > 0.1]
    total_diff = sum(abs(r['total_solve_time_reported'] - r['total_solve_time_calculated']) for r in files_with_diff)
    
    summary = {
        'files_processed': files_processed,
        'files_with_time_diff': len(files_with_diff),
        'total_time_diff': total_diff,
        'total_solve_time_reported': total_reported,
        'total_solve_time_calculated': total_calculated,
        'total_unknown_time': total_unknown,
        'total_sat_time': total_sat,
        'total_unsat_time': total_unsat,
        'total_error_time': total_error,
        'total_llm_time': total_llm,
        'solve_counts': solve_counts
    }
    
    # 构建完整结果
    output_data = {
        'summary': summary,
        'details': results
    }
    
    # 打印汇总信息
    if verbose:
        print("\n=== 日志分析汇总 ===")
        print(f"总共处理文件数: {files_processed}")
        print(f"有时间差异的文件数: {len(files_with_diff)}")
        print(f"总时间差异: {total_diff:.2f}秒")
        print(f"报告的总求解时间: {total_reported:.2f}秒")
        print(f"计算的总求解时间: {total_calculated:.2f}秒")
        print(f"总求解次数: {solve_counts['total']}")
        print(f"  其中sat: {solve_counts['sat']}")
        print(f"  其中unsat: {solve_counts['unsat']}")
        print(f"  其中unknown: {solve_counts['unknown']}")
        print(f"  其中error: {solve_counts['error']}")
    
    # 保存详细结果到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        if verbose:
            print(f"\n详细结果已保存到: {output_file}")
    
    return output_data

def correct_info_dict(info_dict_path, log_dir, output_path=None, verbose=True):
    """
    根据日志信息修正info_dict中的求解时间
    
    Args:
        info_dict_path: 信息字典文件路径
        log_dir: 日志目录路径
        output_path: 输出文件路径，默认为原文件名加上'_corrected'
        verbose: 是否打印详细信息
        
    Returns:
        dict: 修正后的信息字典
    """
    if output_path is None:
        base, ext = os.path.splitext(info_dict_path)
        output_path = f"{base}_corrected{ext}"
    
    # 加载原始信息字典
    with open(info_dict_path, 'r', encoding='utf-8') as f:
        info_dict = json.load(f)
    
    # 处理日志目录，获取所有文件的分析结果
    results = []
    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.log'):
                log_path = os.path.join(root, file)
                try:
                    result = parse_log_file(log_path)
                    if result['file_path']:
                        results.append(result)
                except Exception as e:
                    if verbose:
                        print(f"处理文件 {log_path} 时出错: {str(e)}")
    
    # 根据文件路径创建查找字典
    result_by_path = {r['file_path']: r for r in results if r['file_path']}
    
    # 统计信息
    corrected_count = 0
    unchanged_count = 0
    missing_count = 0
    
    # 修正info_dict中的求解时间
    for file_path, info in info_dict.items():
        if file_path in result_by_path:
            result = result_by_path[file_path]
            
            # 信息字典中的条目至少应该有5个元素才能进行修正
            if len(info) >= 5:
                # 检查报告的时间和计算的时间是否有差异
                reported_time = info[4]  # 总求解时间索引
                calculated_time = result['total_solve_time_calculated']
                
                # 如果差异大于0.1秒，则进行修正
                if abs(reported_time - calculated_time) > 0.1:
                    if verbose:
                        print(f"修正文件 {file_path} 的求解时间：{reported_time}秒 -> {calculated_time}秒")
                    info[4] = calculated_time
                    corrected_count += 1
                else:
                    unchanged_count += 1
            else:
                if verbose:
                    print(f"警告: 文件 {file_path} 的信息条目格式不正确，无法修正")
        else:
            missing_count += 1
    
    # 保存修正后的字典
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info_dict, f, indent=4)
        
        if verbose:
            print(f"\n修正后的字典已保存到: {output_path}")
    
    # 打印汇总信息
    if verbose:
        print("\n=== 修正汇总 ===")
        print(f"总共处理文件数: {len(info_dict)}")
        print(f"已修正的文件数: {corrected_count}")
        print(f"无需修正的文件数: {unchanged_count}")
        print(f"在日志中未找到的文件数: {missing_count}")
    
    # 返回修正后的字典
    return info_dict

def visualize_time_reduction(log_analysis, output_file=None):
    """
    可视化去重前后的时间差异
    
    Args:
        log_analysis: 日志分析结果字典
        output_file: 输出图表的文件路径，如果为None则显示图表
    """
    if not log_analysis.get('details'):
        print("没有足够的数据用于可视化")
        return
    
    # 提取数据
    labels = []
    before_times = []
    after_times = []
    reported_times = []
    
    for i, file_data in enumerate(log_analysis['details']):
        if 'time_reduction' in file_data:
            labels.append(f"日志 {i+1}")
            before_times.append(file_data['time_reduction']['before_deduplication'])
            after_times.append(file_data['time_reduction']['after_deduplication'])
            reported_times.append(file_data['time_reduction']['reported_time'])
    
    if not labels:
        print("没有找到去重前后的时间数据")
        return
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(labels))
    width = 0.25
    
    # 绘制柱状图
    rects1 = ax.bar(x - width, before_times, width, label='去重前的总时间')
    rects2 = ax.bar(x, after_times, width, label='去重后的计算时间')
    rects3 = ax.bar(x + width, reported_times, width, label='日志报告的时间')
    
    # 添加标签和标题
    ax.set_xlabel('日志文件')
    ax.set_ylabel('时间（秒）')
    ax.set_title('日志文件求解时间去重前后对比')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # 添加数值标签
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}',
                       xy=(rect.get_x() + rect.get_width() / 2, height),
                       xytext=(0, 3),  # 3点垂直偏移
                       textcoords="offset points",
                       ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    fig.tight_layout()
    
    # 保存或显示图表
    if output_file:
        plt.savefig(output_file)
        print(f"时间差异图表已保存到: {output_file}")
    else:
        plt.show()
    
    plt.close()

def analyze_and_correct(info_dict_path, log_dir, output_info_dict_path=None, output_analysis_path=None, output_visualization_path=None, verbose=True):
    """
    一站式函数：分析日志文件并修正信息字典中的时间数据
    
    Args:
        info_dict_path: 信息字典文件路径
        log_dir: 日志目录路径
        output_info_dict_path: 修正后的信息字典输出路径，如果为None则使用默认路径
        output_analysis_path: 分析结果的输出路径，如果为None则使用默认路径
        output_visualization_path: 可视化图表的输出路径，如果为None则不生成图表
        verbose: 是否输出详细信息
        
    Returns:
        tuple: (分析结果字典, 修正结果字典)
    """
    if verbose:
        print("=== 执行日志分析和字典修正 ===")
        print(f"找到日志目录: {log_dir}")
        print(f"找到信息字典: {os.path.basename(info_dict_path)}")
        print()
        print("开始分析和修正...")
    
    # 如果输出路径为None，则使用默认路径
    if output_info_dict_path is None:
        output_info_dict_path = "info_dict_corrected.txt"
    if output_analysis_path is None:
        output_analysis_path = "log_analysis.json"
    
    # 第一步：分析日志文件
    if verbose:
        print("=== 第一步：分析日志文件 ===")
    log_analysis = process_log_directory(log_dir, output_analysis_path, verbose=False)
    
    # 输出分析结果摘要
    if verbose:
        print("\n=== 日志分析汇总 ===")
        print(f"总共处理文件数: {log_analysis['summary']['files_processed']}")
        print(f"有时间差异的文件数: {log_analysis['summary']['files_with_time_diff']}")
        print(f"总时间差异: {log_analysis['summary']['total_time_diff']:.2f}秒")
        print(f"报告的总求解时间: {log_analysis['summary']['total_solve_time_reported']:.2f}秒")
        print(f"计算的总求解时间: {log_analysis['summary']['total_solve_time_calculated']:.2f}秒")
        print(f"总求解次数: {log_analysis['summary']['solve_counts']['total']}")
        print(f"  其中sat: {log_analysis['summary']['solve_counts']['sat']}")
        print(f"  其中unsat: {log_analysis['summary']['solve_counts']['unsat']}")
        print(f"  其中unknown: {log_analysis['summary']['solve_counts']['unknown']}")
        print(f"  其中error: {log_analysis['summary']['solve_counts']['error']}")
        print()
        print(f"详细结果已保存到: {output_analysis_path}")
        print()
    
    # 第二步：修正信息字典
    if verbose:
        print("=== 第二步：修正信息字典 ===")
    correction_result = correct_info_dict(info_dict_path, log_dir, output_info_dict_path, verbose=False)
    
    # 可视化时间差异
    if output_visualization_path:
        visualize_time_reduction(log_analysis, output_visualization_path)
        if verbose:
            print(f"\n时间差异可视化已保存到: {output_visualization_path}")
    
    # 输出修正结果摘要
    if verbose:
        print("\n=== 修正汇总 ===")
        print(f"总共处理文件数: {correction_result['total_files']}")
        print(f"已修正的文件数: {correction_result['corrected_files']}")
        print(f"无需修正的文件数: {correction_result['unchanged_files']}")
        print(f"在日志中未找到的文件数: {correction_result['not_found_files']}")
        print()
        print("=== 处理完成 ===")
        
        # 最终摘要
        print("\n=== 执行结果摘要 ===")
        print(f"分析了 {log_analysis['summary']['files_processed']} 个日志文件")
        print(f"发现 {log_analysis['summary']['files_with_time_diff']} 个文件的时间记录不准确")
        print(f"总时间差异: {log_analysis['summary']['total_time_diff']:.2f}秒")
        print(f"修正后的字典已保存到: {output_info_dict_path}")
        print(f"分析结果已保存到: {output_analysis_path}")
        if output_visualization_path:
            print(f"时间差异可视化已保存到: {output_visualization_path}")
    
    return log_analysis, correction_result

def main():
    # 解析命令行参数
    if len(argparse.sys.argv) >= 3:
        info_dict_path = argparse.sys.argv[1]
        log_dir = argparse.sys.argv[2]
        output_info_dict_path = argparse.sys.argv[3] if len(argparse.sys.argv) >= 4 else "info_dict_corrected.txt"
        output_analysis_path = argparse.sys.argv[4] if len(argparse.sys.argv) >= 5 else "log_analysis.json"
        output_visualization_path = argparse.sys.argv[5] if len(argparse.sys.argv) >= 6 else "time_reduction_visualization.png"
    else:
        # 使用默认值
        info_dict_path = "info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt"
        log_dir = "log/run_2025-06-27_23-37-26"
        output_info_dict_path = "info_dict_corrected.txt"
        output_analysis_path = "log_analysis.json"
        output_visualization_path = "time_reduction_visualization.png"
    
    # 执行分析和修正
    analyze_and_correct(
        info_dict_path, 
        log_dir, 
        output_info_dict_path, 
        output_analysis_path,
        output_visualization_path
    )

if __name__ == "__main__":
    main()
 