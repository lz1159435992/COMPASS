#!/usr/bin/env python3
"""
Comprehensive analysis of QF_NIA experimental results for RQ5 formulation
"""

import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

# Try to import pandas, use basic data structures if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

def load_and_parse_results(file_path):
    """Load and parse the QF_NIA results JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    parsed_results = []
    for file_path, result in data.items():
        # Parse the result structure based on observed patterns
        if len(result) >= 8:
            entry = {
                'file_path': file_path,
                'result': result[0] if result[0] else 'unknown',  # sat/unsat/unknown
                'original_time': result[1] if isinstance(result[1], (int, float)) else 0,
                'memory_limit': result[2] if len(result) > 2 else 0,
                'total_execution_time': result[3] if len(result) > 3 and isinstance(result[3], (int, float)) else 0,
                'status': result[4] if len(result) > 4 else 'unknown',
                'llm_time': result[5] if len(result) > 5 and isinstance(result[5], (int, float)) else 0,
                'final_assignments': result[6] if len(result) > 6 else [],
                'counterexamples_list': result[7] if len(result) > 7 else [],
                'method': result[8] if len(result) > 8 else 'unknown'
            }
        else:
            # Handle incomplete entries
            entry = {
                'file_path': file_path,
                'result': result[0] if len(result) > 0 else 'unknown',
                'original_time': result[1] if len(result) > 1 and isinstance(result[1], (int, float)) else 0,
                'memory_limit': result[2] if len(result) > 2 else 0,
                'total_execution_time': 0,
                'status': 'unknown',
                'llm_time': 0,
                'final_assignments': [],
                'counterexamples_list': [],
                'method': 'unknown'
            }
        
        # Extract benchmark category from file path
        path_parts = entry['file_path'].split('/')
        if 'QF_NIA' in path_parts:
            qf_nia_idx = path_parts.index('QF_NIA')
            if qf_nia_idx + 1 < len(path_parts):
                entry['benchmark_category'] = path_parts[qf_nia_idx + 1]
            else:
                entry['benchmark_category'] = 'unknown'
        else:
            entry['benchmark_category'] = 'unknown'
        
        parsed_results.append(entry)
    
    return parsed_results

def analyze_solver_performance(results):
    """Analyze solver performance metrics"""

    # Basic statistics
    total_constraints = len(results)

    # Method distribution
    method_counts = Counter(r['method'] for r in results)

    # Result distribution
    result_counts = Counter(r['result'] for r in results)

    # Status distribution for RL+LLM methods
    rl_llm_results = [r for r in results if r['status'] in ['succeed', 'rl_solve']]

    # Performance metrics
    performance_metrics = {
        'total_constraints': total_constraints,
        'method_distribution': dict(method_counts),
        'result_distribution': dict(result_counts),
        'rl_llm_success_count': len(rl_llm_results),
        'rl_llm_success_rate': len(rl_llm_results) / total_constraints * 100 if total_constraints > 0 else 0,
    }

    # Time analysis
    direct_solve = [r for r in results if r['method'] == 'cached_direct_solve']
    rl_solve = [r for r in results if r['status'] in ['succeed', 'rl_solve']]

    if len(direct_solve) > 0:
        performance_metrics['direct_solve_avg_time'] = sum(r['original_time'] for r in direct_solve) / len(direct_solve)
        direct_solve_sat = [r for r in direct_solve if r['result'] == 'sat']
        performance_metrics['direct_solve_success_rate'] = len(direct_solve_sat) / len(direct_solve) * 100

    if len(rl_solve) > 0:
        performance_metrics['rl_solve_avg_time'] = sum(r['total_execution_time'] for r in rl_solve) / len(rl_solve)
        performance_metrics['rl_solve_avg_llm_time'] = sum(r['llm_time'] for r in rl_solve) / len(rl_solve)
        rl_solve_sat = [r for r in rl_solve if r['result'] == 'sat']
        performance_metrics['rl_solve_success_rate'] = len(rl_solve_sat) / len(rl_solve) * 100

    return performance_metrics, results

def analyze_benchmark_categories(results):
    """Analyze performance across different benchmark categories"""
    category_analysis = {}

    # Get unique categories
    categories = set(r['benchmark_category'] for r in results)

    for category in categories:
        if category == 'unknown':
            continue

        category_data = [r for r in results if r['benchmark_category'] == category]

        # Method distribution within category
        method_dist = Counter(r['method'] for r in category_data)
        result_dist = Counter(r['result'] for r in category_data)

        # RL+LLM performance in this category
        rl_llm_data = [r for r in category_data if r['status'] in ['succeed', 'rl_solve']]

        category_analysis[category] = {
            'total_constraints': len(category_data),
            'method_distribution': dict(method_dist),
            'result_distribution': dict(result_dist),
            'rl_llm_count': len(rl_llm_data),
            'rl_llm_success_rate': len([r for r in rl_llm_data if r['result'] == 'sat']) / len(rl_llm_data) * 100 if len(rl_llm_data) > 0 else 0,
            'avg_original_time': sum(r['original_time'] for r in category_data) / len(category_data) if len(category_data) > 0 else 0,
            'avg_rl_llm_time': sum(r['total_execution_time'] for r in rl_llm_data) / len(rl_llm_data) if len(rl_llm_data) > 0 else 0
        }

    return category_analysis

def analyze_complexity_patterns(results):
    """Analyze patterns related to constraint complexity"""
    complexity_analysis = {}

    # Time-based complexity classification
    time_thresholds = [1, 10, 100, 300, 1200]  # seconds

    for i, threshold in enumerate(time_thresholds):
        if i == 0:
            subset = [r for r in results if r['original_time'] <= threshold]
            complexity_level = f'very_easy_<={threshold}s'
        else:
            prev_threshold = time_thresholds[i-1]
            subset = [r for r in results if prev_threshold < r['original_time'] <= threshold]
            complexity_level = f'complexity_{prev_threshold}s_to_{threshold}s'

        if len(subset) > 0:
            rl_llm_subset = [r for r in subset if r['status'] in ['succeed', 'rl_solve']]

            complexity_analysis[complexity_level] = {
                'count': len(subset),
                'rl_llm_count': len(rl_llm_subset),
                'rl_llm_success_rate': len([r for r in rl_llm_subset if r['result'] == 'sat']) / len(rl_llm_subset) * 100 if len(rl_llm_subset) > 0 else 0,
                'avg_original_time': sum(r['original_time'] for r in subset) / len(subset),
                'avg_rl_time': sum(r['total_execution_time'] for r in rl_llm_subset) / len(rl_llm_subset) if len(rl_llm_subset) > 0 else 0
            }

    # Timeout cases
    timeout_cases = [r for r in results if r['original_time'] >= 1200]
    rl_llm_timeout = [r for r in timeout_cases if r['status'] in ['succeed', 'rl_solve']]

    complexity_analysis['timeout_cases'] = {
        'count': len(timeout_cases),
        'rl_llm_count': len(rl_llm_timeout),
        'rl_llm_success_rate': len([r for r in rl_llm_timeout if r['result'] == 'sat']) / len(rl_llm_timeout) * 100 if len(rl_llm_timeout) > 0 else 0
    }

    return complexity_analysis

def analyze_llm_effectiveness(results):
    """Analyze LLM component effectiveness"""
    rl_llm_data = [r for r in results if r['status'] in ['succeed', 'rl_solve']]

    if len(rl_llm_data) == 0:
        return {}

    # LLM time analysis
    llm_times = [r['llm_time'] for r in rl_llm_data]
    llm_time_stats = {
        'mean_llm_time': sum(llm_times) / len(llm_times),
        'median_llm_time': sorted(llm_times)[len(llm_times)//2],
        'max_llm_time': max(llm_times),
        'min_llm_time': min(llm_times)
    }

    # Assignment analysis
    assignment_counts = []
    for row in rl_llm_data:
        if row['final_assignments'] and isinstance(row['final_assignments'], list):
            assignment_counts.append(len(row['final_assignments']))

    if assignment_counts:
        llm_time_stats['avg_assignments_per_solution'] = sum(assignment_counts) / len(assignment_counts)
        llm_time_stats['max_assignments_per_solution'] = max(assignment_counts)

    # Counterexample analysis
    counterexample_counts = []
    for row in rl_llm_data:
        if row['counterexamples_list'] and isinstance(row['counterexamples_list'], list):
            counterexample_counts.append(len(row['counterexamples_list']))

    if counterexample_counts:
        llm_time_stats['avg_counterexamples_per_solution'] = sum(counterexample_counts) / len(counterexample_counts)
        llm_time_stats['max_counterexamples_per_solution'] = max(counterexample_counts)

    return llm_time_stats

def generate_summary_report(performance_metrics, category_analysis, complexity_analysis, llm_effectiveness):
    """Generate a comprehensive summary report"""
    
    report = f"""
