#!/usr/bin/env python3
"""
检查info_dict文件使用情况的脚本
用于确定哪些info_dict文件是当前使用的，哪些可以归档
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def get_active_info_dicts():
    """获取当前活跃使用的info_dict文件列表"""
    active_files = set()
    
    # 1. 检查各solver_process目录下的info_dict文件
    solver_dirs = [
        'test_rl/test_cvc5/z3_process',
        'test_rl/test_cvc5/cvc5_process', 
        'test_rl/test_cvc5/mathsat5_process',
        'test_rl/test_cvc5/bvparti_process',
        'test_rl/test_QF_NIA/z3_process_QF_NIA',
        'test_rl/test_QF_NIA/cvc5_process_QF_NIA',
        'test_rl/test_QF_NIA/mathsat5_process_QF_NIA',
        'test_rl/test_QF_NIA/ariparti_process_QF_NIA',
    ]
    
    for dir_path in solver_dirs:
        if os.path.exists(dir_path):
            for f in os.listdir(dir_path):
                if f.startswith('info_dict') and f.endswith('.txt'):
                    active_files.add(os.path.join(dir_path, f))
    
    # 2. 检查test_solve目录下的基准文件
    test_solve_dir = 'test_rl/test_solve'
    if os.path.exists(test_solve_dir):
        for f in os.listdir(test_solve_dir):
            if f.startswith('info_dict') and f.endswith('.txt'):
                active_files.add(os.path.join(test_solve_dir, f))
    
    return active_files

def get_root_info_dicts():
    """获取test_rl根目录下的info_dict文件列表"""
    root_files = []
    test_rl_dir = 'test_rl'
    
    if os.path.exists(test_rl_dir):
        for f in os.listdir(test_rl_dir):
            if f.startswith('info_dict') and f.endswith('.txt'):
                filepath = os.path.join(test_rl_dir, f)
                stat = os.stat(filepath)
                root_files.append({
                    'path': filepath,
                    'name': f,
                    'size': stat.st_size,
                    'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                })
    
    return root_files

def analyze_info_dict_name(name):
    """分析info_dict文件名，提取关键信息"""
    info = {
        'solver': None,
        'benchmark': None,
        'llm': None,
        'date': None,
        'method': None,
    }
    
    # 提取solver
    if 'z3' in name.lower():
        info['solver'] = 'Z3'
    elif 'cvc5' in name.lower():
        info['solver'] = 'CVC5'
    elif 'mathsat' in name.lower():
        info['solver'] = 'MathSAT5'
    elif 'bvparti' in name.lower():
        info['solver'] = 'BVParti'
    elif 'ariparti' in name.lower():
        info['solver'] = 'AriParti'
    
    # 提取benchmark
    if 'SMTimer' in name:
        info['benchmark'] = 'SMTimer'
    elif 'QF_NIA' in name:
        info['benchmark'] = 'QF_NIA'
    elif 'QF_LIA' in name:
        info['benchmark'] = 'QF_LIA'
    elif 'QF_BV' in name:
        info['benchmark'] = 'QF_BV'
    elif 'smt_comp' in name:
        info['benchmark'] = 'SMT-COMP'
    
    # 提取LLM
    if 'llama3.1' in name:
        info['llm'] = 'LLaMA3.1'
    elif 'deepseek' in name:
        info['llm'] = 'DeepSeek'
    
    # 提取日期（格式如 _0628, _0728, _0310）
    date_match = re.search(r'_(\d{4})_', name)
    if date_match:
        info['date'] = date_match.group(1)
    
    # 提取方法
    if 'rl_llm_only' in name:
        info['method'] = 'LLM-only'
    elif 'rl_random' in name:
        info['method'] = 'Random'
    elif 'info_dict_rl' in name:
        info['method'] = 'RL+LLM'
    
    return info

def check_if_empty(filepath):
    """检查文件是否为空或只有很少内容"""
    try:
        size = os.path.getsize(filepath)
        if size == 0:
            return True, "空文件"
        if size < 10:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                if not content or content == '{}':
                    return True, "几乎为空"
        return False, None
    except:
        return False, None

def classify_info_dict(filepath, active_files):
    """分类info_dict文件"""
    name = os.path.basename(filepath)
    
    # 检查是否为空
    is_empty, empty_reason = check_if_empty(filepath)
    if is_empty:
        return 'DELETE', empty_reason
    
    # 检查是否在活跃列表中
    if filepath in active_files:
        return 'KEEP', "当前使用的文件"
    
    # 分析文件名
    info = analyze_info_dict_name(name)
    
    # 判断是否为旧版本
    # gai_3, gai_4, gai_5 系列是旧版本
    if 'gai_3' in name or 'gai_4' in name or 'gai_5' in name:
        return 'ARCHIVE', "旧版本实验(gai_3/4/5)"
    
    # gai_6 系列中，非最终版本的可以归档
    if 'gai_6' in name:
        # 检查是否有对应的solver_process目录版本
        # 如果有更新的版本在solver_process目录，则归档
        return 'CHECK', "需要检查是否为最终版本"
    
    # 其他命名模式的文件
    if info['benchmark'] is None and info['solver'] is None:
        return 'ARCHIVE', "无法识别的命名模式"
    
    return 'CHECK', "需要人工检查"

def main():
    print("=" * 80)
    print("info_dict 文件使用情况分析")
    print("=" * 80)
    
    # 获取活跃文件
    active_files = get_active_info_dicts()
    print(f"\n当前活跃使用的info_dict文件: {len(active_files)} 个")
    print("-" * 40)
    for f in sorted(active_files):
        print(f"  ✓ {f}")
    
    # 获取根目录文件
    root_files = get_root_info_dicts()
    print(f"\ntest_rl根目录下的info_dict文件: {len(root_files)} 个")
    print("-" * 40)
    
    # 分类统计
    categories = {
        'KEEP': [],
        'ARCHIVE': [],
        'DELETE': [],
        'CHECK': [],
    }
    
    for file_info in root_files:
        filepath = file_info['path']
        category, reason = classify_info_dict(filepath, active_files)
        categories[category].append({
            **file_info,
            'reason': reason,
            'analysis': analyze_info_dict_name(file_info['name']),
        })
    
    # 输出分类结果
    print("\n" + "=" * 80)
    print("分类结果")
    print("=" * 80)
    
    # DELETE - 可删除
    if categories['DELETE']:
        print(f"\n【可删除】({len(categories['DELETE'])} 个):")
        for f in categories['DELETE']:
            print(f"  ✗ {f['name']} - {f['reason']}")
    
    # ARCHIVE - 可归档
    if categories['ARCHIVE']:
        print(f"\n【可归档】({len(categories['ARCHIVE'])} 个):")
        for f in categories['ARCHIVE']:
            size_kb = f['size'] / 1024
            print(f"  📦 {f['name']} ({size_kb:.1f}KB, {f['mtime']}) - {f['reason']}")
    
    # KEEP - 需保留
    if categories['KEEP']:
        print(f"\n【需保留】({len(categories['KEEP'])} 个):")
        for f in categories['KEEP']:
            print(f"  ✓ {f['name']} - {f['reason']}")
    
    # CHECK - 需检查
    if categories['CHECK']:
        print(f"\n【需人工检查】({len(categories['CHECK'])} 个):")
        for f in categories['CHECK']:
            size_kb = f['size'] / 1024
            analysis = f['analysis']
            info_parts = []
            if analysis['solver']:
                info_parts.append(f"solver={analysis['solver']}")
            if analysis['benchmark']:
                info_parts.append(f"benchmark={analysis['benchmark']}")
            if analysis['method']:
                info_parts.append(f"method={analysis['method']}")
            info_str = ', '.join(info_parts) if info_parts else '未知'
            print(f"  ? {f['name']} ({size_kb:.1f}KB) - {info_str} - {f['reason']}")
    
    # 生成归档命令
    print("\n" + "=" * 80)
    print("归档命令")
    print("=" * 80)
    
    if categories['DELETE'] or categories['ARCHIVE']:
        print("\n# 删除空文件")
        for f in categories['DELETE']:
            print(f"rm '{f['path']}'")
        
        print("\n# 归档旧版本文件")
        print("mkdir -p test_rl/archived/old_info_dicts")
        for f in categories['ARCHIVE']:
            print(f"mv '{f['path']}' test_rl/archived/old_info_dicts/")

if __name__ == '__main__':
    main()
