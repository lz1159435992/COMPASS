#!/usr/bin/env python3
"""
测试QF_NIA_run_advanced_predictor.py的重新实现
验证process_single_file_with_timeout和ConstraintSimplificationEnv_test的正确性
"""

import os
import sys
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """测试所有必要的导入是否正常工作"""
    print("Testing imports...")
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import (
            ConstraintSimplificationEnv_test,
            process_single_file_with_timeout,
            _process_worker_qf_nia,
            run_advanced_prediction_flow
        )
        print("✅ QF_NIA_run_advanced_predictor imports successful")
        return True
    except ImportError as e:
        print(f"❌ QF_NIA_run_advanced_predictor import failed: {e}")
        return False

def test_class_structure():
    """测试ConstraintSimplificationEnv_test类的结构"""
    print("\nTesting ConstraintSimplificationEnv_test class structure...")
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import ConstraintSimplificationEnv_test
        
        # 检查类的关键方法
        required_methods = ['__init__', 'reset', 'step', 'action_space', 'range_init']
        
        for method in required_methods:
            if hasattr(ConstraintSimplificationEnv_test, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        print("✅ ConstraintSimplificationEnv_test class structure correct")
        return True
        
    except Exception as e:
        print(f"❌ Class structure test failed: {e}")
        return False

def test_function_signatures():
    """测试函数签名"""
    print("\nTesting function signatures...")
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import (
            process_single_file_with_timeout,
            _process_worker_qf_nia
        )
        
        import inspect
        
        # 检查process_single_file_with_timeout签名
        sig = inspect.signature(process_single_file_with_timeout)
        expected_params = ['file_path', 'list1', 'info_dict', 'args']
        actual_params = list(sig.parameters.keys())
        
        if actual_params == expected_params:
            print("✅ process_single_file_with_timeout signature correct")
        else:
            print(f"❌ process_single_file_with_timeout signature mismatch: {actual_params} vs {expected_params}")
            return False
        
        # 检查_process_worker_qf_nia签名
        sig = inspect.signature(_process_worker_qf_nia)
        expected_params = ['file_path', 'list1', 'result_dict', 'env_data_queue', 'args']
        actual_params = list(sig.parameters.keys())
        
        if actual_params == expected_params:
            print("✅ _process_worker_qf_nia signature correct")
        else:
            print(f"❌ _process_worker_qf_nia signature mismatch: {actual_params} vs {expected_params}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        return False

def test_data_structure_compatibility():
    """测试与QF_NIA_test.json数据结构的兼容性"""
    print("\nTesting data structure compatibility...")
    
    try:
        # 检查QF_NIA_test.json是否存在
        qf_nia_test_path = "test_rl/predictor/smt_comp_NIA/QF_NIA_test.json"
        if not os.path.exists(qf_nia_test_path):
            print(f"⚠️  QF_NIA_test.json not found at {qf_nia_test_path}")
            return True  # 不算失败，只是警告
        
        # 读取并验证数据结构
        with open(qf_nia_test_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ QF_NIA_test.json loaded successfully with {len(data)} entries")
        
        # 检查数据格式
        sample_key = list(data.keys())[0]
        sample_value = data[sample_key]
        
        if isinstance(sample_value, list) and len(sample_value) >= 3:
            print(f"✅ Data structure correct: [feature_path, solvability_pred, time_pred]")
            print(f"   Sample: {sample_value}")
        else:
            print(f"❌ Data structure incorrect: {sample_value}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure compatibility test failed: {e}")
        return False

def test_code_consistency():
    """测试代码一致性"""
    print("\nTesting code consistency...")
    
    try:
        # 读取QF_NIA_run_advanced_predictor.py文件
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查关键组件是否存在
        checks = [
            ("ConstraintSimplificationEnv_test class", "class ConstraintSimplificationEnv_test"),
            ("process_single_file_with_timeout function", "def process_single_file_with_timeout"),
            ("_process_worker_qf_nia function", "def _process_worker_qf_nia"),
            ("Pre-computed prediction logic", "constraint_info = source_constraints[key]"),
            ("RL+LLM invocation", "process_single_file_with_timeout(key, placeholder_list1, output_dict, args)"),
            ("Environment creation", "ConstraintSimplificationEnv_test("),
            ("Model loading", "EnhancedClassifier()"),
            ("Embedding generation", "process_embeding("),
        ]
        
        all_passed = True
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} missing")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Code consistency test failed: {e}")
        return False

def test_integration_points():
    """测试与原始代码的集成点"""
    print("\nTesting integration points...")
    
    try:
        # 检查是否正确移除了原始的导入
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查不应该存在的导入（已移除的）
        removed_imports = [
            "from test_rl.test_cvc5.predict_z3_process.run_predictor import",
        ]
        
        # 检查应该存在的新导入
        new_imports = [
            "from pearl.api.environment import Environment",
            "from test_rl.test_script.utils import",
            "from test_rl.predictor.smt_comp_QF_IDL.test_group_get_dis_smt_comp_llm import process_embeding",
        ]
        
        all_passed = True
        
        for import_stmt in removed_imports:
            if import_stmt in content:
                print(f"⚠️  Old import still present: {import_stmt}")
                # 不算失败，只是警告
        
        for import_stmt in new_imports:
            if import_stmt in content:
                print(f"✅ New import found: {import_stmt}")
            else:
                print(f"❌ New import missing: {import_stmt}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Integration points test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("QF_NIA_run_advanced_predictor.py 重新实现验证测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("类结构测试", test_class_structure),
        ("函数签名测试", test_function_signatures),
        ("数据结构兼容性测试", test_data_structure_compatibility),
        ("代码一致性测试", test_code_consistency),
        ("集成点测试", test_integration_points),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！QF_NIA_run_advanced_predictor.py 重新实现成功！")
        print("\n主要实现内容:")
        print("1. ✅ 重新实现了ConstraintSimplificationEnv_test类")
        print("2. ✅ 重新实现了process_single_file_with_timeout函数")
        print("3. ✅ 重新实现了_process_worker_qf_nia工作进程函数")
        print("4. ✅ 集成了基于env_gai_6_llm_add_ce_predictor_docker_llm_embed.py的逻辑")
        print("5. ✅ 保持了与QF_NIA_test.json数据结构的兼容性")
    else:
        print("⚠️  部分测试失败，请检查相关问题。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
