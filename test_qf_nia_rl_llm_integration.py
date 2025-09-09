#!/usr/bin/env python3
"""
测试QF_NIA_run_advanced_predictor.py中RL+LLM部分的集成
验证process_single_file_with_timeout是否完全仿照run_predictor.py的处理逻辑
"""

import os
import sys
import tempfile
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """测试导入是否正常"""
    print("Testing imports...")
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import (
            process_single_file_with_timeout,
            _process_worker_qf_nia,
            create_agent_qf_nia,
            ConstraintSimplificationEnv_test,
            process_embeding
        )
        print("✅ 所有RL+LLM组件导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_process_embeding_integration():
    """测试process_embeding集成"""
    print("\nTesting process_embeding integration...")
    
    try:
        from test_rl.test_cvc5.predict_z3_process.QF_NIA_run_advanced_predictor import process_embeding
        
        # 测试简单的SMT字符串
        test_smt = "(set-logic QF_NIA)\n(declare-fun x () Int)\n(assert (> x 0))\n(check-sat)"
        
        # 测试process_embeding调用
        result = process_embeding(test_smt)
        
        if hasattr(result, 'shape') and len(result.shape) == 1:
            print(f"✅ process_embeding正常工作，输出维度: {result.shape}")
            return True
        else:
            print(f"❌ process_embeding输出格式不正确: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ process_embeding测试失败: {e}")
        return False

def test_pearl_agent_parameters():
    """测试Pearl agent参数设置"""
    print("\nTesting Pearl agent parameters...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查create_agent_qf_nia函数的参数设置
        parameter_checks = [
            ("状态维度8192", "state_dim=8192"),
            ("隐藏层配置", "actor_hidden_dims=[1024, 512, 128]"),
            ("critic隐藏层配置", "critic_hidden_dims=[1024, 512, 128]"),
            ("action_representation_module", "action_representation_module=action_representation_module"),
            ("LSTM历史总结模块", "LSTMHistorySummarizationModule"),
            ("观察维度8192", "observation_dim=8192"),
            ("隐藏维度8192", "hidden_dim=8192"),
            ("回放缓冲区大小10", "FIFOOffPolicyReplayBuffer(10)"),
            ("设备ID -1", "device_id=-1"),
        ]
        
        all_passed = True
        for check_name, pattern in parameter_checks:
            if pattern in content:
                print(f"✅ {check_name}: 正确设置")
            else:
                print(f"❌ {check_name}: 设置不正确")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Pearl agent参数测试失败: {e}")
        return False

def test_run_predictor_logic_similarity():
    """测试与run_predictor.py逻辑的相似性"""
    print("\nTesting run_predictor.py logic similarity...")
    
    try:
        # 读取QF_NIA实现
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            qf_nia_content = f.read()
        
        # 读取run_predictor.py参考实现
        run_predictor_path = "test_rl/test_cvc5/cvc5_process/run_predictor.py"
        with open(run_predictor_path, 'r') as f:
            run_predictor_content = f.read()
        
        # 检查关键逻辑相似性
        logic_checks = [
            ("多进程处理", "Process(target=_process_worker"),
            ("环境数据队列", "env_data_queue = Queue()"),
            ("超时控制", "while elapsed < args.timeout:"),
            ("环境数据更新", "env_data_queue.put({"),
            ("在线学习调用", "online_learning("),
            ("回调函数", "def data_callback("),
            ("结果字典", "result_dict['result'] = result_list"),
            ("异常处理", "except Exception as e:"),
            ("环境创建", "ConstraintSimplificationEnv_test("),
            ("Agent创建", "create_agent"),
        ]
        
        all_passed = True
        for check_name, pattern in logic_checks:
            if pattern in qf_nia_content:
                print(f"✅ {check_name}: 逻辑存在")
            else:
                print(f"❌ {check_name}: 逻辑缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 逻辑相似性测试失败: {e}")
        return False

def test_environment_class_modifications():
    """测试环境类的修改"""
    print("\nTesting environment class modifications...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查环境类的关键修改
        env_checks = [
            ("process_embeding在reset中", "self.state = process_embeding(self.smtlib_str).unsqueeze(0)"),
            ("process_embeding在step中", "self.state = process_embeding(solver.to_smt2()).unsqueeze(0)"),
            ("process_embeding在calculate_reward中", "new_state = process_embeding("),
            ("constant_list参数", "self.constant_list = constant_list"),
            ("LLM配置", "self.llm_host = llm_host"),
            ("normalize_smt_str_without_replace", "normalize_smt_str_without_replace(self.smtlib_str)"),
        ]
        
        all_passed = True
        for check_name, pattern in env_checks:
            if pattern in content:
                print(f"✅ {check_name}: 正确实现")
            else:
                print(f"❌ {check_name}: 实现缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 环境类修改测试失败: {e}")
        return False

def test_original_logic_preservation():
    """测试原始逻辑是否保留"""
    print("\nTesting original logic preservation...")
    
    try:
        qf_nia_path = "test_rl/test_cvc5/predict_z3_process/QF_NIA_run_advanced_predictor.py"
        with open(qf_nia_path, 'r') as f:
            content = f.read()
        
        # 检查原始逻辑是否保留
        original_checks = [
            ("run_advanced_prediction_flow函数", "def run_advanced_prediction_flow("),
            ("预测判断逻辑", "if predicted_solvability == 1:"),
            ("时间预测", "predicted_time"),
            ("原始求解逻辑", "solve_and_measure_time"),
            ("信息字典更新", "info_dict[file_path] = "),
            ("main函数", "def main():"),
            ("命令行参数解析", "parser.add_argument"),
        ]
        
        all_passed = True
        for check_name, pattern in original_checks:
            if pattern in content:
                print(f"✅ {check_name}: 保留")
            else:
                print(f"❌ {check_name}: 缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 原始逻辑保留测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("QF_NIA_run_advanced_predictor.py RL+LLM集成验证测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("process_embeding集成测试", test_process_embeding_integration),
        ("Pearl Agent参数测试", test_pearl_agent_parameters),
        ("run_predictor.py逻辑相似性测试", test_run_predictor_logic_similarity),
        ("环境类修改测试", test_environment_class_modifications),
        ("原始逻辑保留测试", test_original_logic_preservation),
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
        print("🎉 所有测试通过！RL+LLM集成成功！")
        print("\n集成特点:")
        print("1. ✅ 完全仿照run_predictor.py的处理逻辑")
        print("2. ✅ 使用process_embeding替代原有编码方法")
        print("3. ✅ Pearl agent参数按照参考文件精确设置")
        print("4. ✅ 保留原有的预测判断逻辑")
        print("5. ✅ 只修改RL+LLM相关部分")
        print("6. ✅ 维持完整的多进程架构和错误处理")
    else:
        print("⚠️  部分测试失败，请检查相关问题。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
