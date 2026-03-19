#!/usr/bin/env python3
"""
RQ3 并行执行模拟脚本

基于原始数据源模拟COMPASS和求解器的并行执行：
1. QF_NIA_advanced_solver_results_all_4_threshold.json: 预测+求解流程结果 (10,043个)
2. NIA.json: 直接求解器结果 [result, time, memory, model]
3. info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt: COMPASS结果

并行执行策略：
- 求解器和COMPASS同时运行
- 谁先完成（时间更短）就使用谁的结果
- 超过1200s的时间记为1200s

数据说明：
- threshold文件中status='succeed'表示RL+LLM成功运行
- threshold文件中status='cached_direct_solve'表示使用直接求解缓存
- COMPASS文件包含RL+LLM的执行结果
"""

import json
import ast
from collections import defaultdict

TIMEOUT = 1200  # 超时时间 (秒)

def load_json_file(filepath):
    """加载JSON文件"""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_txt_dict(filepath):
    """加载Python dict格式的txt文件"""
    with open(filepath, 'r') as f:
        return ast.literal_eval(f.read())

def normalize_key(key):
    """标准化key，提取文件路径的关键部分"""
    if 'QF_NIA' in key:
        idx = key.find('QF_NIA')
        return key[idx:]
    return key

def cap_time(time_val):
    """将时间限制在TIMEOUT内"""
    if isinstance(time_val, (int, float)):
        return min(time_val, TIMEOUT)
    return TIMEOUT

def get_direct_result(direct_data, key):
    """获取直接求解结果"""
    if key not in direct_data:
        return None, TIMEOUT
    
    v = direct_data[key]
    if not isinstance(v, list) or len(v) < 2:
        return 'unknown', TIMEOUT
    
    result = str(v[0]).lower() if v[0] else 'unknown'
    time_val = cap_time(v[1])
    
    # 如果结果是unknown，时间记为TIMEOUT
    if result == 'unknown':
        time_val = TIMEOUT
    
    return result, time_val

def get_compass_result(compass_data, key):
    """获取COMPASS结果"""
    if key not in compass_data:
        return None, TIMEOUT
    
    v = compass_data[key]
    if not isinstance(v, list) or len(v) < 4:
        return 'unknown', TIMEOUT
    
    result = str(v[0]).lower() if v[0] else 'unknown'
    
    # COMPASS结果格式：
    # 长度6: [result, solver_time, memory, exec_time, status, assignments]
    # 长度8: [result, solver_time, memory, exec_time, cumulative_solver_time, final_time, cumulative_llm_time, status]
    # exec_time在index 3
    exec_time = cap_time(v[3])
    
    # 如果结果是unknown，时间记为TIMEOUT
    if result == 'unknown':
        exec_time = TIMEOUT
    
    return result, exec_time