# QF_NIA Experimental Results Analysis for RQ5

## Overall Performance Summary
- Total Constraints Analyzed: {performance_metrics['total_constraints']:,}
- RL+LLM Success Count: {performance_metrics['rl_llm_success_count']}
- RL+LLM Success Rate: {performance_metrics['rl_llm_success_rate']:.2f}%

## Method Distribution
"""
    
    for method, count in performance_metrics['method_distribution'].items():
        percentage = count / performance_metrics['total_constraints'] * 100
        report += f"- {method}: {count:,} ({percentage:.1f}%)\n"
    
    report += f"""
## Result Distribution
"""
    for result, count in performance_metrics['result_distribution'].items():
        percentage = count / performance_metrics['total_constraints'] * 100
        report += f"- {result}: {count:,} ({percentage:.1f}%)\n"
    
    if 'direct_solve_avg_time' in performance_metrics:
        report += f"""
## Performance Comparison
- Direct Solve Average Time: {performance_metrics['direct_solve_avg_time']:.2f}s
- Direct Solve Success Rate: {performance_metrics.get('direct_solve_success_rate', 0):.2f}%
"""
    
    if 'rl_solve_avg_time' in performance_metrics:
        report += f"- RL+LLM Average Total Time: {performance_metrics['rl_solve_avg_time']:.2f}s\n"
        report += f"- RL+LLM Average LLM Time: {performance_metrics['rl_solve_avg_llm_time']:.2f}s\n"
        report += f"- RL+LLM Success Rate: {performance_metrics.get('rl_solve_success_rate', 0):.2f}%\n"
    
    report += f"""
