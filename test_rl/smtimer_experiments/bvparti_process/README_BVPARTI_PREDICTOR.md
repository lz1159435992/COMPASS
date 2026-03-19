# BVParti预测器使用说明

## 概述

`run_bvparti_predictor.py` 是基于STP-Parti-Bitwuzla求解器的强化学习预测器，仿照 `cvc5_process/run_predictor.py` 的架构实现，但使用BVParti作为底层求解器。

## 主要特性

### 1. 多求解器支持
- **BVParti**: 默认求解器，使用STP-Parti-Bitwuzla组合
- **Z3**: 传统Z3求解器
- **CVC5**: CVC5求解器

### 2. JSON格式兼容性
- 自动识别并处理两种JSON格式：
  - 简单格式（cvc5格式）：`{"path": ["status", time, limit, {}]}`
  - 复杂格式（bvparti格式）：包含metadata和results的嵌套结构
- 自动转换timeout状态为unknown
- 错误处理和状态映射

### 3. 强化学习环境
- 基于Pearl框架的RL环境
- 支持约束简化和变量赋值
- LLM辅助的智能求解策略
- 多进程处理和超时控制

## 安装要求

### 必需依赖
```bash
pip install torch numpy loguru
pip install transformers  # 用于BERT嵌入
pip install ollama  # 用于LLM调用
```

### Pearl框架
```bash
# 安装Pearl强化学习框架
pip install pearl-agent
```

### BVParti求解器
确保以下路径存在并可执行：
- `/home/lz/PycharmProjects/Pearl/test_rl/AriParti_sync/STP-Parti-Bitwuzla-at-SMT-COMP-2025-build/solver/BVPartition-bin`
- `/home/lz/PycharmProjects/Pearl/test_rl/AriParti_sync/STP-Parti-Bitwuzla-at-SMT-COMP-2025-build/solver/partitioner-bin`
- `/home/lz/PycharmProjects/Pearl/test_rl/AriParti_sync/STP-Parti-Bitwuzla-at-SMT-COMP-2025-build/solver/bitwuzla-0.8.0-bin`

## 使用方法

### 基本用法
```bash
cd /home/lz/PycharmProjects/Pearl
python test_rl/test_cvc5/bvparti_process/run_bvparti_predictor.py \
    --solver bvparti \
    --result_dict_path /path/to/SMTimer_z3_result_predictor.json \
    --info_dict_path /path/to/output_info_dict.txt \
    --llm_model llama3.1:70b \
    --timeout 1200
```

### 主要参数

#### 文件路径参数
- `--rl_dict_path`: RL字典文件路径（默认：`/home/lz/sibyl_3/src/networks/info_dict_rl.txt`）
- `--info_dict_path`: 输出信息字典文件路径
- `--result_dict_path`: 输入结果字典文件路径
- `--binary_model_path`: 二分类模型路径（默认：`models/binary_classifier.pth`）
- `--eight_class_model_path`: 八分类模型路径（默认：`models/eight_class_model.pth`）

#### 求解器参数
- `--solver`: 选择求解器 (`z3`/`cvc5`/`bvparti`，默认：`bvparti`)
- `--time_threshold`: 时间阈值（默认：300秒）
- `--timeout`: 执行超时时间（默认：1200秒）

#### LLM参数
- `--llm_host`: LLM服务器地址（默认：`http://172.29.7.221:32943`）
- `--llm_model`: LLM模型名称（默认：`llama3.1:70b`）

#### 训练参数
- `--num_episodes`: 训练轮数（默认：1）
- `--record_period`: 记录周期（默认：1）

### 示例命令

#### 使用BVParti求解器
```bash
python test_rl/test_cvc5/bvparti_process/run_bvparti_predictor.py \
    --solver bvparti \
    --result_dict_path /home/lz/PycharmProjects/Pearl/test_rl/AriParti_sync/scripts/batch_output/bv_default/SMTimer_z3_result_rl.json \
    --info_dict_path info_dict_bvparti_results.txt \
    --timeout 1200 \
    --llm_model llama3.1:70b
```

#### 使用Z3求解器进行对比
```bash
python test_rl/test_cvc5/bvparti_process/run_bvparti_predictor.py \
    --solver z3 \
    --result_dict_path /home/lz/PycharmProjects/Pearl/test_rl/test_cvc5/cvc5_smtimer_results_predictor.json \
    --info_dict_path info_dict_z3_results.txt \
    --timeout 600
```

## 输出格式

处理完成后，信息字典文件包含以下格式的数据：
```json
{
  "file_path": [
    "original_result",      // 原始求解结果
    original_time,          // 原始求解时间
    original_memory,        // 原始内存使用
    total_execution_time,   // 总执行时间
    total_solve_time,       // 累计求解时间
    final_solve_time,       // 最终成功求解时间
    llm_time,              // LLM累计时间
    "succeed/failed",       // 最终状态
    [final_assignments],    // 最终变量赋值
    [counterexamples_list]  // 所有反例列表
  ]
}
```

## 测试

运行测试脚本验证安装：
```bash
python test_rl/test_cvc5/bvparti_process/test_bvparti_predictor.py
```

测试包括：
- BVParti求解器功能测试
- JSON格式兼容性测试
- 环境创建测试
- 命令行参数解析测试

## 与cvc5_process的差异

### 主要改进
1. **求解器支持**: 默认使用BVParti，支持多种求解器
2. **JSON兼容性**: 自动处理新旧两种JSON格式
3. **错误处理**: 更好的异常处理和状态映射
4. **日志记录**: 详细的求解过程日志

### 兼容性
- 保持与原始cvc5_process相同的API接口
- 支持相同的命令行参数（除了默认求解器）
- 输出格式完全兼容

## 故障排除

### 常见问题

1. **BVParti路径不存在**
   - 检查AriParti_sync目录是否正确
   - 确保所有二进制文件已编译并可执行

2. **模型文件缺失**
   - 确保binary_classifier.pth和eight_class_model.pth存在
   - 运行训练脚本生成模型文件

3. **LLM连接失败**
   - 检查LLM服务器地址和端口
   - 确保ollama服务正在运行

4. **内存不足**
   - 减少num_episodes参数
   - 使用较小的模型
   - 增加系统内存

### 日志文件
程序运行时会生成详细的日志文件，包含：
- 求解过程详情
- LLM调用记录
- 错误和异常信息
- 性能统计数据

## 性能优化

### 建议配置
- **GPU**: 推荐使用CUDA加速
- **内存**: 至少16GB RAM
- **存储**: SSD存储以提高I/O性能

### 参数调优
- 根据硬件配置调整timeout参数
- 根据问题复杂度调整num_episodes
- 根据网络状况调整LLM超时设置

## 贡献

如需改进或报告问题，请：
1. 运行测试脚本确认问题
2. 检查日志文件获取详细信息
3. 提供复现步骤和环境信息
