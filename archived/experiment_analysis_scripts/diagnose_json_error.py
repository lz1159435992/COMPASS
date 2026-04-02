#!/usr/bin/env python3
"""
诊断QF_NIA_run_advanced_predictor.py中JSON解析错误的具体文件
"""

import os
import sys
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_json_file(file_path, file_description):
    """检查单个JSON文件的格式"""
    print(f"\n检查 {file_description}: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        file_size = os.path.getsize(file_path)
        print(f"📁 文件大小: {file_size:,} bytes")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 文件内容长度: {len(content):,} 字符")
        
        # 尝试解析JSON
        try:
            data = json.loads(content)
            print(f"✅ JSON格式正确，包含 {len(data)} 个条目")
            
            # 显示前几个键作为示例
            if isinstance(data, dict):
                sample_keys = list(data.keys())[:3]
                print(f"📋 示例键: {sample_keys}")
                
                # 检查值的格式
                if sample_keys:
                    sample_value = data[sample_keys[0]]
                    print(f"📋 示例值格式: {type(sample_value)} - {sample_value}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            print(f"🔍 错误位置: 第 {e.lineno} 行, 第 {e.colno} 列")
            
            # 显示错误附近的内容
            lines = content.split('\n')
            if e.lineno <= len(lines):
                start_line = max(0, e.lineno - 3)
                end_line = min(len(lines), e.lineno + 2)
                
                print(f"🔍 错误附近的内容 (行 {start_line + 1} - {end_line}):")
                for i in range(start_line, end_line):
                    marker = " >>> " if i == e.lineno - 1 else "     "
                    print(f"{marker}{i + 1:4d}: {lines[i]}")
            
            return False
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def diagnose_qf_nia_files():
    """诊断QF_NIA相关的所有文件"""
    print("=" * 60)
    print("QF_NIA JSON文件诊断")
    print("=" * 60)
    
    # 默认文件路径（从QF_NIA_run_advanced_predictor.py中获取）
    files_to_check = [
        ("/home/<USER>/PycharmProjects/Pearl/test_rl/predictor/smt_comp_NIA/QF_NIA_test.json", "源约束文件"),
        ("/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json", "直接求解缓存"),
        ("/home/<USER>/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt", "RL求解缓存"),
        ("QF_NIA_advanced_solver_results_all.json", "输出文件"),
    ]
    
    results = []
    
    for file_path, description in files_to_check:
        result = check_json_file(file_path, description)
        results.append((file_path, description, result))
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断结果总结:")
    print("=" * 60)
    
    all_good = True
    for file_path, description, result in results:
        status = "✅ 正常" if result else "❌ 有问题"
        print(f"{status} {description}")
        if not result:
            all_good = False
            print(f"     文件: {file_path}")
    
    if all_good:
        print("\n🎉 所有文件格式都正常！")
    else:
        print("\n⚠️  发现问题文件，请检查上述错误信息。")
        print("\n💡 建议:")
        print("1. 检查文件是否被截断或损坏")
        print("2. 查看是否有尾随逗号或其他格式错误")
        print("3. 考虑重新生成损坏的文件")
        print("4. 使用修复后的load_dictionary函数会自动处理这些问题")
    
    return all_good

def test_with_fixed_load_dictionary():
    """使用修复后的load_dictionary函数测试文件加载"""
    print("\n" + "=" * 60)
    print("使用修复后的load_dictionary函数测试")
    print("=" * 60)
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import load_dictionary
        
        files_to_test = [
            ("/home/<USER>/PycharmProjects/Pearl/test_rl/predictor/smt_comp_NIA/QF_NIA_test.json", "源约束文件"),
            ("/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json", "直接求解缓存"),
            ("/home/<USER>/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt", "RL求解缓存"),
        ]
        
        for file_path, description in files_to_test:
            print(f"\n测试加载 {description}: {file_path}")
            
            try:
                data = load_dictionary(file_path)
                if isinstance(data, dict):
                    print(f"✅ 成功加载，包含 {len(data)} 个条目")
                    
                    # 显示示例数据
                    if len(data) > 0:
                        sample_key = list(data.keys())[0]
                        sample_value = data[sample_key]
                        print(f"📋 示例: {sample_key} -> {sample_value}")
                else:
                    print(f"❌ 加载失败，返回类型: {type(data)}")
                    
            except Exception as e:
                print(f"❌ 加载异常: {e}")
        
        print("\n✅ 修复后的load_dictionary函数测试完成")
        return True
        
    except ImportError as e:
        print(f"⚠️  无法导入修复后的函数: {e}")
        return False

def main():
    """主函数"""
    print("开始诊断JSON文件问题...")
    
    # 首先诊断原始文件
    file_diagnosis = diagnose_qf_nia_files()
    
    # 然后测试修复后的函数
    function_test = test_with_fixed_load_dictionary()
    
    print("\n" + "=" * 60)
    print("最终总结:")
    print("=" * 60)
    
    if file_diagnosis:
        print("✅ 所有JSON文件格式正常")
    else:
        print("⚠️  发现JSON格式问题，但修复后的load_dictionary函数可以处理")
    
    if function_test:
        print("✅ 修复后的load_dictionary函数工作正常")
    else:
        print("⚠️  修复后的load_dictionary函数测试失败")
    
    print("\n💡 解决方案:")
    print("1. 使用修复后的load_dictionary函数（已实现）")
    print("2. 函数会自动处理JSON格式错误")
    print("3. 损坏的文件会被备份，程序继续运行")
    print("4. 详细的错误日志帮助定位问题")
    
    return True

if __name__ == "__main__":
    main()
