#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import argparse
from collections import defaultdict

def read_json_log_file(log_file_path):
    """
    读取JSON格式的日志文件，提取text字段
    
    Args:
        log_file_path: 日志文件路径
        
    Returns:
        list: 包含所有text字段的列表
    """
    text_contents = []
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # 解析JSON对象
                    json_obj = json.loads(line)
                    if "text" in json_obj:
                        text_contents.append(json_obj["text"])
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，直接添加整行
                    text_contents.append(line)
    except Exception as e:
        print(f"读取文件 {log_file_path} 时出错: {str(e)}")
    
    return text_contents

def collect_all_log_files(log_dir):
    """
    收集日志目录下的所有日志文件
    
    Args:
        log_dir: 日志目录路径
        
    Returns:
        list: 日志文件路径列表
    """
    log_files = []
    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.log'):
                log_path = os.path.join(root, file)
                log_files.append(log_path)
    return log_files

def extract_file_processing_segments(texts):
    """
    从日志文本列表中提取"子进程开始处理"到"完成文件"之间的约束处理段
    
    Args:
        texts: 日志文本列表
        
    Returns:
        dict: 文件路径到处理段的映射
    """
    segments = {}
    current_file = None
    current_segment = []
    
    # 正则表达式模式
    start_pattern = r'子进程开始处理: (.+)'
    end_pattern = r'完成文件 \d+/\d+: (.+)'
    
    for text in texts:
        # 检查是否是新文件的开始
        start_match = re.search(start_pattern, text)
        if start_match:
            # 如果有当前处理的文件，保存之前的段
            if current_file and current_segment:
                segments[current_file] = current_segment
            
            # 开始新文件的处理
            current_file = start_match.group(1)
            current_segment = [text]
            continue
        
        # 检查是否是文件处理的结束
        end_match = re.search(end_pattern, text)
        if end_match and current_file == end_match.group(1):
            # 添加结束行
            current_segment.append(text)
            # 保存当前段
            segments[current_file] = current_segment
            # 重置
            current_file = None
            current_segment = []
            continue
        
        # 如果正在处理文件，添加到当前段
        if current_file:
            current_segment.append(text)
    
    # 处理最后一个段
    if current_file and current_segment:
        segments[current_file] = current_segment
    
    return segments

def extract_solve_times(texts):
    """
    从日志文本中提取求解时间信息
    
    Args:
        texts: 日志文本列表
        
    Returns:
        dict: 包含求解时间信息的字典
    """
    result = {
        'line_190_times': [],  # handle_satisfiable 行的求解时间
        'line_196_times': [],  # handle_unknown 行的求解时间
        'line_203_times': [],  # handle_unsatisfiable 行的求解时间
        'total_calculated': 0,  # 根据日志计算的总求解时间
        'total_reported': 0,    # 日志中报告的最终累计求解时间
    }
    
    # 正则表达式模式
    sat_pattern = r'求解结果: sat, 本次求解耗时: (\d+\.\d+)秒'
    unknown_pattern = r'求解结果: unknown, 本次求解耗时: (\d+\.\d+)秒'
    unsat_pattern = r'求解结果: unsat, 本次求解耗时: (\d+\.\d+)秒'
    cumulative_solve_time_pattern = r'当前累计求解时间: (\d+\.\d+)秒'
    final_result_pattern = r'约束已成功求解! 最终求解耗时: (\d+\.\d+)秒, 当前累计求解时间: (\d+\.\d+)秒'
    env_data_pattern = r'总求解时间=(\d+\.\d+)秒'
    
    # 使用集合跟踪已处理的日志行，避免重复处理
    processed_lines = set()
    
    # 提取所有求解时间信息
    for text in texts:
        # 提取sat求解时间 (line 190)
        sat_match = re.search(sat_pattern, text)
        if sat_match and text not in processed_lines:
            processed_lines.add(text)
            solve_time = float(sat_match.group(1))
            result['line_190_times'].append(solve_time)
            result['total_calculated'] += solve_time
        
        # 提取unknown求解时间 (line 196)
        unknown_match = re.search(unknown_pattern, text)
        if unknown_match and text not in processed_lines:
            processed_lines.add(text)
            solve_time = float(unknown_match.group(1))
            result['line_196_times'].append(solve_time)
            result['total_calculated'] += solve_time
        
        # 提取unsat求解时间 (line 203)
        unsat_match = re.search(unsat_pattern, text)
        if unsat_match and text not in processed_lines:
            processed_lines.add(text)
            solve_time = float(unsat_match.group(1))
            result['line_203_times'].append(solve_time)
            result['total_calculated'] += solve_time
        
        # 提取最终累计求解时间
        final_match = re.search(final_result_pattern, text)
        if final_match:
            total_cumulative_time = float(final_match.group(2))
            result['total_reported'] = total_cumulative_time
        
        # 提取环境数据更新中的总求解时间
        env_data_match = re.search(env_data_pattern, text)
        if env_data_match and result['total_reported'] == 0:
            total_solve_time = float(env_data_match.group(1))
            result['total_reported'] = total_solve_time
    
    # 如果没有找到最终求解时间，则查找最后一次记录的累计求解时间
    if result['total_reported'] == 0:
        for text in reversed(texts):
            cumulative_match = re.search(cumulative_solve_time_pattern, text)
            if cumulative_match:
                result['total_reported'] = float(cumulative_match.group(1))
                break
    
    return result

