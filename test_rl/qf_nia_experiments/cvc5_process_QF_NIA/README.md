# QF_NIA CVC5求解实验框架

本目录包含使用CVC5求解器和强化学习方法求解QF_NIA（非线性整数算术）问题的完整实验框架。

## 目录结构

```
cvc5_process_QF_NIA/
├── __init__.py                          # 包初始化文件
├── README.md                            # 本说明文档
├── test_group_get_dis_smt_comp_bert_embeding_single.py  # 数据处理和embedding生成
├── train_predictor.py                   # 预测器模型训练
├── run_predictor.py                     # 运行求解实验
├── analyze_solver_time.py               # 结果分析工具
├── features/                            # Embedding特征存储目录
│   └── QF_NIA_llm_embeddings/          # LLM生成的embeddings
├── models/                              # 训练好的模型存储目录
│   ├── QF_NIA_bert_predictor_mask_best.pth           # 二分类模型（可解性）
│   └── QF_NIA_bert_predictor_2_mask_best_model.pth   # 八分类模型（时间）
├── log/                                 # 日志文件目录
└── supervenn_output/                    # 结果可视化输出目录
```

## 实验流程

### 1. 数据准备和Embedding生成

第一步是处理QF_NIA问题集并生成LLM embeddings：

```bash
cd /home/lz/PycharmProjects/Pearl/test_rl/test_QF_NIA/cvc5_process_QF_NIA
python test_group_get_dis_smt_comp_bert_embeding_single.py
```

**功能说明：**
- 读取`/home/lz/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json`中的QF_NIA问题集
- 对每个SMT文件进行归一化处理
- 使用LLM API（llama3.1:70b）生成8192维的embedding向量
- 将embeddings保存为.npy文件到`features/QF_NIA_llm_embeddings/`目录
- 生成`embeding_QF_NIA.json`记录每个文件的embedding路径和标签
- 自动分割训练集（80%）和测试集（20%），生成`QF_NIA_train.json`和`QF_NIA_test.json`

**输出文件：**
- `embeding_QF_NIA.json`: embedding字典，格式为 `{file_path: [embedding_path, solvability_label, time_label]}`
- `QF_NIA_train.json`: 训练集
- `QF_NIA_test.json`: 测试集

**时间标签说明：**
- 0: ≤1秒
- 1: ≤20秒
- 2: ≤50秒
- 3: ≤100秒
- 4: ≤200秒
- 5: ≤500秒
- 6: ≤1200秒
- 7: >1200秒

### 2. 模型训练

使用生成的embeddings训练两个预测器模型：

**训练二分类模型（可解性预测）：**
```bash
python train_predictor.py --mode binary --epochs 100 --batch_size 32 --lr 0.001
```

**训练八分类模型（求解时间预测）：**
```bash
python train_predictor.py --mode multiclass --epochs 100 --batch_size 32 --lr 0.001
```

**同时训练两个模型：**
```bash
python train_predictor.py --mode both --epochs 100 --batch_size 32 --lr 0.001
```

**模型架构：**

1. **EnhancedClassifier（二分类）**
   - 输入：8192维embedding
   - 结构：FC(8192→2048) + ResBlock + FC(2048→512) + ResBlock + FC(512→128) + FC(128→1)
   - 输出：可解性概率（sigmoid激活）

2. **EnhancedEightClassModelLargeInput（八分类）**
   - 输入：8192维embedding
   - 结构：FC(8192→256) + BN + Dropout + FC(256→128) + BN + Dropout + FC(128→64) + BN + Dropout + FC(64→8)
   - 包含残差连接：residual_fc(8192→8)
   - 输出：8个时间类别的概率分布

**训练特性：**
- 使用Adam优化器
- ReduceLROnPlateau学习率调度
- 早停机制（patience=15/20轮）
- 自动保存最佳模型

### 3. 运行求解实验

使用训练好的预测器模型和强化学习进行SMT求解：

```bash
python run_predictor.py --solver cvc5 --timeout 1200 --max_files 100
```

**参数说明：**
- `--solver`: SMT求解器名称（cvc5, z3, mathsat等）
- `--llm_host`: LLM服务器地址（默认：http://172.29.7.221:32903）
- `--llm_model`: LLM模型名称（默认：llama3.1:70b）
- `--timeout`: 单个问题的超时时间，单位：秒（默认：1200）
- `--max_files`: 最多处理的文件数（None表示处理所有）

**实验过程：**
1. 加载测试集和训练好的预测器模型
2. 对每个QF_NIA问题：
   - 读取并归一化SMT文件
   - 创建强化学习环境（ConstraintSimplificationEnv_test）
   - 使用预测器指导变量赋值
   - 使用LLM生成具体的变量值
   - 通过强化学习优化求解过程
3. 记录求解结果：原始状态、求解时间、成功/失败、反例列表等
4. 定期保存结果到`info_dict_SMTimer_*.txt`

**输出文件：**
- `info_dict_SMTimer_{solver}_{model}_QF_NIA.txt`: 求解结果文件

**结果格式：**
```json
{
  "file_path": [
    "原始状态",      // sat/unsat/unknown
    原始求解时间,     // 秒
    原始超时限制,     // 秒
    执行时间,         // 秒
    "状态",          // succeed/failed
    实际求解时间,     // 秒（如果成功）
    反例,            // 最终成功的变量赋值
    反例列表          // 所有尝试的变量赋值历史
  ]
}
```

### 4. 结果分析

分析求解结果并生成统计报告和可视化图表：

