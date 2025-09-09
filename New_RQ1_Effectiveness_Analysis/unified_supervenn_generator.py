#!/usr/bin/env python3
"""
统一的SuperVenn图生成器
支持Z3、CVC5、BVParti等多种求解器的SuperVenn分析
基于AriParti_sync/scripts/compare_results.py的专业SuperVenn风格
"""

import json
import ast
import os
import matplotlib.pyplot as plt
from supervenn import supervenn
import argparse
from typing import Dict, Set, Any, Tuple

# 配置常量
TIMEOUT_VALUE = 1200.0

class SuperVennGenerator:
    """统一的SuperVenn图生成器类"""
    
    def __init__(self, solver_name: str = "Solver"):
        self.solver_name = solver_name
        self.color_palette = ['#0072B2', '#D55E00']  # 专业配色方案
        
    def load_z3_data(self, baseline_file: str, rl_llm_file: str = None) -> Tuple[Set[str], Set[str]]:
        """加载Z3实验数据"""
        # 如果没有提供RL+LLM文件，尝试自动查找
        if rl_llm_file is None:
            rl_llm_file = baseline_file.replace('result_dict_z3solver_300s.txt', 'result_dict_RL+LLM_108.txt')

        # 加载基线数据
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)

        # 加载RL+LLM数据
        try:
            with open(rl_llm_file, 'r') as f:
                rl_llm_data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: RL+LLM file not found: {rl_llm_file}")
            rl_llm_data = baseline_data  # 使用基线数据作为备用

        baseline_solved = set()
        rl_llm_solved = set()

        # 处理基线数据
        for package, solvers in baseline_data.items():
            for solver_name, solver_data in solvers.items():
                if 'sat_list' in solver_data:
                    for i, time_val in enumerate(solver_data['sat_list']):
                        baseline_solved.add(f"{package}/{solver_name}/constraint_{i}")

        # 处理RL+LLM数据
        for package, solvers in rl_llm_data.items():
            for solver_name, solver_data in solvers.items():
                if 'sat_list' in solver_data:
                    for i, time_val in enumerate(solver_data['sat_list']):
                        rl_llm_solved.add(f"{package}/{solver_name}/constraint_{i}")

        return baseline_solved, rl_llm_solved
    
    def load_cvc5_data(self, file_path: str) -> Tuple[Set[str], Set[str]]:
        """加载CVC5实验数据"""
        with open(file_path, 'r') as f:
            content = f.read()
            data = ast.literal_eval(content)
        
        baseline_solved = set()
        rl_llm_solved = set()
        
        for path, result_data in data.items():
            # CVC5数据格式: [status, baseline_time, baseline_solved, timeout, rl_time, rl_solved, total_time, rl_status, ...]
            baseline_status = result_data[0]
            rl_status = result_data[7]
            
            # 基线求解器解决的约束
            if baseline_status in ['sat', 'unsat']:
                baseline_solved.add(path)
            
            # RL+LLM解决的约束
            if rl_status == 'succeed':
                rl_llm_solved.add(path)
        
        return baseline_solved, rl_llm_solved
    
    def load_bvparti_data(self, file_path: str) -> Tuple[Set[str], Set[str]]:
        """加载BVParti实验数据"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        baseline_solved = set()
        rl_llm_solved = set()

        for path, result_data in data.items():
            # BVParti数据格式: [status, baseline_time, baseline_solved, timeout, rl_time, rl_solved, total_time, rl_status, baseline_solutions, rl_solutions]
            baseline_status = result_data[0]
            baseline_solved_flag = result_data[2]
            rl_solved_flag = result_data[5]
            rl_status = result_data[7]
            rl_solutions = result_data[9]

            # 判断基线求解成功
            baseline_success = (baseline_solved_flag == 1) or (baseline_status not in ["unknown", "failed"])
            if baseline_success:
                baseline_solved.add(path)

            # 判断RL+LLM求解成功
            rl_llm_success = (rl_solved_flag == 1) or (rl_status not in ["unknown", "failed"]) or (len(rl_solutions) > 0 and len(rl_solutions[0]) > 0)
            if rl_llm_success:
                rl_llm_solved.add(path)

        return baseline_solved, rl_llm_solved

    def load_mathsat_data(self, file_path: str) -> Tuple[Set[str], Set[str]]:
        """加载MathSAT实验数据"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: MathSAT data file not found: {file_path}")
            print("Returning empty sets for demonstration purposes")
            return set(), set()

        baseline_solved = set()
        rl_llm_solved = set()

        for path, result_data in data.items():
            # MathSAT数据格式: 假设与CVC5类似的格式
            # [status, baseline_time, baseline_solved, timeout, rl_time, rl_solved, total_time, rl_status, ...]
            baseline_status = result_data[0]
            rl_status = result_data[7]

            # 基线求解器解决的约束
            if baseline_status in ['sat', 'unsat']:
                baseline_solved.add(path)

            # RL+LLM解决的约束
            if rl_status == 'succeed':
                rl_llm_solved.add(path)

        return baseline_solved, rl_llm_solved
    
    def generate_supervenn_plot(self, baseline_solved: Set[str], rl_llm_solved: Set[str], 
                               title: str, output_path: str) -> Dict[str, Any]:
        """生成SuperVenn图"""
        
        # 计算集合统计
        baseline_only = baseline_solved - rl_llm_solved
        rl_llm_only = rl_llm_solved - baseline_solved
        both_solved = baseline_solved & rl_llm_solved
        
        # 设置专业样式
        with plt.style.context('seaborn-v0_8-paper'):
            plt.rcParams.update({
                'font.family': 'serif',
                'font.serif': ['Times New Roman', 'DejaVu Serif'],
                'font.size': 10
            })
            
            plt.figure(figsize=(10, 3))
            
            # 创建SuperVenn图
            sets_data = [baseline_solved, rl_llm_solved]
            # 统一集合标签为“求解器”和“求解器+COMPASS”
            set_labels = [f'{self.solver_name}', f'{self.solver_name} + COMPASS']
            
            plot = supervenn(sets_data,
                           set_annotations=set_labels,
                           side_plots=True,
                           sets_ordering='minimize gaps',
                           bar_height=1.0,
                           side_plot_width=0.4,
                           color_cycle=self.color_palette,
                           rotate_col_annotations=False,
                           widths_minmax_ratio=0.02)
            
            if 'main' in plot.axes:
                plot.axes['main'].set_title(title, fontsize=14, fontweight='bold')
            
            plt.savefig(output_path, bbox_inches='tight', format='pdf', dpi=300)
            plt.close()
        
        # 返回统计信息
        stats = {
            'baseline_total': len(baseline_solved),
            'rl_llm_total': len(rl_llm_solved),
            'baseline_only': len(baseline_only),
            'rl_llm_only': len(rl_llm_only),
            'both_solved': len(both_solved),
            'total_unique': len(baseline_solved | rl_llm_solved),
            'improvement': len(rl_llm_solved) - len(baseline_solved),
            'relative_improvement': ((len(rl_llm_solved) - len(baseline_solved)) / max(len(baseline_solved), 1)) * 100
        }
        
        return stats
    
    def generate_latex_code(self, stats: Dict[str, Any], figure_label: str) -> str:
        """生成LaTeX图片代码"""
        
        latex_code = f"""
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.8\\textwidth]{{pics/supervenn-{self.solver_name.lower()}-comparison.pdf}}
\\caption{{SuperVenn analysis of {self.solver_name} vs {self.solver_name}+COMPASS. The diagram shows {stats['baseline_only']} constraints solved exclusively by {self.solver_name}, {stats['rl_llm_only']} constraints solved exclusively by {self.solver_name}+COMPASS, and {stats['both_solved']} constraints solved by both. Total improvement: {stats['baseline_total']} → {stats['rl_llm_total']} (+{stats['improvement']} constraints, {stats['relative_improvement']:.1f}\\% relative).}}
\\label{{{figure_label}}}
\\end{{figure}}
"""
        return latex_code
    
    def print_analysis_summary(self, stats: Dict[str, Any]):
        """打印分析总结"""
        print(f"\n{self.solver_name} SuperVenn Analysis Summary:")
        print("=" * 50)
        print(f"Baseline solved: {stats['baseline_total']} constraints")
        print(f"RL+LLM solved: {stats['rl_llm_total']} constraints")
        print(f"Baseline only: {stats['baseline_only']} constraints")
        print(f"RL+LLM only: {stats['rl_llm_only']} constraints")
        print(f"Both solved: {stats['both_solved']} constraints")
        print(f"Total unique solved: {stats['total_unique']} constraints")
        print(f"Improvement: +{stats['improvement']} constraints ({stats['relative_improvement']:.1f}% relative)")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Generate SuperVenn diagrams for solver comparison')
    parser.add_argument('--solver', choices=['z3', 'cvc5', 'bvparti', 'mathsat'], required=True,
                       help='Solver type')
    parser.add_argument('--data-file', required=True,
                       help='Path to the data file')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for generated files')
    parser.add_argument('--solver-name',
                       help='Custom solver name for labels (default: auto-detect from solver type)')

    args = parser.parse_args()

    # 设置求解器名称
    solver_names = {'z3': 'Z3', 'cvc5': 'CVC5', 'bvparti': 'BVParti', 'mathsat': 'MathSAT'}
    solver_name = args.solver_name or solver_names[args.solver]
    
    # 创建输出目录
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Created directory: {args.output_dir}")
    
    # 创建生成器
    generator = SuperVennGenerator(solver_name)
    
    # 加载数据
    print(f"Loading {solver_name} data from {args.data_file}...")
    
    if args.solver == 'z3':
        baseline_solved, rl_llm_solved = generator.load_z3_data(args.data_file)
    elif args.solver == 'cvc5':
        baseline_solved, rl_llm_solved = generator.load_cvc5_data(args.data_file)
    elif args.solver == 'bvparti':
        baseline_solved, rl_llm_solved = generator.load_bvparti_data(args.data_file)
    elif args.solver == 'mathsat':
        baseline_solved, rl_llm_solved = generator.load_mathsat_data(args.data_file)
    
    # 生成SuperVenn图
    output_path = os.path.join(args.output_dir, f"supervenn-{solver_name.lower()}-comparison.pdf")
    title = f"{solver_name} Solving Capability Comparison"
    
    print(f"Generating SuperVenn diagram...")
    stats = generator.generate_supervenn_plot(baseline_solved, rl_llm_solved, title, output_path)
    
    # 生成LaTeX代码
    figure_label = f"fig:supervenn-{solver_name.lower()}"
    latex_code = generator.generate_latex_code(stats, figure_label)
    
    # 保存LaTeX代码
    latex_file = os.path.join(args.output_dir, f"{solver_name.lower()}_supervenn_latex.txt")
    with open(latex_file, 'w') as f:
        f.write(latex_code)
    
    # 打印分析结果
    generator.print_analysis_summary(stats)
    
    print(f"\n✅ SuperVenn diagram saved to: {output_path}")
    print(f"✅ LaTeX code saved to: {latex_file}")
    print(f"🎉 {solver_name} SuperVenn analysis completed!")

if __name__ == "__main__":
    main()
