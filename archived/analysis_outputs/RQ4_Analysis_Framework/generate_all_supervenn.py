#!/usr/bin/env python3
"""
批量生成所有求解器的SuperVenn图
"""

import json
import os
import subprocess
import sys

def load_config(config_file: str):
    """加载配置文件"""
    with open(config_file, 'r') as f:
        return json.load(f)

def generate_supervenn_for_solver(solver_id: str, solver_config: dict, output_dir: str):
    """为单个求解器生成SuperVenn图"""
    
    print(f"\n🔍 Generating SuperVenn for {solver_config['name']}...")
    
    # 检查数据文件是否存在
    data_file = solver_config['data_file']
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return False
    
    # 构建命令
    cmd = [
        'python', 'RQ4_Analysis_Framework/unified_supervenn_generator.py',
        '--solver', solver_id,
        '--data-file', data_file,
        '--output-dir', output_dir,
        '--solver-name', solver_config['name']
    ]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {solver_config['name']} SuperVenn generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating {solver_config['name']} SuperVenn:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False

def create_summary_report(config: dict, output_dir: str):
    """创建总结报告"""
    
    report_lines = [
        "# RQ4 SuperVenn Analysis Summary Report",
        "",
        "## Generated SuperVenn Diagrams",
        ""
    ]
    
    for solver_id, solver_config in config['solvers'].items():
        solver_name = solver_config['name']
        figure_file = f"supervenn-{solver_name.lower()}-comparison.pdf"
        latex_file = f"{solver_name.lower()}_supervenn_latex.txt"
        
        report_lines.extend([
            f"### {solver_name}",
            f"- **Description**: {solver_config['description']}",
            f"- **Data File**: `{solver_config['data_file']}`",
            f"- **SuperVenn Figure**: `{figure_file}`",
            f"- **LaTeX Code**: `{latex_file}`",
            ""
        ])
    
    report_lines.extend([
        "## Usage in Paper",
        "",
        "1. Copy the generated PDF files to your paper's figures directory",
        "2. Use the LaTeX code from the corresponding `.txt` files",
        "3. Update figure references in your RQ4 section",
        "",
        "## File Structure",
        "```",
        f"{output_dir}/",
        "├── supervenn-z3-comparison.pdf",
        "├── supervenn-cvc5-comparison.pdf", 
        "├── supervenn-bvparti-comparison.pdf",
        "├── z3_supervenn_latex.txt",
        "├── cvc5_supervenn_latex.txt",
        "└── bvparti_supervenn_latex.txt",
        "```"
    ])
    
    # 保存报告
    report_file = os.path.join(output_dir, "RQ4_SuperVenn_Summary.md")
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📋 Summary report saved to: {report_file}")

def main():
    """主函数"""
    
    print("🚀 RQ4 SuperVenn Analysis Framework")
    print("=" * 50)
    
    # 加载配置
    config_file = "RQ4_Analysis_Framework/solver_config.json"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    config = load_config(config_file)
    output_dir = config['output_settings']['figure_dir']
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # 生成所有SuperVenn图
    success_count = 0
    total_count = len(config['solvers'])
    
    for solver_id, solver_config in config['solvers'].items():
        if generate_supervenn_for_solver(solver_id, solver_config, output_dir):
            success_count += 1
    
    # 创建总结报告
    create_summary_report(config, output_dir)
    
    # 打印最终结果
    print("\n" + "=" * 50)
    print("🎉 RQ4 SuperVenn Generation Complete!")
    print(f"✅ Successfully generated: {success_count}/{total_count} SuperVenn diagrams")
    
    if success_count == total_count:
        print("\n🎯 All SuperVenn diagrams generated successfully!")
        print("📝 Ready for integration into paper RQ4 section")
    else:
        print(f"\n⚠️  {total_count - success_count} diagrams failed to generate")
        print("🔍 Check the error messages above for details")

if __name__ == "__main__":
    main()