def simulate_parallel_execution():
    """模拟并行执行"""
    
    # 文件路径
    threshold_file = 'test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json'
    direct_file = '/home/lz/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json'
    compass_file = '/home/lz/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt'
    
    print("=" * 100)
    print("RQ3 并行执行模拟 - 基于原始数据源")
    print("=" * 100)
    
    # 加载数据
    print("\n加载数据文件...")
    threshold_data = load_json_file(threshold_file)
    direct_data = load_json_file(direct_file)
    compass_data = load_txt_dict(compass_file)
    
    print(f"预测+求解结果: {len(threshold_data)} 个")
    print(f"直接求解结果: {len(direct_data)} 个")
    print(f"COMPASS结果: {len(compass_data)} 个")
    
    # 分析threshold文件中的status分布
    status_counts = {}
    for k, v in threshold_data.items():
        if isinstance(v, list) and len(v) > 7:
            s = v[7]
            if isinstance(s, str):
                status_counts[s] = status_counts.get(s, 0) + 1
    
    print("\n预测+求解结果的Status分布:")
    for s, c in sorted(status_counts.items()):
        print(f"  {s}: {c}")
    
    # 创建succeed案例的执行时间映射
    succeed_times = {}
    for k, v in threshold_data.items():
        if isinstance(v, list) and len(v) > 7 and v[7] == 'succeed':
            exec_time = v[3] if len(v) > 3 else TIMEOUT
            succeed_times[k] = cap_time(exec_time)
    
    print(f"\nSucceed案例数量: {len(succeed_times)}")
    
    # 统计变量
    stats = {
        'direct': {
            'sat': 0, 'unsat': 0, 'unknown': 0,
            'sat_times': [], 'unsat_times': [], 'unknown_times': [],
            'total_time': 0
        },
        'parallel': {
            'sat': 0, 'unsat': 0, 'unknown': 0,
            'sat_times': [], 'unsat_times': [], 'unknown_times': [],
            'total_time': 0
        }
    }
    
    # 详细分析
    conversion_details = {
        'unknown_to_sat': [],  # 直接求解unknown，并行后变成sat
        'sat_faster_by_compass': [],  # 直接求解sat，但COMPASS更快
        'sat_faster_by_direct': [],  # 直接求解sat，直接求解更快
        'sat_faster_by_succeed': [],  # 直接求解sat，但succeed案例更快
    }
    
    total_processed = 0
    
    print("\n" + "=" * 100)
    print("开始模拟并行执行...")
    print("=" * 100)
    
    for test_key in threshold_data.keys():
        norm_key = test_key  # 不需要标准化，直接使用原始key
        
        # 获取直接求解结果
        direct_result, direct_time = get_direct_result(direct_data, norm_key)
        if direct_result is None:
            continue
        
        total_processed += 1
        
        # 获取COMPASS结果
        compass_result, compass_time = get_compass_result(compass_data, norm_key)
        
        # 获取succeed案例的执行时间（如果有）
        succeed_time = succeed_times.get(norm_key, None)
        
        # 统计直接求解结果
        if direct_result == 'sat':
            stats['direct']['sat'] += 1
            stats['direct']['sat_times'].append(direct_time)
        elif direct_result == 'unsat':
            stats['direct']['unsat'] += 1
            stats['direct']['unsat_times'].append(direct_time)
        else:
            stats['direct']['unknown'] += 1
            stats['direct']['unknown_times'].append(TIMEOUT)
        stats['direct']['total_time'] += direct_time if direct_result != 'unknown' else TIMEOUT
        
        # 并行执行逻辑：谁先完成用谁的结果
        # 注意：只有当结果是sat或unsat时才算"完成"
        
        # 确定并行执行的最终结果
        parallel_result = None
        parallel_time = TIMEOUT
        
        # 情况1: 直接求解有确定结果(sat/unsat)
        if direct_result in ['sat', 'unsat']:
            # 首先检查是否是succeed案例且更快
            if succeed_time is not None and succeed_time < direct_time:
                # succeed案例更快，使用succeed的时间（结果仍然是sat）
                parallel_result = direct_result
                parallel_time = succeed_time
                conversion_details['sat_faster_by_succeed'].append({
                    'key': norm_key,
                    'direct_time': direct_time,
                    'succeed_time': succeed_time,
                    'saved': direct_time - succeed_time
                })
            # 然后检查COMPASS是否也有确定结果且更快
            elif compass_result in ['sat', 'unsat'] and compass_time < direct_time:
                parallel_result = compass_result
                parallel_time = compass_time
                if direct_result == 'sat':
                    conversion_details['sat_faster_by_compass'].append({
                        'key': norm_key,
                        'direct_time': direct_time,
                        'compass_time': compass_time,
                        'saved': direct_time - compass_time
                    })
            else:
                parallel_result = direct_result
                parallel_time = direct_time
                if direct_result == 'sat' and compass_result is not None:
                    conversion_details['sat_faster_by_direct'].append({
                        'key': norm_key,
                        'direct_time': direct_time,
                        'compass_time': compass_time
                    })
        
        # 情况2: 直接求解是unknown
        else:
            # 检查COMPASS是否有确定结果
            if compass_result in ['sat', 'unsat']:
                parallel_result = compass_result
                parallel_time = compass_time
                conversion_details['unknown_to_sat'].append({
                    'key': norm_key,
                    'compass_result': compass_result,
                    'compass_time': compass_time,
                    'saved': TIMEOUT - compass_time
                })
            else:
                parallel_result = 'unknown'
                parallel_time = TIMEOUT
        
        # 统计并行执行结果
        if parallel_result == 'sat':
            stats['parallel']['sat'] += 1
            stats['parallel']['sat_times'].append(parallel_time)
        elif parallel_result == 'unsat':
            stats['parallel']['unsat'] += 1
            stats['parallel']['unsat_times'].append(parallel_time)
        else:
            stats['parallel']['unknown'] += 1
            stats['parallel']['unknown_times'].append(TIMEOUT)
        stats['parallel']['total_time'] += parallel_time
    
    # 打印结果
    print_results(stats, total_processed, conversion_details)
    
    return stats, conversion_details

