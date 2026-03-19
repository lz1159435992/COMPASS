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

def check_info_greater_files(analysis_file, log_dir):
    """
    检查 info_dict_time > log_calculated_time 且差距大于 10 秒的文件，并验证日志数据是否正确
    
    Args:
        analysis_file: 分析结果文件路径
        log_dir: 日志目录路径
        
    Returns:
        dict: 检查结果
    """
    # 加载分析结果
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 处理所有日志文件，提取文件处理段
    print(f"正在处理日志目录: {log_dir}")
    all_segments = process_all_log_files(log_dir)
    
    # 初始化结果
    info_greater_files = []
    
    # 遍历所有文件数据
    for file_data in analysis_data['details']:
        info_dict_time = file_data['info_dict_time']
        log_calculated_time = file_data['log_calculated_time']
        constraint_path = file_data['constraint_path']
        
        # 只检查 info_dict_time > log_calculated_time 且差距大于 10 秒的文件
        if info_dict_time > log_calculated_time and (info_dict_time - log_calculated_time) > 10:
            # 检查日志数据是否正确
            verification_result = {
                'constraint_path': constraint_path,
                'info_dict_time': info_dict_time,
                'log_calculated_time': log_calculated_time,
                'difference': info_dict_time - log_calculated_time,
                'line_190_count': len(file_data['line_190_times']),
                'line_190_sum': file_data['line_190_sum'],
                'line_196_count': len(file_data['line_196_times']),
                'line_196_sum': file_data['line_196_sum'],
                'line_203_count': len(file_data['line_203_times']),
                'line_203_sum': file_data['line_203_sum'],
                'verification': 'not_found'
            }
            
            # 验证日志数据
            if constraint_path in all_segments:
                segment_texts = all_segments[constraint_path]
                
                # 统计求解时间
                sat_times = []
                unknown_times = []
                unsat_times = []
                line_302_times = []  # 新增: 第302行的求解时间
                line_304_times = []  # 新增: 第304行的求解时间 (unsat/timeout)
                reported_time = 0
                
                # 正则表达式模式
                sat_pattern = r'求解结果: sat, 本次求解耗时: (\d+\.\d+)秒'
                unknown_pattern = r'求解结果: unknown, 本次求解耗时: (\d+\.\d+)秒'
                unsat_pattern = r'求解结果: unsat, 本次求解耗时: (\d+\.\d+)秒'
                final_result_pattern = r'约束已成功求解! 最终求解耗时: (\d+\.\d+)秒, 当前累计求解时间: (\d+\.\d+)秒'
                
                # 新增: 第302行和304行的模式
                line_302_pattern = r'__mp_main__:step:302 - 变量 .+ 的相关断言求解成功：sat，耗时: (\d+\.\d+)秒'
                line_304_pattern = r'__mp_main__:step:304 - 变量 .+ 的相关断言求解失败: (unsat|timeout)，耗时: (\d+\.\d+)秒'
                
                # 使用集合跟踪已处理的日志行，避免重复处理
                processed_lines = set()
                
                # 提取所有求解时间信息
                for text in segment_texts:
                    # 提取sat求解时间 (line 190)
                    sat_match = re.search(sat_pattern, text)
                    if sat_match and text not in processed_lines:
                        processed_lines.add(text)
                        solve_time = float(sat_match.group(1))
                        sat_times.append(solve_time)
                    
                    # 提取unknown求解时间 (line 196)
                    unknown_match = re.search(unknown_pattern, text)
                    if unknown_match and text not in processed_lines:
                        processed_lines.add(text)
                        solve_time = float(unknown_match.group(1))
                        unknown_times.append(solve_time)
                    
                    # 提取unsat求解时间 (line 203)
                    unsat_match = re.search(unsat_pattern, text)
                    if unsat_match and text not in processed_lines:
                        processed_lines.add(text)
                        solve_time = float(unsat_match.group(1))
                        unsat_times.append(solve_time)
                    
                    # 新增: 提取第302行的求解时间
                    line_302_match = re.search(line_302_pattern, text)
                    if line_302_match and text not in processed_lines:
                        processed_lines.add(text)
                        solve_time = float(line_302_match.group(1))
                        line_302_times.append(solve_time)
                    
                    # 新增: 提取第304行的求解时间 (变量相关断言求解失败: unsat或timeout)
                    line_304_match = re.search(line_304_pattern, text)
                    if line_304_match and text not in processed_lines:
                        processed_lines.add(text)
                        solve_time = float(line_304_match.group(2))  # 注意：组索引从1变为2，因为现在有两个捕获组
                        line_304_times.append(solve_time)
                    
                    # 提取最终累计求解时间
                    final_match = re.search(final_result_pattern, text)
                    if final_match:
                        reported_time = float(final_match.group(2))
                
                # 计算总求解时间
                sat_sum = sum(sat_times)
                unknown_sum = sum(unknown_times)
                unsat_sum = sum(unsat_times)
                line_302_sum = sum(line_302_times)  # 新增: 第302行求解时间总和
                line_304_sum = sum(line_304_times)  # 新增: 第304行求解时间总和
                
                # 新增: 包含新增行的总求解时间
                total_sum = sat_sum + unknown_sum + unsat_sum + line_302_sum + line_304_sum
                
                # 验证结果
                verification_result['verified_sat_count'] = len(sat_times)
                verification_result['verified_sat_sum'] = sat_sum
                verification_result['verified_unknown_count'] = len(unknown_times)
                verification_result['verified_unknown_sum'] = unknown_sum
                verification_result['verified_unsat_count'] = len(unsat_times)
                verification_result['verified_unsat_sum'] = unsat_sum
                
                # 新增: 第302行和304行的统计
                verification_result['verified_line_302_count'] = len(line_302_times)
                verification_result['verified_line_302_sum'] = line_302_sum
                verification_result['verified_line_304_count'] = len(line_304_times)
                verification_result['verified_line_304_sum'] = line_304_sum
                
                verification_result['verified_total_sum'] = total_sum
                verification_result['verified_reported_time'] = reported_time
                
                # 检查数据是否一致
                sat_count_match = len(sat_times) == verification_result['line_190_count']
                sat_sum_match = abs(sat_sum - verification_result['line_190_sum']) < 0.001
                unknown_count_match = len(unknown_times) == verification_result['line_196_count']
                unknown_sum_match = abs(unknown_sum - verification_result['line_196_sum']) < 0.001
                unsat_count_match = len(unsat_times) == verification_result['line_203_count']
                unsat_sum_match = abs(unsat_sum - verification_result['line_203_sum']) < 0.001
                
                # 修改: 总时间现在包括新增的行
                old_total_sum = sat_sum + unknown_sum + unsat_sum
                old_total_match = abs(old_total_sum - log_calculated_time) < 0.001
                new_total_match = abs(total_sum - log_calculated_time) < 0.001
                
                # 修改: 验证逻辑，考虑新增行的情况
                if (sat_count_match and sat_sum_match and 
                    unknown_count_match and unknown_sum_match and 
                    unsat_count_match and unsat_sum_match and 
                    (old_total_match or new_total_match)):
                    verification_result['verification'] = 'correct'
                else:
                    verification_result['verification'] = 'incorrect'
                    verification_result['mismatch_details'] = {
                        'sat_count_match': sat_count_match,
                        'sat_sum_match': sat_sum_match,
                        'unknown_count_match': unknown_count_match,
                        'unknown_sum_match': unknown_sum_match,
                        'unsat_count_match': unsat_count_match,
                        'unsat_sum_match': unsat_sum_match,
                        'old_total_match': old_total_match,
                        'new_total_match': new_total_match
                    }
            
            info_greater_files.append(verification_result)
    
    # 按差距排序
    info_greater_files.sort(key=lambda x: x['difference'], reverse=True)
    
    # 打印结果
    print(f"\n找到 {len(info_greater_files)} 个 info_dict_time > log_calculated_time 且差距大于 10 秒的文件")
    
    # 打印验证结果统计
    verification_stats = {'correct': 0, 'incorrect': 0, 'not_found': 0}
    for file_info in info_greater_files:
        verification_stats[file_info['verification']] += 1
    
    print(f"验证结果统计:")
    print(f"  数据正确: {verification_stats['correct']} 个文件")
    print(f"  数据不正确: {verification_stats['incorrect']} 个文件")
    print(f"  未找到日志: {verification_stats['not_found']} 个文件")
    
    # 打印差距最大的10个文件
    print("\n差距最大的10个文件:")
    for i, file_info in enumerate(info_greater_files[:10]):
        print(f"{i+1}. {file_info['constraint_path']}")
        print(f"   info_dict_time: {file_info['info_dict_time']:.3f}秒")
        print(f"   log_calculated_time: {file_info['log_calculated_time']:.3f}秒")
        print(f"   差异: {file_info['difference']:.3f}秒")
        print(f"   验证结果: {file_info['verification']}")
        
        if file_info['verification'] != 'not_found':
            print(f"   原始数据:")
            print(f"     line_190 (sat): {file_info['line_190_count']}次, 总计{file_info['line_190_sum']:.3f}秒")
            print(f"     line_196 (unknown): {file_info['line_196_count']}次, 总计{file_info['line_196_sum']:.3f}秒")
            print(f"     line_203 (unsat): {file_info['line_203_count']}次, 总计{file_info['line_203_sum']:.3f}秒")
            print(f"   验证数据:")
            print(f"     line_190 (sat): {file_info['verified_sat_count']}次, 总计{file_info['verified_sat_sum']:.3f}秒")
            print(f"     line_196 (unknown): {file_info['verified_unknown_count']}次, 总计{file_info['verified_unknown_sum']:.3f}秒")
            print(f"     line_203 (unsat): {file_info['verified_unsat_count']}次, 总计{file_info['verified_unsat_sum']:.3f}秒")
            
            # 新增: 打印第302行和304行的统计
            if 'verified_line_302_count' in file_info:
                print(f"     line_302 (sat): {file_info['verified_line_302_count']}次, 总计{file_info['verified_line_302_sum']:.3f}秒")
            if 'verified_line_304_count' in file_info:
                print(f"     line_304 (unsat/timeout): {file_info['verified_line_304_count']}次, 总计{file_info['verified_line_304_sum']:.3f}秒")
            
            # 修改: 打印新旧总时间
            old_total_sum = file_info['verified_sat_sum'] + file_info['verified_unknown_sum'] + file_info['verified_unsat_sum']
            new_total_sum = old_total_sum
            if 'verified_line_302_sum' in file_info:
                new_total_sum += file_info['verified_line_302_sum']
            if 'verified_line_304_sum' in file_info:
                new_total_sum += file_info['verified_line_304_sum']
            
            print(f"     旧总计: {old_total_sum:.3f}秒")
            print(f"     新总计(含302/304行): {new_total_sum:.3f}秒")
            print(f"     报告时间: {file_info['verified_reported_time']:.3f}秒")
            
            if file_info['verification'] == 'incorrect':
                print(f"   不匹配详情:")
                for key, value in file_info['mismatch_details'].items():
                    print(f"     {key}: {value}")
        
        print()
    
    # 保存结果到文件
    output_file = 'info_greater_files_check.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(info_greater_files, f, indent=2)
    
    print(f"详细结果已保存到: {output_file}")
    
    return info_greater_files

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='检查 info_dict_time > log_calculated_time 且差距大于 10 秒的文件，并验证日志数据是否正确')
    parser.add_argument('analysis_file', nargs='?', 
                        help='分析结果文件路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/solver_time_analysis.json')
    parser.add_argument('log_dir', nargs='?',
                        help='日志目录路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/log/run_2025-06-27_23-37-26')
    
    args = parser.parse_args()
    
    check_info_greater_files(args.analysis_file, args.log_dir)

if __name__ == "__main__":
    main() 