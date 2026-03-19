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

def fix_info_dict(info_dict_path, log_dir, output_path):
    """
    修正info_dict中的求解时间记录，基于日志中的实际求解时间
    
    Args:
        info_dict_path: info_dict文件路径
        log_dir: 日志目录路径
        output_path: 修正后的info_dict输出路径
        
    Returns:
        dict: 修正结果统计
    """
    # 加载info_dict
    with open(info_dict_path, 'r', encoding='utf-8') as f:
        info_dict = json.load(f)
    
    # 处理所有日志文件，提取文件处理段
    print(f"正在处理日志目录: {log_dir}")
    all_segments = process_all_log_files(log_dir)
    
    # 初始化修正统计
    stats = {
        'total_files': len(info_dict),
        'files_modified': 0,
        'files_not_found': 0,
        'total_time_diff_before': 0,
        'total_time_diff_after': 0
    }
    
    # 修正每个约束文件的求解时间
    fixed_info_dict = {}
    for constraint_path, info in info_dict.items():
        # 查找对应的处理段
        if constraint_path in all_segments:
            # 提取求解时间
            segment_texts = all_segments[constraint_path]
            solve_times = extract_solve_times(segment_texts)
            
            # 确保info_dict中有足够的元素
            if len(info) >= 5:
                original_time = info[4]  # 总求解时间索引
                
                # 计算各行求解时间之和
                line_190_sum = sum(solve_times['line_190_times'])
                line_196_sum = sum(solve_times['line_196_times'])
                line_203_sum = sum(solve_times['line_203_times'])
                total_line_sum = line_190_sum + line_196_sum + line_203_sum
                
                # 计算差异
                diff_before = abs(original_time - total_line_sum)
                stats['total_time_diff_before'] += diff_before
                
                # 确定要使用的时间
                # 如果日志中报告的时间存在且合理，优先使用报告的时间
                # 否则使用计算的总和
                corrected_time = solve_times['total_reported']
                if corrected_time < 0.001 or corrected_time > 1200:  # 如果报告时间不合理
                    corrected_time = total_line_sum
                
                # 如果修正后的时间与原始时间差异超过0.1秒，则进行修正
                if abs(original_time - corrected_time) > 0.1:
                    # 创建新的信息条目，替换求解时间
                    new_info = info.copy()
                    new_info[4] = corrected_time
                    fixed_info_dict[constraint_path] = new_info
                    stats['files_modified'] += 1
                    
                    # 计算修正后的差异
                    diff_after = abs(corrected_time - total_line_sum)
                    stats['total_time_diff_after'] += diff_after
                    
                    print(f"修正文件: {constraint_path}")
                    print(f"  原始时间: {original_time:.3f}秒")
                    print(f"  修正为: {corrected_time:.3f}秒")
                    print(f"  190/196/203行总和: {total_line_sum:.3f}秒")
                    print(f"  修正前差异: {diff_before:.3f}秒")
                    print(f"  修正后差异: {diff_after:.3f}秒")
                else:
                    # 如果差异不大，保持原样
                    fixed_info_dict[constraint_path] = info
            else:
                # 如果格式不正确，保持原样
                fixed_info_dict[constraint_path] = info
                print(f"警告: 文件 {constraint_path} 的信息条目格式不正确")
        else:
            # 如果未找到日志，保持原样
            fixed_info_dict[constraint_path] = info
            stats['files_not_found'] += 1
            print(f"未找到约束 {constraint_path} 对应的日志文件")
    
    # 保存修正后的info_dict
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_info_dict, f, indent=2)
    
    print(f"\n修正后的info_dict已保存到: {output_path}")
    
    # 打印统计信息
    print("\n=== 修正统计 ===")
    print(f"总约束文件数: {stats['total_files']}")
    print(f"修正的文件数: {stats['files_modified']}")
    print(f"未找到日志的文件数: {stats['files_not_found']}")
    print(f"修正前总时间差异: {stats['total_time_diff_before']:.2f}秒")
    print(f"修正后总时间差异: {stats['total_time_diff_after']:.2f}秒")
    
    return stats

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='修正info_dict中的求解时间记录，基于日志中的实际求解时间')
    parser.add_argument('info_dict_path', nargs='?',
                        help='info_dict文件路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt')
    parser.add_argument('log_dir', nargs='?',
                        help='日志目录路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/log/run_2025-06-27_23-37-26')
    parser.add_argument('output_path', nargs='?',
                        help='修正后的info_dict输出路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/fixed_info_dict.json')
    
    args = parser.parse_args()
    
    fix_info_dict(args.info_dict_path, args.log_dir, args.output_path)

if __name__ == "__main__":
    main() 