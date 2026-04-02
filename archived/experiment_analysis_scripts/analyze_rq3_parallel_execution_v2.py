#!/usr/bin/env python3
"""
RQ3 并行执行分析脚本 V2 - 基于三个原始数据源

数据源:
1. QF_NIA_test.json: 测试对象列表 (10,043 个约束的 key)
2. NIA.json: 直接求解器结果 [result, time, memory, model]
3. info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt: COMPASS 结果

COMPASS 结果格式:
- 长度 6: [result, solver_time, memory, exec_time, status, assignments]
  - status='failed' 表示 COMPASS 失败
- 长度 8: [result, solver_time, memory, exec_time, status, final_time, final_assignment, history]
  - status='succeed' 表示 COMPASS 成功

并行执行策略:
- 求解器和 COMPASS 同时运行
- 谁先完成用谁的结果
- 如果直接求解是 unknown，检查 COMPASS 是否能解决
"""

import json
import ast
import os
from collections import defaultdict

TIMEOUT = 1200  # 超时时间 (秒)

def load_json_file(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_txt_dict(filepath):
    """加载 Python dict 格式的 txt 文件"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return ast.literal_eval(content)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def normalize_key(key):
    """标准化 key，提取文件路径的关键部分"""
    if 'QF_NIA' in key:
        idx = key.find('QF_NIA')
        return key[idx:]
    return key

def analyze_parallel_execution():
    """分析并行执行策略"""
    
    # 文件路径
    test_file = '/home/<USER>/PycharmProjects/Pearl/test_rl/predictor/smt_comp_NIA/QF_NIA_test.json'
    direct_file = '/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json'
    compass_file = '/home/<USER>/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt'
    
    # 加载数据
    print("=" * 80)
    print("加载数据文件...")
    print("=" * 80)
    
    test_data = load_json_file(test_file)
    direct_data = load_json_file(direct_file)
    compass_data = load_txt_dict(compass_file)
    
    if not all([test_data, direct_data, compass_data]):
        print("数据加载失败!")
        return None
    
    print(f"测试对象: {len(test_data)} 个")
    print(f"直接求解结果: {len(direct_data)} 个")
    print(f"COMPASS 结果: {len(compass_data)} 个")
    
    # 创建标准化的 key 映射
    direct_normalized = {}
    for k, v in direct_data.items():
        norm_key = normalize_key(k)
        direct_normalized[norm_key] = v
    
    compass_normalized = {}
    for k, v in compass_data.items():
        norm_key = normalize_key(k)
        compass_normalized[norm_key] = v
    
    # 分析 COMPASS 数据
    print("\n" + "=" * 80)
    print("COMPASS 数据分析...")
    print("=" * 80)
    
    compass_sat = 0
    compass_unknown = 0
    compass_failed = 0
    compass_succeed = 0
    
    for k, v in compass_normalized.items():
        if isinstance(v, list):
            result = str(v[0]).lower() if v[0] else 'unknown'
            if result == 'sat':
                compass_sat += 1
            else:
                compass_unknown += 1
            
            if len(v) >= 5:
                status = v[4]
                if status == 'failed':
                    compass_failed += 1
                elif status == 'succeed':
                    compass_succeed += 1
    
    print(f"COMPASS SAT: {compass_sat}")
    print(f"COMPASS Unknown: {compass_unknown}")
    print(f"COMPASS Failed 状态: {compass_failed}")
    print(f"COMPASS Succeed 状态: {compass_succeed}")
    
    # 分析直接求解 unknown 案例在 COMPASS 中的结果
    print("\n" + "=" * 80)
    print("分析直接求解 Unknown 案例...")
    print("=" * 80)
    
    direct_unknown_keys = []
    for k, v in direct_normalized.items():
        if isinstance(v, list) and len(v) >= 1:
            result = str(v[0]).lower() if v[0] else 'unknown'
            if result == 'unknown':
                direct_unknown_keys.append(k)
    
    print(f"直接求解 Unknown 案例数: {len(direct_unknown_keys)}")
    
    # 检查这些 unknown 案例在 COMPASS 中的结果
    compass_solved = 0
    compass_not_solved = 0
    compass_not_found = 0
    compass_solved_times = []
    
    for k in direct_unknown_keys:
        compass_result = compass_normalized.get(k)
        if compass_result and isinstance(compass_result, list):
            result = str(compass_result[0]).lower() if compass_result[0] else 'unknown'
            if result == 'sat':
                compass_solved += 1
                # 获取 COMPASS 执行时间
                exec_time = compass_result[3] if len(compass_result) > 3 else TIMEOUT
                if isinstance(exec_time, (int, float)):
                    compass_solved_times.append(min(exec_time, TIMEOUT))
            else:
                compass_not_solved += 1
        else:
            compass_not_found += 1
    
    print(f"\n直接求解 Unknown 案例在 COMPASS 中的结果:")
    print(f"  COMPASS 成功解决 (unknown -> sat): {compass_solved}")
    print(f"  COMPASS 未解决: {compass_not_solved}")
    print(f"  COMPASS 无结果: {compass_not_found}")
    
    if compass_solved_times:
        print(f"\nCOMPASS 成功解决案例的执行时间:")
        print(f"  平均时间: {sum(compass_solved_times)/len(compass_solved_times):.1f}s")
        print(f"  最小时间: {min(compass_solved_times):.1f}s")
        print(f"  最大时间: {max(compass_solved_times):.1f}s")
    
    # 计算并行执行的统计数据
    print("\n" + "=" * 80)
    print("计算并行执行统计...")
    print("=" * 80)
    
    # 统计变量
    stats = {
        'total': 0,
        'direct': {
            'sat': 0, 'unsat': 0, 'unknown': 0,
            'sat_times': [], 'unsat_times': [],
            'total_time': 0
        },
        'parallel': {
            'sat': 0, 'unsat': 0, 'unknown': 0,
            'sat_times': [], 'unsat_times': [],
            'total_time': 0
        }
    }
    
    for test_key in test_data.keys():
        norm_key = normalize_key(test_key)
        
        # 获取直接求解结果
        direct_result = direct_normalized.get(norm_key)
        if not direct_result or not isinstance(direct_result, list) or len(direct_result) < 2:
            continue
        
        stats['total'] += 1
        
        direct_status = str(direct_result[0]).lower() if direct_result[0] else 'unknown'
        direct_time = direct_result[1] if isinstance(direct_result[1], (int, float)) else TIMEOUT
        direct_time = min(direct_time, TIMEOUT)
        
        # 统计直接求解结果
        if direct_status == 'sat':
            stats['direct']['sat'] += 1
            stats['direct']['sat_times'].append(direct_time)
            stats['direct']['total_time'] += direct_time
        elif direct_status == 'unsat':
            stats['direct']['unsat'] += 1
            stats['direct']['unsat_times'].append(direct_time)
            stats['direct']['total_time'] += direct_time
        else:
            stats['direct']['unknown'] += 1
            stats['direct']['total_time'] += TIMEOUT
        
        # 获取 COMPASS 结果
        compass_result = compass_normalized.get(norm_key)
        
        # 并行执行逻辑
        if direct_status in ['sat', 'unsat']:
            # 直接求解已经有结果，使用直接求解结果
            parallel_status = direct_status
            parallel_time = direct_time
        else:
            # 直接求解是 unknown，检查 COMPASS
            if compass_result and isinstance(compass_result, list):
                compass_status = str(compass_result[0]).lower() if compass_result[0] else 'unknown'
                compass_exec_time = compass_result[3] if len(compass_result) > 3 else TIMEOUT
                compass_exec_time = min(compass_exec_time, TIMEOUT) if isinstance(compass_exec_time, (int, float)) else TIMEOUT
                
                if compass_status == 'sat':
                    parallel_status = 'sat'
                    parallel_time = compass_exec_time
                else:
                    parallel_status = 'unknown'
                    parallel_time = TIMEOUT
            else:
                parallel_status = 'unknown'
                parallel_time = TIMEOUT
        
        # 统计并行执行结果
        if parallel_status == 'sat':
            stats['parallel']['sat'] += 1
            stats['parallel']['sat_times'].append(parallel_time)
            stats['parallel']['total_time'] += parallel_time
        elif parallel_status == 'unsat':
            stats['parallel']['unsat'] += 1
            stats['parallel']['unsat_times'].append(parallel_time)
            stats['parallel']['total_time'] += parallel_time
        else:
            stats['parallel']['unknown'] += 1
            stats['parallel']['total_time'] += TIMEOUT
    
    return stats, compass_solved, compass_solved_times

def print_analysis(stats, compass_solved, compass_solved_times):
    """打印分析结果"""
    
    print("\n" + "=" * 80)
    print("最终分析结果")
    print("=" * 80)
    
    total = stats['total']
    print(f"总约束数: {total}")
    
    # 直接求解统计
    print("\n--- 直接求解 (Direct Solving) ---")
    d = stats['direct']
    print(f"  SAT: {d['sat']} ({100*d['sat']/total:.1f}%)")
    print(f"  UNSAT: {d['unsat']} ({100*d['unsat']/total:.1f}%)")
    print(f"  Unknown: {d['unknown']} ({100*d['unknown']/total:.1f}%)")
    
    direct_sat_avg = sum(d['sat_times'])/len(d['sat_times']) if d['sat_times'] else 0
    direct_unsat_avg = sum(d['unsat_times'])/len(d['unsat_times']) if d['unsat_times'] else 0
    print(f"  SAT 平均时间: {direct_sat_avg:.1f}s")
    print(f"  UNSAT 平均时间: {direct_unsat_avg:.1f}s")
    
    direct_total_time = d['total_time']
    print(f"  总时间: {direct_total_time:.0f}s ({direct_total_time/3600:.1f}h)")
    print(f"  平均时间: {direct_total_time/total:.1f}s")
    
    # 并行执行统计
    print("\n--- 并行执行 (Parallel Execution) ---")
    p = stats['parallel']
    print(f"  SAT: {p['sat']} ({100*p['sat']/total:.1f}%)")
    print(f"  UNSAT: {p['unsat']} ({100*p['unsat']/total:.1f}%)")
    print(f"  Unknown: {p['unknown']} ({100*p['unknown']/total:.1f}%)")
    
    parallel_sat_avg = sum(p['sat_times'])/len(p['sat_times']) if p['sat_times'] else 0
    parallel_unsat_avg = sum(p['unsat_times'])/len(p['unsat_times']) if p['unsat_times'] else 0
    print(f"  SAT 平均时间: {parallel_sat_avg:.1f}s")
    print(f"  UNSAT 平均时间: {parallel_unsat_avg:.1f}s")
    
    parallel_total_time = p['total_time']
    print(f"  总时间: {parallel_total_time:.0f}s ({parallel_total_time/3600:.1f}h)")
    print(f"  平均时间: {parallel_total_time/total:.1f}s")
    
    # 改进分析
    print("\n--- 改进分析 ---")
    sat_improvement = p['sat'] - d['sat']
    unknown_reduction = d['unknown'] - p['unknown']
    time_saved = direct_total_time - parallel_total_time
    
    print(f"  SAT 增加: +{sat_improvement}")
    print(f"  Unknown 减少: -{unknown_reduction}")
    print(f"  时间节省: {time_saved:.0f}s ({time_saved/3600:.1f}h)")
    print(f"  时间减少比例: {100*time_saved/direct_total_time:.2f}%")
    
    if compass_solved_times:
        avg_compass_time = sum(compass_solved_times) / len(compass_solved_times)
        print(f"\n  COMPASS 成功案例平均执行时间: {avg_compass_time:.1f}s")
        print(f"  (相比 {TIMEOUT}s 超时节省 {TIMEOUT - avg_compass_time:.1f}s)")
    
    # 生成 LaTeX 表格
    print("\n" + "=" * 80)
    print("LaTeX 表格")
    print("=" * 80)
    
    print(f"""
\\begin{{table}}[b]
    \\centering
    \\caption{{Performance comparison between direct solving and parallel execution on \\QFNIA{{}} ({total:,} constraints)}}
    \\label{{tab:parallel-execution}}
    \\begingroup
    \\setlength{{\\tabcolsep}}{{5pt}}
    \\renewcommand{{\\arraystretch}}{{0.95}}
    \\small
    \\begin{{tabular}}{{>{{\\centering\\arraybackslash}}m{{3.0cm}}
                    S[table-format=4]
                    S[table-format=3]
                    S[table-format=4]
                    S[table-format=3.1]
                    S[table-format=3.1]
                    S[table-format=7.0]}}
    \\toprule
    \\textbf{{Strategy}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{sat}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{unsat}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{unknown}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{sat}} Avg. (s)}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{Overall Avg. (s)}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{Total (s)}}}} \\\\
    \\midrule
    Direct Solving & {d['sat']} & {d['unsat']} & {d['unknown']} & {direct_sat_avg:.1f} & {direct_total_time/total:.1f} & {int(direct_total_time)} \\\\
    Parallel Execution & {p['sat']} & {p['unsat']} & {p['unknown']} & {parallel_sat_avg:.1f} & {parallel_total_time/total:.1f} & {int(parallel_total_time)} \\\\
    \\bottomrule
    \\end{{tabular}}
    \\endgroup
\\end{{table}}
""")
    
    # 与论文数据对比
    print("\n" + "=" * 80)
    print("与论文数据对比")
    print("=" * 80)
    print(f"""
论文数据 (QF_NIA_advanced_solver_results_all.json):
  Direct: SAT=6685, UNSAT=792, Unknown=2440
  Parallel: SAT=6764, UNSAT=792, Unknown=2361
  COMPASS 转换: 79 个 unknown -> sat

当前分析 (原始数据源):
  Direct: SAT={d['sat']}, UNSAT={d['unsat']}, Unknown={d['unknown']}
  Parallel: SAT={p['sat']}, UNSAT={p['unsat']}, Unknown={p['unknown']}
  COMPASS 转换: {compass_solved} 个 unknown -> sat

差异分析:
  Direct SAT 差异: {d['sat'] - 6685}
  COMPASS 转换差异: {compass_solved - 79}
""")

if __name__ == "__main__":
    result = analyze_parallel_execution()
    if result:
        stats, compass_solved, compass_solved_times = result
        print_analysis(stats, compass_solved, compass_solved_times)
