#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import argparse

def count_time_diff(analysis_file):
    """
    统计 info_dict_time < log_calculated_time 的文件数目
    
    Args:
        analysis_file: 分析结果文件路径
        
    Returns:
        dict: 统计结果
    """
    # 加载分析结果
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 初始化统计数据
    stats = {
        'total_files': len(analysis_data['details']),
        'info_less_than_calculated': 0,
        'info_greater_than_calculated': 0,
        'info_greater_small_diff': 0,  # info_dict_time > log_calculated_time 且差距小于 2 秒的文件数
        'info_greater_large_diff': 0,  # info_dict_time > log_calculated_time 且差距大于 2 秒的文件数
        'small_diff_files': 0,  # 相差小于 2 秒的文件数
        'unknown_solved_files': 0,  # 包含 unknown 结果的文件数
        'unknown_time_contribution': 0,  # unknown 求解对总时间的贡献
        'total_calculated_time': 0,  # 所有文件的总计算时间
        'large_diff_files': [],  # 存储差异特别大的文件
        'info_greater_large_diff_files': [],  # 存储 info_dict_time > log_calculated_time 且差距大于 2 秒的文件
        'info_greater_diff_distribution': {  # info_dict_time > log_calculated_time 差距分布
            '0-0.1s': 0,
            '0.1-0.5s': 0,
            '0.5-1s': 0,
            '1-2s': 0,
            '2-5s': 0,
            '5-10s': 0,
            '10-50s': 0,
            '50-100s': 0,
            '100s+': 0
        },
        'info_greater_diff_files': []  # 存储所有 info_dict_time > log_calculated_time 的文件信息
    }
    
    # 遍历所有文件数据
    for file_data in analysis_data['details']:
        info_dict_time = file_data['info_dict_time']
        log_calculated_time = file_data['log_calculated_time']
        
        # 累计总计算时间
        stats['total_calculated_time'] += log_calculated_time
        
        # 计算 unknown 结果对总时间的贡献
        line_196_sum = file_data['line_196_sum']
        if line_196_sum > 0:
            stats['unknown_solved_files'] += 1
            stats['unknown_time_contribution'] += line_196_sum
        
        # 计算时间差异百分比
        if log_calculated_time > 0:
            diff_percentage = abs(info_dict_time - log_calculated_time) / log_calculated_time * 100
        else:
            diff_percentage = 0
        
        # 统计相差小于 2 秒的文件
        if abs(info_dict_time - log_calculated_time) < 2:
            stats['small_diff_files'] += 1
        
        # 统计 info_dict_time < log_calculated_time 的文件
        if info_dict_time < log_calculated_time:
            stats['info_less_than_calculated'] += 1
            
            # 如果差异超过 50%，记录详细信息
            if diff_percentage > 50:
                unknown_percentage = (line_196_sum / log_calculated_time * 100) if log_calculated_time > 0 else 0
                
                # 获取第302行和304行的数据（如果存在）
                line_302_sum = file_data.get('line_302_sum', 0)
                line_302_count = len(file_data.get('line_302_times', []))
                line_304_sum = file_data.get('line_304_sum', 0)
                line_304_count = len(file_data.get('line_304_times', []))
                
                stats['large_diff_files'].append({
                    'constraint_path': file_data['constraint_path'],
                    'info_dict_time': info_dict_time,
                    'log_calculated_time': log_calculated_time,
                    'diff_percentage': diff_percentage,
                    'line_190_count': len(file_data['line_190_times']),
                    'line_190_sum': file_data['line_190_sum'],
                    'line_196_count': len(file_data['line_196_times']),
                    'line_196_sum': line_196_sum,
                    'unknown_percentage': unknown_percentage,
                    'line_203_count': len(file_data['line_203_times']),
                    'line_203_sum': file_data['line_203_sum'],
                    'line_302_count': line_302_count,
                    'line_302_sum': line_302_sum,
                    'line_304_count': line_304_count,
                    'line_304_sum': line_304_sum
                })
        else:
            stats['info_greater_than_calculated'] += 1
            # 记录文件信息
            diff = info_dict_time - log_calculated_time
            
            # 获取第302行和304行的数据（如果存在）
            line_302_sum = file_data.get('line_302_sum', 0)
            line_302_count = len(file_data.get('line_302_times', []))
            line_304_sum = file_data.get('line_304_sum', 0)
            line_304_count = len(file_data.get('line_304_times', []))
            
            file_info = {
                'constraint_path': file_data['constraint_path'],
                'info_dict_time': info_dict_time,
                'log_calculated_time': log_calculated_time,
                'difference': diff,
                'line_190_count': len(file_data['line_190_times']),
                'line_190_sum': file_data['line_190_sum'],
                'line_196_count': len(file_data['line_196_times']),
                'line_196_sum': line_196_sum,
                'line_203_count': len(file_data['line_203_times']),
                'line_203_sum': file_data['line_203_sum'],
                'line_302_count': line_302_count,
                'line_302_sum': line_302_sum,
                'line_304_count': line_304_count,
                'line_304_sum': line_304_sum
            }
            stats['info_greater_diff_files'].append(file_info)
            
            # 统计差距分布
            if diff < 0.1:
                stats['info_greater_diff_distribution']['0-0.1s'] += 1
            elif diff < 0.5:
                stats['info_greater_diff_distribution']['0.1-0.5s'] += 1
            elif diff < 1:
                stats['info_greater_diff_distribution']['0.5-1s'] += 1
            elif diff < 2:
                stats['info_greater_diff_distribution']['1-2s'] += 1
            elif diff < 5:
                stats['info_greater_diff_distribution']['2-5s'] += 1
            elif diff < 10:
                stats['info_greater_diff_distribution']['5-10s'] += 1
            elif diff < 50:
                stats['info_greater_diff_distribution']['10-50s'] += 1
            elif diff < 100:
                stats['info_greater_diff_distribution']['50-100s'] += 1
            else:
                stats['info_greater_diff_distribution']['100s+'] += 1
            
            # 判断 info_dict_time > log_calculated_time 的文件中差距是否小于 2 秒
            if diff < 2:
                stats['info_greater_small_diff'] += 1
            else:
                stats['info_greater_large_diff'] += 1
                # 记录差距大于 2 秒的文件详情
                stats['info_greater_large_diff_files'].append(file_info)
    
    # 计算 unknown 结果占总时间的百分比
    unknown_percentage = (stats['unknown_time_contribution'] / stats['total_calculated_time'] * 100) if stats['total_calculated_time'] > 0 else 0
    
    # 打印统计结果
    print(f"总文件数: {stats['total_files']}")
    print(f"info_dict_time < log_calculated_time 的文件数: {stats['info_less_than_calculated']} ({stats['info_less_than_calculated']/stats['total_files']*100:.2f}%)")
    print(f"info_dict_time >= log_calculated_time 的文件数: {stats['info_greater_than_calculated']} ({stats['info_greater_than_calculated']/stats['total_files']*100:.2f}%)")
    print(f"  其中差距小于 2 秒的文件数: {stats['info_greater_small_diff']} ({stats['info_greater_small_diff']/stats['info_greater_than_calculated']*100:.2f}%)")
    print(f"  其中差距大于 2 秒的文件数: {stats['info_greater_large_diff']} ({stats['info_greater_large_diff']/stats['info_greater_than_calculated']*100:.2f}%)")
    print(f"info_dict_time 与 log_calculated_time 相差小于 2 秒的文件数: {stats['small_diff_files']} ({stats['small_diff_files']/stats['total_files']*100:.2f}%)")
    print(f"包含 unknown 结果的文件数: {stats['unknown_solved_files']} ({stats['unknown_solved_files']/stats['total_files']*100:.2f}%)")
    print(f"unknown 求解总时间: {stats['unknown_time_contribution']:.2f}秒")
    print(f"所有文件总计算时间: {stats['total_calculated_time']:.2f}秒")
    print(f"unknown 求解时间占总时间比例: {unknown_percentage:.2f}%")
    
    # 打印 info_dict_time > log_calculated_time 差距分布情况
    print("\ninfo_dict_time > log_calculated_time 差距分布情况:")
    for range_name, count in stats['info_greater_diff_distribution'].items():
        if stats['info_greater_than_calculated'] > 0:
            percentage = count / stats['info_greater_than_calculated'] * 100
        else:
            percentage = 0
        print(f"  差距 {range_name}: {count} 个文件 ({percentage:.2f}%)")
    
    # 打印差异特别大的文件
    print("\n差异特别大的文件 (info_dict_time < log_calculated_time 且差异 > 50%):")
    for i, file_info in enumerate(sorted(stats['large_diff_files'], key=lambda x: x['diff_percentage'], reverse=True)[:10]):
        print(f"{i+1}. {file_info['constraint_path']}")
        print(f"   info_dict_time: {file_info['info_dict_time']:.3f}秒")
        print(f"   log_calculated_time: {file_info['log_calculated_time']:.3f}秒")
        print(f"   差异: {file_info['diff_percentage']:.2f}%")
        print(f"   line_190 (sat): {file_info['line_190_count']}次, 总计{file_info['line_190_sum']:.3f}秒 ({file_info['line_190_sum']/file_info['log_calculated_time']*100:.2f}%)")
        print(f"   line_196 (unknown): {file_info['line_196_count']}次, 总计{file_info['line_196_sum']:.3f}秒 ({file_info['unknown_percentage']:.2f}%)")
        print(f"   line_203 (unsat): {file_info['line_203_count']}次, 总计{file_info['line_203_sum']:.3f}秒 ({file_info['line_203_sum']/file_info['log_calculated_time']*100:.2f}%)")
        
        # 打印第302行和304行的信息（如果存在）
        if 'line_302_count' in file_info and file_info['line_302_count'] > 0:
            line_302_percentage = (file_info['line_302_sum'] / file_info['log_calculated_time'] * 100) if file_info['log_calculated_time'] > 0 else 0
            print(f"   line_302 (变量相关断言求解成功): {file_info['line_302_count']}次, 总计{file_info['line_302_sum']:.3f}秒 ({line_302_percentage:.2f}%)")
        if 'line_304_count' in file_info and file_info['line_304_count'] > 0:
            line_304_percentage = (file_info['line_304_sum'] / file_info['log_calculated_time'] * 100) if file_info['log_calculated_time'] > 0 else 0
            print(f"   line_304 (变量相关断言求解失败: unsat/timeout): {file_info['line_304_count']}次, 总计{file_info['line_304_sum']:.3f}秒 ({line_304_percentage:.2f}%)")
        
        print()
    
    # 打印 info_dict_time > log_calculated_time 且差距大于 2 秒的文件
    print("\ninfo_dict_time > log_calculated_time 且差距大于 2 秒的文件:")
    for i, file_info in enumerate(sorted(stats['info_greater_large_diff_files'], key=lambda x: x['difference'], reverse=True)[:10]):
        print(f"{i+1}. {file_info['constraint_path']}")
        print(f"   info_dict_time: {file_info['info_dict_time']:.3f}秒")
        print(f"   log_calculated_time: {file_info['log_calculated_time']:.3f}秒")
        print(f"   差异: {file_info['difference']:.3f}秒")
        print(f"   line_190 (sat): {file_info['line_190_count']}次, 总计{file_info['line_190_sum']:.3f}秒")
        print(f"   line_196 (unknown): {file_info['line_196_count']}次, 总计{file_info['line_196_sum']:.3f}秒")
        print(f"   line_203 (unsat): {file_info['line_203_count']}次, 总计{file_info['line_203_sum']:.3f}秒")
        
        # 打印第302行和304行的信息（如果存在）
        if 'line_302_count' in file_info and file_info['line_302_count'] > 0:
            print(f"   line_302 (变量相关断言求解成功): {file_info['line_302_count']}次, 总计{file_info['line_302_sum']:.3f}秒")
        if 'line_304_count' in file_info and file_info['line_304_count'] > 0:
            print(f"   line_304 (变量相关断言求解失败: unsat/timeout): {file_info['line_304_count']}次, 总计{file_info['line_304_sum']:.3f}秒")
        
        print()
    
    # 分析 unknown 结果对差异的影响
    unknown_impact = []
    for file_data in analysis_data['details']:
        if file_data['info_dict_time'] < file_data['log_calculated_time'] and file_data['line_196_sum'] > 0:
            unknown_percentage = file_data['line_196_sum'] / file_data['log_calculated_time'] * 100
            
            # 获取第302行和304行的数据（如果存在）
            line_302_sum = file_data.get('line_302_sum', 0)
            line_304_sum = file_data.get('line_304_sum', 0)
            
            unknown_impact.append({
                'constraint_path': file_data['constraint_path'],
                'info_dict_time': file_data['info_dict_time'],
                'log_calculated_time': file_data['log_calculated_time'],
                'line_196_sum': file_data['line_196_sum'],
                'unknown_percentage': unknown_percentage,
                'line_302_sum': line_302_sum,
                'line_304_sum': line_304_sum
            })
    
    print("\nunknown 结果对时间差异的影响 (按 unknown 时间占比排序):")
    for i, file_info in enumerate(sorted(unknown_impact, key=lambda x: x['unknown_percentage'], reverse=True)[:10]):
        print(f"{i+1}. {file_info['constraint_path']}")
        print(f"   info_dict_time: {file_info['info_dict_time']:.3f}秒")
        print(f"   log_calculated_time: {file_info['log_calculated_time']:.3f}秒")
        print(f"   unknown 求解时间: {file_info['line_196_sum']:.3f}秒 ({file_info['unknown_percentage']:.2f}%)")
        
        # 打印第302行和304行的信息（如果存在且大于0）
        if file_info.get('line_302_sum', 0) > 0:
            line_302_percentage = (file_info['line_302_sum'] / file_info['log_calculated_time'] * 100) if file_info['log_calculated_time'] > 0 else 0
            print(f"   line_302 求解时间: {file_info['line_302_sum']:.3f}秒 ({line_302_percentage:.2f}%)")
        if file_info.get('line_304_sum', 0) > 0:
            line_304_percentage = (file_info['line_304_sum'] / file_info['log_calculated_time'] * 100) if file_info['log_calculated_time'] > 0 else 0
            print(f"   line_304 求解时间: {file_info['line_304_sum']:.3f}秒 ({line_304_percentage:.2f}%)")
        
        print()
    
    # 分析相差小于 2 秒的文件
    small_diff_files = []
    for file_data in analysis_data['details']:
        if abs(file_data['info_dict_time'] - file_data['log_calculated_time']) < 2:
            # 获取第302行和304行的数据（如果存在）
            line_302_sum = file_data.get('line_302_sum', 0)
            line_304_sum = file_data.get('line_304_sum', 0)
            
            small_diff_files.append({
                'constraint_path': file_data['constraint_path'],
                'info_dict_time': file_data['info_dict_time'],
                'log_calculated_time': file_data['log_calculated_time'],
                'difference': abs(file_data['info_dict_time'] - file_data['log_calculated_time']),
                'line_302_sum': line_302_sum,
                'line_304_sum': line_304_sum
            })
    
    print("\n相差小于 2 秒的文件 (按差异从小到大排序):")
    for i, file_info in enumerate(sorted(small_diff_files, key=lambda x: x['difference'])[:10]):
        print(f"{i+1}. {file_info['constraint_path']}")
        print(f"   info_dict_time: {file_info['info_dict_time']:.3f}秒")
        print(f"   log_calculated_time: {file_info['log_calculated_time']:.3f}秒")
        print(f"   差异: {file_info['difference']:.3f}秒")
        
        # 打印第302行和304行的信息（如果存在且大于0）
        if file_info.get('line_302_sum', 0) > 0:
            print(f"   line_302 求解时间: {file_info['line_302_sum']:.3f}秒")
        if file_info.get('line_304_sum', 0) > 0:
            print(f"   line_304 求解时间: {file_info['line_304_sum']:.3f}秒")
        
        print()
    
    return stats

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='统计 info_dict_time < log_calculated_time 的文件数目')
    parser.add_argument('analysis_file', nargs='?', 
                        help='分析结果文件路径',
                        default='/home/nju/PycharmProjects/Pearl/test_rl/test_cvc5/mathsat5_process/solver_time_analysis.json')
    
    args = parser.parse_args()
    
    count_time_diff(args.analysis_file)

if __name__ == "__main__":
    main() 