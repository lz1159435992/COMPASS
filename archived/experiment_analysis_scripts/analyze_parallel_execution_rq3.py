#!/usr/bin/env python3
"""
RQ3 Parallel Execution Analysis Script

This script analyzes the parallel execution strategy for COMPASS:
- Direct solver and COMPASS run in parallel
- Whoever finishes first wins
- Compare with baseline direct solving

Data format in QF_NIA_advanced_solver_results_all.json:
[result, time, memory, total_exec_time, cumulative_solver_time, 
 final_solve_time, cumulative_llm_time, status, assignments, history]

Status types:
- "cached_direct_solve": Direct solver result (from cache)
- "succeed": RL+LLM successfully processed (but may not have SAT result)
- "failed": RL+LLM failed
- Other (list): RL+LLM solved with specific assignments
"""

import json
import os
from collections import defaultdict

TIMEOUT = 1200  # seconds

def load_json_file(filepath):
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def analyze_parallel_execution():
    """
    Analyze parallel execution strategy:
    - For each constraint, compare direct solve time vs COMPASS time
    - Parallel strategy: min(direct_time, compass_time)
    """
    
    # Load the advanced solver results
    data = load_json_file('QF_NIA_advanced_solver_results_all.json')
    if not data:
        return None
    
    print("=" * 80)
    print("RQ3: Parallel Execution Analysis")
    print("=" * 80)
    print(f"Total constraints: {len(data)}")
    
    # Categorize results
    direct_solve = []      # cached_direct_solve
    compass_sat = []       # COMPASS solved with SAT result
    compass_other = []     # COMPASS processed but not SAT
    failed = []            # failed
    
    for key, value in data.items():
        if not isinstance(value, list) or len(value) < 8:
            continue
            
        result = value[0]
        time_taken = value[1]
        total_exec_time = value[3] if len(value) > 3 else 0
        status = str(value[7])
        
        entry = {
            'key': key,
            'result': result,
            'time': time_taken,
            'total_exec_time': total_exec_time,
            'status': status
        }
        
        if status == 'cached_direct_solve':
            direct_solve.append(entry)
        elif status == 'failed':
            failed.append(entry)
        elif result == 'sat':
            compass_sat.append(entry)
        else:
            compass_other.append(entry)
    
    # Direct solve breakdown
    direct_sat = [x for x in direct_solve if x['result'] == 'sat']
    direct_unsat = [x for x in direct_solve if x['result'] == 'unsat']
    direct_unknown = [x for x in direct_solve if x['result'] not in ['sat', 'unsat']]
    
    print(f"\nResult Distribution:")
    print(f"  Direct solve (cached): {len(direct_solve)}")
    print(f"    - SAT: {len(direct_sat)}")
    print(f"    - UNSAT: {len(direct_unsat)}")
    print(f"    - Unknown: {len(direct_unknown)}")
    print(f"  COMPASS SAT: {len(compass_sat)}")
    print(f"  COMPASS other: {len(compass_other)}")
    print(f"  Failed: {len(failed)}")
    
    # Calculate times
    direct_sat_times = [x['time'] for x in direct_sat 
                       if isinstance(x['time'], (int, float)) and x['time'] > 0]
    direct_unsat_times = [x['time'] for x in direct_unsat 
                         if isinstance(x['time'], (int, float)) and x['time'] > 0]
    
    # COMPASS execution times (capped at TIMEOUT)
    compass_exec_times = []
    for x in compass_sat:
        exec_time = x['total_exec_time']
        if isinstance(exec_time, (int, float)) and exec_time > 0:
            compass_exec_times.append(min(exec_time, TIMEOUT))
    
    print(f"\n--- Time Statistics ---")
    if direct_sat_times:
        print(f"Direct SAT avg time: {sum(direct_sat_times)/len(direct_sat_times):.2f}s")
    if direct_unsat_times:
        print(f"Direct UNSAT avg time: {sum(direct_unsat_times)/len(direct_unsat_times):.2f}s")
    if compass_exec_times:
        print(f"COMPASS SAT avg exec time: {sum(compass_exec_times)/len(compass_exec_times):.2f}s")
    
    # Calculate total times
    # Direct solving:
    # - SAT: actual time
    # - UNSAT: actual time  
    # - Unknown: timeout (1200s)
    total_direct_sat_time = sum(direct_sat_times)
    total_direct_unsat_time = sum(direct_unsat_times)
    total_direct_unknown_time = len(direct_unknown) * TIMEOUT
    total_direct_time = total_direct_sat_time + total_direct_unsat_time + total_direct_unknown_time
    
    # Parallel execution:
    # - Direct SAT: actual time (direct solver wins)
    # - Direct UNSAT: actual time (direct solver wins)
    # - COMPASS SAT: COMPASS exec time (COMPASS wins, capped at TIMEOUT)
    # - Remaining unknown: timeout
    remaining_unknown = len(direct_unknown) - len(compass_sat)
    total_compass_exec_time = sum(compass_exec_times)
    total_parallel_time = (total_direct_sat_time + total_direct_unsat_time + 
                          total_compass_exec_time + remaining_unknown * TIMEOUT)
    
    print(f"\n--- Total Time Analysis ---")
    print(f"Direct solving total: {total_direct_time:.0f}s ({total_direct_time/3600:.1f}h)")
    print(f"  - SAT: {total_direct_sat_time:.0f}s")
    print(f"  - UNSAT: {total_direct_unsat_time:.0f}s")
    print(f"  - Unknown (timeout): {total_direct_unknown_time:.0f}s")
    print(f"\nParallel execution total: {total_parallel_time:.0f}s ({total_parallel_time/3600:.1f}h)")
    print(f"  - Direct SAT: {total_direct_sat_time:.0f}s")
    print(f"  - Direct UNSAT: {total_direct_unsat_time:.0f}s")
    print(f"  - COMPASS SAT: {total_compass_exec_time:.0f}s")
    print(f"  - Remaining unknown: {remaining_unknown * TIMEOUT:.0f}s")
    
    time_saved = total_direct_time - total_parallel_time
    print(f"\nTime saved: {time_saved:.0f}s ({time_saved/3600:.1f}h)")
    print(f"Percentage reduction: {100*time_saved/total_direct_time:.2f}%")
    
    # Average per constraint
    avg_direct = total_direct_time / len(data)
    avg_parallel = total_parallel_time / len(data)
    print(f"\n--- Average Time per Constraint ---")
    print(f"Direct: {avg_direct:.1f}s")
    print(f"Parallel: {avg_parallel:.1f}s")
    print(f"Reduction: {100*(avg_direct-avg_parallel)/avg_direct:.2f}%")
    
    # Combined SAT times for parallel execution
    all_parallel_sat_times = direct_sat_times + compass_exec_times
    parallel_sat_avg = sum(all_parallel_sat_times) / len(all_parallel_sat_times) if all_parallel_sat_times else 0
    
    return {
        'total': len(data),
        'direct_sat': len(direct_sat),
        'direct_unsat': len(direct_unsat),
        'direct_unknown': len(direct_unknown),
        'compass_sat': len(compass_sat),
        'remaining_unknown': remaining_unknown,
        'direct_sat_avg_time': sum(direct_sat_times)/len(direct_sat_times) if direct_sat_times else 0,
        'compass_exec_avg_time': sum(compass_exec_times)/len(compass_exec_times) if compass_exec_times else 0,
        'parallel_sat_avg_time': parallel_sat_avg,
        'total_direct_time': total_direct_time,
        'total_parallel_time': total_parallel_time,
        'avg_direct': avg_direct,
        'avg_parallel': avg_parallel,
        'time_reduction_pct': 100*(avg_direct-avg_parallel)/avg_direct if avg_direct > 0 else 0,
        'time_saved_hours': time_saved / 3600
    }