def process_all_log_files(log_dir):
    """
    处理所有日志文件，提取文件处理段
    
    Args:
        log_dir: 日志目录路径
        
    Returns:
        dict: 文件路径到处理段的映射
    """
    all_segments = {}
    log_files = collect_all_log_files(log_dir)
    
    print(f"发现 {len(log_files)} 个日志文件")
    
    for log_file in log_files:
        print(f"处理日志文件: {os.path.basename(log_file)}")
        texts = read_json_log_file(log_file)
        segments = extract_file_processing_segments(texts)
        
        # 合并段
        for file_path, segment in segments.items():
            if file_path in all_segments:
                all_segments[file_path].extend(segment)
            else:
                all_segments[file_path] = segment
    
    print(f"总共提取了 {len(all_segments)} 个文件的处理段")
    return all_segments

def compare_solve_times(info_dict_path, log_dir, output_file=None):
    """
    比较info_dict中的求解时间与日志中190、196、203行的求解时间
    
    Args:
        info_dict_path: info_dict文件路径
        log_dir: 日志目录路径
        output_file: 输出文件路径，如果为None则只打印结果
        
    Returns:
        dict: 比较结果
    """
    # 加载info_dict
    with open(info_dict_path, 'r', encoding='utf-8') as f:
        info_dict = json.load(f)
    
    # 处理所有日志文件，提取文件处理段
    print(f"正在处理日志目录: {log_dir}")
    all_segments = process_all_log_files(log_dir)
    
    # 初始化结果
    results = []
    inconsistencies = []
    
    # 分析每个约束文件
    for constraint_path, info in info_dict.items():
        # 查找对应的处理段
        if constraint_path in all_segments:
            # 提取求解时间
            segment_texts = all_segments[constraint_path]
            solve_times = extract_solve_times(segment_texts)
            
            # 确保info_dict中有足够的元素
            if len(info) >= 5:
                info_dict_time = info[4]  # 总求解时间索引
                
                # 计算各行求解时间之和
                line_190_sum = sum(solve_times['line_190_times'])
                line_196_sum = sum(solve_times['line_196_times'])
                line_203_sum = sum(solve_times['line_203_times'])
                total_line_sum = line_190_sum + line_196_sum + line_203_sum
                
                # 计算与info_dict中记录的时间差异
                diff_with_info = abs(info_dict_time - total_line_sum)
                
                # 计算与日志报告的累计时间差异
                diff_with_reported = abs(solve_times['total_reported'] - total_line_sum)
                
                # 记录结果
                result = {
                    'constraint_path': constraint_path,
                    'info_dict_time': info_dict_time,
                    'log_reported_time': solve_times['total_reported'],
                    'total_line_sum': total_line_sum,
                    'line_190_sum': line_190_sum,
                    'line_196_sum': line_196_sum,
                    'line_203_sum': line_203_sum,
                    'line_190_count': len(solve_times['line_190_times']),
                    'line_196_count': len(solve_times['line_196_times']),
                    'line_203_count': len(solve_times['line_203_times']),
                    'diff_with_info': diff_with_info,
                    'diff_with_reported': diff_with_reported
                }
                
                results.append(result)
                
                # 检查不一致性
                # 如果与info_dict或报告的时间差异超过0.1秒，认为是不一致的
                if diff_with_info > 0.1 or diff_with_reported > 0.1:
                    inconsistencies.append(result)
            else:
                print(f"警告: 文件 {constraint_path} 的信息条目格式不正确")
        else:
            print(f"未找到约束 {constraint_path} 对应的日志文件")
    
    # 构建完整结果
    comparison_result = {
        'summary': {
            'total_files': len(info_dict),
            'files_analyzed': len(results),
            'inconsistent_files': len(inconsistencies)
        },
        'results': results,
        'inconsistencies': inconsistencies
    }
    
    # 保存结果到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_result, f, indent=2)
        print(f"比较结果已保存到: {output_file}")
    
    # 打印统计信息
    print("\n=== 比较统计 ===")
    print(f"总约束文件数: {comparison_result['summary']['total_files']}")
    print(f"成功分析的文件数: {comparison_result['summary']['files_analyzed']}")
    print(f"不一致的文件数: {comparison_result['summary']['inconsistent_files']}")
    
    # 打印不一致的文件
    print("\n=== 不一致的文件 ===")
    for i, inconsistency in enumerate(sorted(inconsistencies, key=lambda x: max(x['diff_with_info'], x['diff_with_reported']), reverse=True)[:10]):
        print(f"{i+1}. 约束: {inconsistency['constraint_path']}")
        print(f"   info_dict时间: {inconsistency['info_dict_time']:.3f}秒")
        print(f"   日志报告时间: {inconsistency['log_reported_time']:.3f}秒")
        print(f"   190/196/203行总和: {inconsistency['total_line_sum']:.3f}秒")
        print(f"   与info_dict差异: {inconsistency['diff_with_info']:.3f}秒")
        print(f"   与报告时间差异: {inconsistency['diff_with_reported']:.3f}秒")
        print(f"   line_190 (sat): {inconsistency['line_190_count']}次, 总计{inconsistency['line_190_sum']:.3f}秒")
        print(f"   line_196 (unknown): {inconsistency['line_196_count']}次, 总计{inconsistency['line_196_sum']:.3f}秒")
        print(f"   line_203 (unsat): {inconsistency['line_203_count']}次, 总计{inconsistency['line_203_sum']:.3f}秒")
        print()
    
    return comparison_result

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='比较info_dict中的求解时间与日志中190、196、203行的求解时间')
    parser.add_argument('info_dict_path', nargs='?',
                        help='info_dict文件路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt')
    parser.add_argument('log_dir', nargs='?',
                        help='日志目录路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/log/run_2025-06-27_23-37-26')
    parser.add_argument('--output', '-o',
                        help='输出文件路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/solve_times_comparison.json')
    
    args = parser.parse_args()
    
    compare_solve_times(args.info_dict_path, args.log_dir, args.output)

if __name__ == "__main__":
    main() 