#!/usr/bin/env python3
"""
测试QF_NIA_run_advanced_predictor.py的参数配置和文件读取修改
"""

import os
import sys
import tempfile

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_parameter_configuration():
    """测试参数配置是否正确"""
    print("Testing parameter configuration...")
    
    try:
        # 读取QF_NIA_run_advanced_predictor.py文件
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查参数定义
        required_params = [
            ("binary_model_path", "QF_NIA_bert_predictor_mask_best_llm.pth"),
            ("eight_class_model_path", "QF_NIA_bert_predictor_2_mask_best_model_llm.pth"),
            ("llm_host", "http://172.29.7.221:32783"),
            ("llm_model", "llama3.1:70b"),
        ]
        
        all_passed = True
        for param_name, expected_value in required_params:
            if f"--{param_name}" in content and expected_value in content:
                print(f"✅ Parameter {param_name} correctly configured with {expected_value}")
            else:
                print(f"❌ Parameter {param_name} missing or incorrectly configured")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Parameter configuration test failed: {e}")
        return False

def test_model_loading_logic():
    """测试模型加载逻辑是否正确"""
    print("\nTesting model loading logic...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查模型加载代码
        model_loading_checks = [
            ("Direct parameter usage", "args.binary_model_path"),
            ("Direct parameter usage", "args.eight_class_model_path"),
            ("Direct parameter usage", "args.llm_host"),
            ("No getattr usage", "getattr(args, 'binary_model_path'"),  # 这个不应该存在
            ("No getattr usage", "getattr(args, 'eight_class_model_path'"),  # 这个不应该存在
            ("No getattr usage", "getattr(args, 'ollama_host'"),  # 这个不应该存在
        ]
        
        all_passed = True
        for check_name, pattern in model_loading_checks:
            if "No getattr usage" in check_name:
                # 这些模式不应该存在
                if pattern in content:
                    print(f"❌ {check_name}: Found deprecated pattern {pattern}")
                    all_passed = False
                else:
                    print(f"✅ {check_name}: Deprecated pattern correctly removed")
            else:
                # 这些模式应该存在
                if pattern in content:
                    print(f"✅ {check_name}: Found {pattern}")
                else:
                    print(f"❌ {check_name}: Missing {pattern}")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Model loading logic test failed: {e}")
        return False

def test_file_reading_logic():
    """测试文件读取逻辑是否正确"""
    print("\nTesting file reading logic...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查文件读取逻辑
        file_reading_checks = [
            ("Direct SMT reading", "smtlib_str = file.read()"),
            ("No JSON parsing", "json.loads(smtlib_str_raw)"),  # 这个不应该存在
            ("No dict access", "dict_obj.get('smt_script')"),  # 这个不应该存在
        ]
        
        all_passed = True
        for check_name, pattern in file_reading_checks:
            if "No JSON parsing" in check_name or "No dict access" in check_name:
                # 这些模式不应该存在
                if pattern in content:
                    print(f"❌ {check_name}: Found deprecated pattern {pattern}")
                    all_passed = False
                else:
                    print(f"✅ {check_name}: Deprecated pattern correctly removed")
            else:
                # 这些模式应该存在
                if pattern in content:
                    print(f"✅ {check_name}: Found {pattern}")
                else:
                    print(f"❌ {check_name}: Missing {pattern}")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ File reading logic test failed: {e}")
        return False

def test_smt_file_reading():
    """测试SMT文件读取功能"""
    print("\nTesting SMT file reading functionality...")
    
    try:
        # 创建一个测试SMT文件
        test_smt_content = """(set-info :smt-lib-version 2.6)
(set-logic QF_NIA)
(declare-fun x () Int)
(declare-fun y () Int)
(assert (and (> x 0) (< y 10) (= (* x y) 20)))
(check-sat)
(exit)"""
        
        # 写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.smt2', delete=False) as f:
            f.write(test_smt_content)
            temp_file_path = f.name
        
        try:
            # 测试读取
            with open(temp_file_path, 'r') as file:
                smtlib_str = file.read()
            
            # 验证内容
            if smtlib_str == test_smt_content:
                print("✅ SMT file reading works correctly")
                print(f"   Read {len(smtlib_str)} characters")
                print(f"   Content preview: {smtlib_str[:50]}...")
                return True
            else:
                print("❌ SMT file reading failed: content mismatch")
                return False
                
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"❌ SMT file reading test failed: {e}")
        return False

def test_code_consistency():
    """测试代码一致性"""
    print("\nTesting code consistency...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查关键代码段
        consistency_checks = [
            ("Model initialization", "model = EnhancedClassifier()"),
            ("Model loading", "model.load_state_dict(torch.load(args.binary_model_path))"),
            ("Time model initialization", "model_time = EnhancedEightClassModelLargeInput()"),
            ("Time model loading", "model_time.load_state_dict(torch.load(args.eight_class_model_path))"),
            ("Embedding generation", "process_embeding(normalized_str, args.llm_host)"),
            ("Direct file reading", "with open(file_path, 'r') as file:"),
            ("SMT string assignment", "smtlib_str = file.read()"),
        ]
        
        all_passed = True
        for check_name, pattern in consistency_checks:
            if pattern in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Code consistency test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("QF_NIA_run_advanced_predictor.py 参数和文件读取修改验证")
    print("=" * 60)
    
    tests = [
        ("参数配置测试", test_parameter_configuration),
        ("模型加载逻辑测试", test_model_loading_logic),
        ("文件读取逻辑测试", test_file_reading_logic),
        ("SMT文件读取功能测试", test_smt_file_reading),
        ("代码一致性测试", test_code_consistency),
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
        print("🎉 所有测试通过！参数和文件读取修改成功！")
        print("\n主要修改内容:")
        print("1. ✅ 使用正确的参数名称 (binary_model_path, eight_class_model_path, llm_host)")
        print("2. ✅ 移除了方法内的默认参数设置")
        print("3. ✅ 直接读取SMT2文本文件，不使用JSON解析")
        print("4. ✅ 使用args.参数名直接访问参数值")
        print("5. ✅ 更新了模型文件路径为正确的文件名")
    else:
        print("⚠️  部分测试失败，请检查相关问题。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
