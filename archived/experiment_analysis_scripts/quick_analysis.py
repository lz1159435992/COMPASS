#!/usr/bin/env python3
"""
Quick analysis of QF_NIA experimental results for RQ5
"""

import json

def quick_analysis():
    """Quick analysis of the QF_NIA results"""
    
    # Load the data
    with open("test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json", 'r') as f:
        data = json.load(f)
    
    print(f"Total constraints analyzed: {len(data)}")
    
    # Analyze methods
    methods = {}
    results = {}
    rl_llm_cases = []
    direct_solve_cases = []
    
    for file_path, result in data.items():
        if len(result) >= 8:
            method = result[7] if len(result) > 7 else 'unknown'
            # Handle case where method might be a list
            if isinstance(method, list):
                method = str(method)
            sat_result = result[0]
            original_time = result[1] if isinstance(result[1], (int, float)) else 0

            # Count methods
            methods[method] = methods.get(method, 0) + 1
            results[sat_result] = results.get(sat_result, 0) + 1
            
            # Collect RL+LLM cases
            if method in ['succeed', 'rl_solve']:
                rl_llm_cases.append({
                    'file': file_path,
                    'result': sat_result,
                    'original_time': original_time,
                    'total_time': result[3] if len(result) > 3 else 0,
                    'llm_time': result[5] if len(result) > 5 else 0,
                    'method': method
                })
            elif method == 'cached_direct_solve':
                direct_solve_cases.append({
                    'file': file_path,
                    'result': sat_result,
                    'original_time': original_time
                })
    
    print("\nMethod Distribution:")
    for method, count in methods.items():
        percentage = count / len(data) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    print("\nResult Distribution:")
    for result, count in results.items():
        percentage = count / len(data) * 100
        print(f"  {result}: {count} ({percentage:.1f}%)")
    
    print(f"\nRL+LLM Cases: {len(rl_llm_cases)}")
    print(f"Direct Solve Cases: {len(direct_solve_cases)}")
    
    # Analyze RL+LLM performance
    if rl_llm_cases:
        sat_rl_llm = [case for case in rl_llm_cases if case['result'] == 'sat']
        print(f"\nRL+LLM Success Rate: {len(sat_rl_llm)}/{len(rl_llm_cases)} ({len(sat_rl_llm)/len(rl_llm_cases)*100:.1f}%)")
        
        # Time analysis
        total_times = [case['total_time'] for case in rl_llm_cases if case['total_time'] > 0]
        llm_times = [case['llm_time'] for case in rl_llm_cases if case['llm_time'] > 0]
        
        if total_times:
            print(f"Average RL+LLM Total Time: {sum(total_times)/len(total_times):.2f}s")
        if llm_times:
            print(f"Average LLM Time: {sum(llm_times)/len(llm_times):.2f}s")
    
    # Analyze direct solve performance
    if direct_solve_cases:
        sat_direct = [case for case in direct_solve_cases if case['result'] == 'sat']
        print(f"\nDirect Solve Success Rate: {len(sat_direct)}/{len(direct_solve_cases)} ({len(sat_direct)/len(direct_solve_cases)*100:.1f}%)")
        
        original_times = [case['original_time'] for case in direct_solve_cases if case['original_time'] > 0]
        if original_times:
            print(f"Average Direct Solve Time: {sum(original_times)/len(original_times):.2f}s")
    
    # Analyze by complexity (time-based)
    print("\nComplexity Analysis (by original solving time):")
    time_ranges = [
        ("Very Easy (≤1s)", 0, 1),
        ("Easy (1-10s)", 1, 10),
        ("Medium (10-100s)", 10, 100),
        ("Hard (100-300s)", 100, 300),
        ("Very Hard (300-1200s)", 300, 1200),
        ("Timeout (≥1200s)", 1200, float('inf'))
    ]
    
    for range_name, min_time, max_time in time_ranges:
        range_cases = []
        range_rl_llm = []
        
        for file_path, result in data.items():
            if len(result) >= 2:
                original_time = result[1] if isinstance(result[1], (int, float)) else 0
                method = result[7] if len(result) > 7 else 'unknown'
                
                if min_time <= original_time < max_time:
                    range_cases.append((file_path, result))
                    if method in ['succeed', 'rl_solve']:
                        range_rl_llm.append((file_path, result))
        
        if range_cases:
            rl_llm_percentage = len(range_rl_llm) / len(range_cases) * 100
            print(f"  {range_name}: {len(range_cases)} total, {len(range_rl_llm)} RL+LLM ({rl_llm_percentage:.1f}%)")
    
    # Sample some interesting cases
    print("\nSample RL+LLM Success Cases:")
    success_cases = [case for case in rl_llm_cases if case['result'] == 'sat'][:3]
    for i, case in enumerate(success_cases, 1):
        print(f"  {i}. Original time: {case['original_time']:.2f}s, RL+LLM time: {case['total_time']:.2f}s, LLM time: {case['llm_time']:.2f}s")
    
    return {
        'total_constraints': len(data),
        'methods': methods,
        'results': results,
        'rl_llm_cases': len(rl_llm_cases),
        'direct_solve_cases': len(direct_solve_cases)
    }

if __name__ == "__main__":
    analysis = quick_analysis()