def generate_latex_table(stats):
    """Generate LaTeX table for RQ3 results."""
    
    print("\n" + "=" * 80)
    print("LaTeX Table for Paper (Table 7)")
    print("=" * 80)
    
    combined_sat = stats['direct_sat'] + stats['compass_sat']
    
    latex = f"""
\\begin{{table}}[b]
    \\centering
    \\caption{{Performance comparison between direct solving and parallel execution on \\QFNIA{{}} (10,043 constraints)}}
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
    Direct Solving & {stats['direct_sat']} & {stats['direct_unsat']} & {stats['direct_unknown']} & {stats['direct_sat_avg_time']:.1f} & {stats['avg_direct']:.1f} & {int(stats['total_direct_time'])} \\\\
    Parallel Execution & {combined_sat} & {stats['direct_unsat']} & {stats['remaining_unknown']} & {stats['parallel_sat_avg_time']:.1f} & {stats['avg_parallel']:.1f} & {int(stats['total_parallel_time'])} \\\\
    \\bottomrule
    \\end{{tabular}}
    \\endgroup
\\end{{table}}
"""
    print(latex)
    
    print("\n" + "=" * 80)
    print("Key Statistics for Paper Text")
    print("=" * 80)
    print(f"""
Key findings for RQ3 text:
- Parallel execution converts {stats['compass_sat']} unknown cases to SAT
- SAT count increases from {stats['direct_sat']} to {combined_sat} (+{stats['compass_sat']})
- Unknown count decreases from {stats['direct_unknown']} to {stats['remaining_unknown']} (-{stats['compass_sat']})
- Average time per constraint: {stats['avg_direct']:.1f}s → {stats['avg_parallel']:.1f}s ({stats['time_reduction_pct']:.1f}% reduction)
- Total time saved: {stats['time_saved_hours']:.1f} hours
- COMPASS average execution time for solved cases: {stats['compass_exec_avg_time']:.1f}s
""")