def print_results(stats, total, conversion_details):
    """打印分析结果"""
    
    print("\n" + "=" * 100)
    print("分析结果")
    print("=" * 100)
    print(f"总处理约束数: {total}")
    
    # 直接求解统计
    print("\n" + "-" * 100)
    print("直接求解 (Direct Solving)")
    print("-" * 100)
    d = stats['direct']
    print(f"  SAT:     {d['sat']:>6} ({100*d['sat']/total:>5.1f}%)")
    print(f"  UNSAT:   {d['unsat']:>6} ({100*d['unsat']/total:>5.1f}%)")
    print(f"  Unknown: {d['unknown']:>6} ({100*d['unknown']/total:>5.1f}%)")
    
    direct_sat_avg = sum(d['sat_times'])/len(d['sat_times']) if d['sat_times'] else 0
    direct_unsat_avg = sum(d['unsat_times'])/len(d['unsat_times']) if d['unsat_times'] else 0
    direct_overall_avg = d['total_time'] / total
    
    print(f"\n  SAT平均时间:     {direct_sat_avg:>8.1f}s")
    print(f"  UNSAT平均时间:   {direct_unsat_avg:>8.1f}s")
    print(f"  总体平均时间:    {direct_overall_avg:>8.1f}s")
    print(f"  总时间:          {d['total_time']:>10.0f}s ({d['total_time']/3600:.1f}h)")
    
    # 并行执行统计
    print("\n" + "-" * 100)
    print("并行执行 (Parallel Execution)")
    print("-" * 100)
    p = stats['parallel']
    print(f"  SAT:     {p['sat']:>6} ({100*p['sat']/total:>5.1f}%)")
    print(f"  UNSAT:   {p['unsat']:>6} ({100*p['unsat']/total:>5.1f}%)")
    print(f"  Unknown: {p['unknown']:>6} ({100*p['unknown']/total:>5.1f}%)")
    
    parallel_sat_avg = sum(p['sat_times'])/len(p['sat_times']) if p['sat_times'] else 0
    parallel_unsat_avg = sum(p['unsat_times'])/len(p['unsat_times']) if p['unsat_times'] else 0
    parallel_overall_avg = p['total_time'] / total
    
    print(f"\n  SAT平均时间:     {parallel_sat_avg:>8.1f}s")
    print(f"  UNSAT平均时间:   {parallel_unsat_avg:>8.1f}s")
    print(f"  总体平均时间:    {parallel_overall_avg:>8.1f}s")
    print(f"  总时间:          {p['total_time']:>10.0f}s ({p['total_time']/3600:.1f}h)")
    
    # 改进分析
    print("\n" + "-" * 100)
    print("改进分析")
    print("-" * 100)
    
    sat_increase = p['sat'] - d['sat']
    unknown_decrease = d['unknown'] - p['unknown']
    time_saved = d['total_time'] - p['total_time']
    
    print(f"  SAT增加:         +{sat_increase}")
    print(f"  Unknown减少:     -{unknown_decrease}")
    print(f"  时间节省:        {time_saved:>10.0f}s ({time_saved/3600:.1f}h)")
    print(f"  时间减少比例:    {100*time_saved/d['total_time']:.2f}%")
    
    # 转换详情
    print("\n" + "-" * 100)
    print("转换详情")
    print("-" * 100)
    
    unknown_to_sat = conversion_details['unknown_to_sat']
    print(f"\n  Unknown -> SAT 转换: {len(unknown_to_sat)} 个")
    if unknown_to_sat:
        avg_compass_time = sum(x['compass_time'] for x in unknown_to_sat) / len(unknown_to_sat)
        total_saved = sum(x['saved'] for x in unknown_to_sat)
        print(f"    COMPASS平均执行时间: {avg_compass_time:.1f}s")
        print(f"    总节省时间: {total_saved:.0f}s ({total_saved/3600:.1f}h)")
        print(f"    每个案例平均节省: {total_saved/len(unknown_to_sat):.1f}s")
    
    sat_faster_compass = conversion_details['sat_faster_by_compass']
    print(f"\n  SAT案例中COMPASS更快: {len(sat_faster_compass)} 个")
    if sat_faster_compass:
        total_saved = sum(x['saved'] for x in sat_faster_compass)
        print(f"    总节省时间: {total_saved:.0f}s")
    
    sat_faster_succeed = conversion_details.get('sat_faster_by_succeed', [])
    print(f"\n  SAT案例中Succeed更快: {len(sat_faster_succeed)} 个")
    if sat_faster_succeed:
        total_saved = sum(x['saved'] for x in sat_faster_succeed)
        avg_succeed_time = sum(x['succeed_time'] for x in sat_faster_succeed) / len(sat_faster_succeed)
        avg_direct_time = sum(x['direct_time'] for x in sat_faster_succeed) / len(sat_faster_succeed)
        print(f"    总节省时间: {total_saved:.0f}s ({total_saved/3600:.1f}h)")
        print(f"    平均Succeed执行时间: {avg_succeed_time:.1f}s")
        print(f"    平均直接求解时间: {avg_direct_time:.1f}s")
    
    sat_faster_direct = conversion_details['sat_faster_by_direct']
    print(f"\n  SAT案例中直接求解更快: {len(sat_faster_direct)} 个")
    
    # 生成LaTeX表格
    print("\n" + "=" * 100)
    print("LaTeX表格")
    print("=" * 100)
    
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
                    S[table-format=4]
                    S[table-format=4]
                    S[table-format=3.1]
                    S[table-format=3.1]
                    S[table-format=7.0]}}
    \\toprule
    \\textbf{{Strategy}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{sat}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{unsat}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{unknown}}}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{\\texttt{{sat}} Avg. (s)}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{Overall Avg. (s)}}}} & \\multicolumn{{1}}{{c}}{{\\textbf{{Total (s)}}}} \\\\
    \\midrule
    Direct Solving & {d['sat']} & {d['unsat']} & {d['unknown']} & {direct_sat_avg:.1f} & {direct_overall_avg:.1f} & {int(d['total_time'])} \\\\
    Parallel Execution & {p['sat']} & {p['unsat']} & {p['unknown']} & {parallel_sat_avg:.1f} & {parallel_overall_avg:.1f} & {int(p['total_time'])} \\\\
    \\bottomrule
    \\end{{tabular}}
    \\endgroup
\\end{{table}}
""")

if __name__ == "__main__":
    stats, details = simulate_parallel_execution()
