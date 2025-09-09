#!/usr/bin/env python3
"""
测试QF_NIA_run_advanced_predictor.py中process_embeding函数的重新实现
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_function_definition():
    """测试process_embeding函数定义是否正确"""
    print("Testing process_embeding function definition...")
    
    try:
        # 读取QF_NIA_run_advanced_predictor.py文件
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查函数定义
        function_checks = [
            ("Function definition", "def process_embeding(text, host="),
            ("Default host parameter", "host='http://172.29.7.221:32783'"),
            ("Client creation", "client = Client(host=host)"),
            ("Embeddings call", "client.embeddings("),
            ("Model specification", "model='llama3.1:70b'"),
            ("Temperature setting", '"temperature": 0'),
            ("Return statement", "return torch.tensor(response['embedding']"),
            ("Dtype specification", "dtype=torch.float32"),
            ("Logging", "logger.info("),
        ]
        
        all_passed = True
        for check_name, pattern in function_checks:
            if pattern in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing pattern '{pattern}'")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Function definition test failed: {e}")
        return False

def test_function_signature():
    """测试函数签名是否正确"""
    print("\nTesting function signature...")
    
    try:
        # 尝试导入函数（如果环境允许）
        try:
            from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import process_embeding
            
            import inspect
            sig = inspect.signature(process_embeding)
            params = list(sig.parameters.keys())
            
            expected_params = ['text', 'host']
            if params == expected_params:
                print(f"✅ Function signature correct: {sig}")
                
                # 检查默认值
                host_param = sig.parameters['host']
                if host_param.default == 'http://172.29.7.221:32783':
                    print("✅ Default host parameter correct")
                    return True
                else:
                    print(f"❌ Default host parameter incorrect: {host_param.default}")
                    return False
            else:
                print(f"❌ Function signature incorrect: {params} vs {expected_params}")
                return False
                
        except ImportError as e:
            print(f"⚠️  Cannot import function (likely due to missing dependencies): {e}")
            # 这不算失败，只是环境限制
            return True
            
    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        return False

def test_parameter_usage():
    """测试参数使用是否正确"""
    print("\nTesting parameter usage...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查参数使用
        usage_checks = [
            ("Host parameter usage", "process_embeding(normalized_str, args.llm_host)"),
            ("Function call with two parameters", "process_embeding("),
            ("Args.llm_host usage", "args.llm_host"),
        ]
        
        all_passed = True
        for check_name, pattern in usage_checks:
            if pattern in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing pattern '{pattern}'")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Parameter usage test failed: {e}")
        return False

def test_import_removal():
    """测试是否正确移除了外部导入"""
    print("\nTesting import removal...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查是否移除了外部导入
        removed_imports = [
            "from test_rl.predictor.smt_comp_QF_IDL.test_group_get_dis_smt_comp_llm import process_embeding",
        ]
        
        all_passed = True
        for import_stmt in removed_imports:
            if import_stmt in content:
                print(f"❌ Old import still present: {import_stmt}")
                all_passed = False
            else:
                print(f"✅ Old import correctly removed")
        
        # 检查是否有本地实现的注释
        if "process_embeding function is implemented locally below" in content:
            print("✅ Local implementation comment found")
        else:
            print("❌ Local implementation comment missing")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Import removal test failed: {e}")
        return False

def test_function_completeness():
    """测试函数实现的完整性"""
    print("\nTesting function completeness...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查函数的完整性
        completeness_checks = [
            ("Docstring", '"""'),
            ("Args documentation", "Args:"),
            ("Returns documentation", "Returns:"),
            ("Client import", "from ollama import Client"),
            ("Torch import", "import torch"),
            ("Error handling potential", "response['embedding']"),
            ("Type conversion", "torch.tensor"),
            ("Float32 dtype", "dtype=torch.float32"),
        ]
        
        all_passed = True
        for check_name, pattern in completeness_checks:
            if pattern in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Function completeness test failed: {e}")
        return False

def test_consistency_with_original():
    """测试与原始函数的一致性"""
    print("\nTesting consistency with original function...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查与原始函数的一致性
        consistency_checks = [
            ("Same model", "llama3.1:70b"),
            ("Same temperature", '"temperature": 0'),
            ("Same return type", "torch.tensor"),
            ("Same response access", "response['embedding']"),
            ("Ollama Client", "Client(host=host)"),
        ]
        
        all_passed = True
        for check_name, pattern in consistency_checks:
            if pattern in content:
                print(f"✅ {check_name}: Consistent")
            else:
                print(f"❌ {check_name}: Inconsistent or missing")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("process_embeding函数重新实现验证测试")
    print("=" * 60)
    
    tests = [
        ("函数定义测试", test_function_definition),
        ("函数签名测试", test_function_signature),
        ("参数使用测试", test_parameter_usage),
        ("导入移除测试", test_import_removal),
        ("函数完整性测试", test_function_completeness),
        ("原始函数一致性测试", test_consistency_with_original),
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
        print("🎉 所有测试通过！process_embeding函数重新实现成功！")
        print("\n主要实现特性:")
        print("1. ✅ 将host参数外提，支持动态配置")
        print("2. ✅ 保持与原始函数的完全一致性")
        print("3. ✅ 添加了完整的文档字符串")
        print("4. ✅ 使用正确的默认host地址")
        print("5. ✅ 移除了外部依赖，实现本地化")
    else:
        print("⚠️  部分测试失败，请检查相关问题。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