def verify_table_data(stats):
    """Verify the data matches what's in the paper."""
    print("\n" + "=" * 80)
    print("Verification Against Paper Table")
    print("=" * 80)
    
    expected = {
        'direct_sat': 6685,
        'direct_unsat': 792,
        'direct_unknown': 2440,
        'direct_sat_avg': 18.4,
        'direct_overall_avg': 307.6,
        'direct_total': 3089045,
        'parallel_sat': 6764,
        'parallel_unknown': 2361,
        'parallel_sat_avg': 20.8,
        'parallel_overall_avg': 299.9,
        'parallel_total': 3011928
    }
    
    combined_sat = stats['direct_sat'] + stats['compass_sat']
    
    checks = [
        ('Direct SAT', stats['direct_sat'], expected['direct_sat']),
        ('Direct UNSAT', stats['direct_unsat'], expected['direct_unsat']),
        ('Direct Unknown', stats['direct_unknown'], expected['direct_unknown']),
        ('Direct SAT Avg', round(stats['direct_sat_avg_time'], 1), expected['direct_sat_avg']),
        ('Direct Overall Avg', round(stats['avg_direct'], 1), expected['direct_overall_avg']),
        ('Direct Total', int(stats['total_direct_time']), expected['direct_total']),
        ('Parallel SAT', combined_sat, expected['parallel_sat']),
        ('Parallel Unknown', stats['remaining_unknown'], expected['parallel_unknown']),
        ('Parallel SAT Avg', round(stats['parallel_sat_avg_time'], 1), expected['parallel_sat_avg']),
        ('Parallel Overall Avg', round(stats['avg_parallel'], 1), expected['parallel_overall_avg']),
        ('Parallel Total', int(stats['total_parallel_time']), expected['parallel_total']),
    ]
    
    all_pass = True
    for name, actual, expected_val in checks:
        status = "✓" if actual == expected_val else "✗"
        if actual != expected_val:
            all_pass = False
        print(f"  {status} {name}: {actual} (expected: {expected_val})")
    
    print(f"\nAll checks passed: {all_pass}")
    return all_pass

if __name__ == "__main__":
    stats = analyze_parallel_execution()
    if stats:
        generate_latex_table(stats)
        verify_table_data(stats)