## Benchmark Category Analysis
"""
    for category, data in category_analysis.items():
        report += f"""
### {category}
- Total Constraints: {data['total_constraints']:,}
- RL+LLM Applications: {data['rl_llm_count']}
- RL+LLM Success Rate: {data['rl_llm_success_rate']:.2f}%
- Average Original Time: {data['avg_original_time']:.2f}s
- Average RL+LLM Time: {data['avg_rl_llm_time']:.2f}s
"""
    
    report += f"""
## Complexity-Based Analysis
"""
    for level, data in complexity_analysis.items():
        report += f"""
### {level}
- Count: {data['count']:,}
- RL+LLM Applications: {data['rl_llm_count']}
- RL+LLM Success Rate: {data['rl_llm_success_rate']:.2f}%
- Average Original Time: {data['avg_original_time']:.2f}s
- Average RL Time: {data['avg_rl_time']:.2f}s
"""
    
    if llm_effectiveness:
        report += f"""
## LLM Component Effectiveness
- Mean LLM Time: {llm_effectiveness.get('mean_llm_time', 0):.2f}s
- Median LLM Time: {llm_effectiveness.get('median_llm_time', 0):.2f}s
- Average Assignments per Solution: {llm_effectiveness.get('avg_assignments_per_solution', 0):.1f}
- Average Counterexamples per Solution: {llm_effectiveness.get('avg_counterexamples_per_solution', 0):.1f}
"""
    
    return report

def main():
    """Main analysis function"""
    results_file = "test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json"
    
    print("Loading and parsing QF_NIA experimental results...")
    results = load_and_parse_results(results_file)
    
    print("Analyzing solver performance...")
    performance_metrics, processed_results = analyze_solver_performance(results)

    print("Analyzing benchmark categories...")
    category_analysis = analyze_benchmark_categories(processed_results)

    print("Analyzing complexity patterns...")
    complexity_analysis = analyze_complexity_patterns(processed_results)

    print("Analyzing LLM effectiveness...")
    llm_effectiveness = analyze_llm_effectiveness(processed_results)
    
    print("Generating summary report...")
    report = generate_summary_report(performance_metrics, category_analysis, complexity_analysis, llm_effectiveness)
    
    # Save report
    with open("QF_NIA_Analysis_Report.md", "w") as f:
        f.write(report)
    
    print("Analysis complete! Report saved to QF_NIA_Analysis_Report.md")
    
    # Return data for further analysis
    return {
        'performance_metrics': performance_metrics,
        'category_analysis': category_analysis,
        'complexity_analysis': complexity_analysis,
        'llm_effectiveness': llm_effectiveness,
        'processed_results': processed_results
    }

if __name__ == "__main__":
    analysis_results = main()