**分析单个结果文件：**
```bash
python analyze_solver_time.py --result_file info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt --plot
```

**比较多个求解器：**
```bash
python analyze_solver_time.py --compare \
    info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt \
    info_dict_SMTimer_z3_llama3.1_70b_QF_NIA.txt \
    --names CVC5 Z3
```

**分析输出：**
- 总问题数、成功率、失败率
- 平均/中位数/最小/最大求解时间
- 平均/中位数加速比
- 求解时间分布（按时间范围统计）

**可视化图表：**
- `solve_time_distribution.png`: 求解时间分布直方图
- `speedup_distribution.png`: 加速比分布直方图
- `time_range_distribution.png`: 时间范围分布柱状图
- `solver_comparison.png`: 多求解器性能比较图（成功率、平均时间、加速比、成功/失败分布）

**分析报告：**
- `solver_time_analysis.json`: JSON格式的详细统计数据

## 依赖环境

### Python包依赖
```
torch>=1.10.0
numpy>=1.20.0
z3-solver>=4.8.0
loguru>=0.5.0
tqdm>=4.60.0
matplotlib>=3.3.0
ollama>=0.1.0
```

### 外部服务
- **LLM服务器**: 需要一个运行llama3.1:70b模型的Ollama服务器
- **SMT求解器**: CVC5、Z3、MathSAT等（根据需要）

### Pearl框架
```
pearl (强化学习框架)
├── policy_learners
├── replay_buffers
├── action_representation_modules
└── history_summarization_modules
```

## 核心组件说明

### 1. 数据处理
- **归一化**：使用`normalize_smt_str()`将SMT文件中的变量名标准化为VAR0, VAR1, ...
- **变量提取**：识别并提取所有非布尔类型变量
- **超时控制**：使用信号机制防止处理过程卡死（30秒超时）

### 2. Embedding生成
- **方法**：使用LLM的embedding API（不是文本生成）
- **维度**：8192维向量
- **缓存**：每个文件的embedding只生成一次，保存为.npy文件

### 3. 预测器模型
- **二分类模型**：预测问题是否可解（SAT vs UNSAT/UNKNOWN）
- **八分类模型**：预测求解时间范围
- **训练策略**：
  - 数据增强：8:2训练测试分割
  - 正则化：Dropout(0.5)、BatchNorm
  - 优化：Adam + ReduceLROnPlateau
  - 早停：防止过拟合

### 4. 强化学习环境
- **状态**：SMT问题的8192维embedding
- **动作**：选择变量并通过LLM生成具体赋值
- **奖励**：
  - 部分约束可满足：+5
  - 预测可解且实际可解：+5
  - 求解成功：+500/timeout * 1000
  - 反例重复：-10
- **策略**：Soft Actor-Critic (SAC)
- **历史总结**：LSTM (hidden_dim=8192)

### 5. 求解流程
1. **预测可解性**：使用二分类模型判断是否值得求解
2. **预测时间**：使用八分类模型选择合适的超时时间
3. **变量选择**：RL agent选择下一个要赋值的变量
4. **值生成**：LLM根据当前状态和反例历史生成具体值
5. **约束验证**：检查部分约束是否满足
6. **完整求解**：所有变量赋值后调用SMT求解器验证

## 实验技巧

### 1. 调试模式
设置`max_files`参数限制处理文件数进行快速测试：
```bash
python run_predictor.py --max_files 10
```

### 2. 断点续传
所有脚本都支持断点续传，已处理的文件会自动跳过。

### 3. 日志管理
- 所有脚本都使用loguru记录详细日志
- 日志文件保存在当前目录和`log/`目录
- 可通过日志文件追踪处理进度和错误

### 4. 内存管理
- 处理完每个文件后自动清理GPU缓存
- 使用`del`显式删除大对象
- 定期保存中间结果防止数据丢失

### 5. 并行处理
当前实现为顺序处理。如需并行：
- 可以手动分割数据集
- 在不同机器上运行多个实例
- 最后合并结果文件

## 常见问题

### 1. LLM连接失败
- 检查LLM服务器是否运行：`curl http://172.29.7.221:32903/api/version`
- 确认模型已加载：`ollama list`
- 检查网络连接和防火墙设置

### 2. 归一化超时
- 某些复杂的SMT文件可能需要很长时间归一化
- 当前设置30秒超时，超时的文件会被跳过
- 可以在代码中调整`signal.alarm(30)`的值

### 3. CUDA内存不足
- 减小batch_size
- 使用CPU训练：`--device cpu`
- 减少RL agent的hidden_dims

### 4. 模型不收敛
- 增加训练轮数
- 调整学习率
- 检查数据集是否平衡
- 尝试不同的模型架构

## 扩展建议

### 1. 支持更多逻辑
- 修改`logic_systems`列表添加其他SMT-LIB逻辑
- 调整模型输入维度以适应不同的embedding大小

### 2. 改进预测器
- 尝试Transformer架构
- 添加图神经网络处理约束结构
- 集成多个预测器（Ensemble）

### 3. 优化RL策略
- 尝试其他RL算法（PPO, A3C等）
- 调整奖励函数
- 添加课程学习（Curriculum Learning）

### 4. 分布式训练
- 使用PyTorch DDP进行多GPU训练
- 实现参数服务器架构

## 引用和参考

本实验框架基于以下组件开发：
- Pearl强化学习框架
- Z3/CVC5 SMT求解器
- Ollama LLM服务
- PyTorch深度学习框架

## 作者和联系方式

如有问题或建议，请联系项目维护者。

---

最后更新：2025-11-01

