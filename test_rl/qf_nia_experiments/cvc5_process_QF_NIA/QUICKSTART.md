# QF_NIA实验快速开始指南

## 5分钟快速开始

### 1. 环境准备

```bash
# 安装依赖
cd /home/<USER>/PycharmProjects/Pearl/test_rl/qf_nia_experiments/cvc5_process_QF_NIA
pip install -r requirements.txt

# 检查LLM服务
curl http://172.29.7.221:32903/api/version

# 检查SMT求解器
cvc5 --version
```

### 2. 一键运行实验（推荐）

```bash
# 运行完整实验流程（处理所有文件）
./run_experiment.sh

# 或者限制处理文件数（快速测试）
MAX_FILES=10 ./run_experiment.sh
```

这个脚本会自动完成：
1. 生成embeddings（如果不存在）
2. 训练模型（如果不存在）
3. 运行求解实验
4. 分析结果并生成图表

### 3. 分步执行（手动控制）

如果需要更细粒度的控制，可以分步执行：

**步骤1：生成Embeddings**
```bash
python test_group_get_dis_smt_comp_bert_embeding_single.py
# 输出: embeding_QF_NIA.json, QF_NIA_train.json, QF_NIA_test.json
```

**步骤2：训练模型**
```bash
# 训练两个模型
python train_predictor.py --mode both --epochs 100 --batch_size 32

# 或者只训练可解性模型
python train_predictor.py --mode binary --epochs 100

# 或者只训练时间预测模型
python train_predictor.py --mode multiclass --epochs 100
```

**步骤3：运行实验**
```bash
# 使用CVC5求解器
python run_predictor.py --solver cvc5 --timeout 1200

# 使用Z3求解器
python run_predictor.py --solver z3 --timeout 1200

# 限制处理10个文件（快速测试）
python run_predictor.py --solver cvc5 --timeout 1200 --max_files 10
```

**步骤4：分析结果**
```bash
# 分析单个结果文件
python analyze_solver_time.py \
    --result_file info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt \
    --plot

# 比较多个求解器
python analyze_solver_time.py \
    --compare \
        info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt \
        info_dict_SMTimer_z3_llama3.1_70b_QF_NIA.txt \
    --names CVC5 Z3
```

## 调试模式

### 测试少量文件

```bash
# 只处理10个文件进行快速测试
python run_predictor.py --solver cvc5 --max_files 10
```

### 查看日志

```bash
# 实时查看运行日志
tail -f embedding_generation.log
tail -f run_predictor.log

# 查看所有日志
ls log/
```

### 检查中间结果

```python
# 在Python中查看embedding
import numpy as np
import json

# 加载embedding字典
with open('embeding_QF_NIA.json', 'r') as f:
    embed_dict = json.load(f)

# 查看某个文件的embedding
for file_path, info in list(embed_dict.items())[:5]:
    print(f"File: {file_path}")
    print(f"Embedding path: {info[0]}")
    print(f"Solvability: {info[1]}")
    print(f"Time label: {info[2]}")
    
    # 加载embedding
    embedding = np.load(info[0])
    print(f"Shape: {embedding.shape}")
    print()
```

## 常见问题排查

### 问题1：LLM连接失败

```bash
# 检查LLM服务
curl http://172.29.7.221:32903/api/version

# 测试embedding API
curl -X POST http://172.29.7.221:32903/api/embeddings \
    -H "Content-Type: application/json" \
    -d '{"model":"llama3.1:70b","prompt":"test"}'
```

**解决方案：**
- 确保Ollama服务正在运行
- 检查模型是否已加载：`ollama list`
- 修改配置文件中的host地址

### 问题2：CUDA内存不足

**解决方案：**
```bash
# 使用CPU训练
python train_predictor.py --mode both --device cpu --batch_size 16

# 减小batch size
python train_predictor.py --mode both --batch_size 16

# 清理GPU缓存
python -c "import torch; torch.cuda.empty_cache()"
```

### 问题3：模型不收敛

**解决方案：**
- 增加训练轮数：`--epochs 200`
- 调整学习率：`--lr 0.0001`
- 检查数据分布是否平衡
- 查看训练日志中的损失曲线

### 问题4：归一化超时

**解决方案：**
- 跳过问题文件（程序会自动跳过）
- 增加超时时间（修改代码中的`signal.alarm(30)`）
- 检查SMT文件是否过大或过于复杂

## 进阶使用

### 自定义配置

编辑`config.json`文件修改实验参数：

```json
{
  "predictor": {
    "binary_classifier": {
      "learning_rate": 0.0005,
      "batch_size": 64,
      "epochs": 150
    }
  }
}
```

### 批量实验

```bash
# 创建实验脚本
cat > batch_experiment.sh << 'EOF'
#!/bin/bash
for solver in cvc5 z3 mathsat; do
    echo "Running experiment with $solver..."
    python run_predictor.py --solver $solver --timeout 1200
done
EOF

chmod +x batch_experiment.sh
./batch_experiment.sh
```

### 分布式运行

```bash
# 在多台机器上并行运行
# 机器1
python run_predictor.py --solver cvc5 --max_files 1000

# 机器2（从第1001个文件开始，需要修改代码实现）
python run_predictor.py --solver cvc5 --skip 1000 --max_files 1000
```

### 结果合并

```python
import json

# 合并多个结果文件
def merge_results(file1, file2, output):
    with open(file1, 'r') as f:
        results1 = json.load(f)
    with open(file2, 'r') as f:
        results2 = json.load(f)
    
    merged = {**results1, **results2}
    
    with open(output, 'w') as f:
        json.dump(merged, f, indent=4)
    
    print(f"Merged {len(results1)} + {len(results2)} = {len(merged)} results")

# 使用
merge_results(
    'info_dict_SMTimer_cvc5_machine1.txt',
    'info_dict_SMTimer_cvc5_machine2.txt',
    'info_dict_SMTimer_cvc5_merged.txt'
)
```

## 性能优化建议

### 1. 加速embedding生成
- 使用批量API（如果支持）
- 缓存已生成的embeddings
- 并行处理多个文件

### 2. 加速模型训练
- 使用混合精度训练（`torch.cuda.amp`）
- 增大batch size
- 使用多GPU训练（DDP）

### 3. 加速实验运行
- 预先筛选有价值的问题
- 设置合理的超时时间
- 使用更快的求解器

## 输出文件说明

```
cvc5_process_QF_NIA/
├── embeding_QF_NIA.json              # Embedding字典
├── QF_NIA_train.json                  # 训练集
├── QF_NIA_test.json                   # 测试集
├── solver_time_analysis.json          # 分析报告
├── info_dict_SMTimer_*.txt            # 实验结果
├── features/
│   └── QF_NIA_llm_embeddings/        # Embedding文件
│       ├── file1.npy
│       ├── file2.npy
│       └── ...
├── models/
│   ├── QF_NIA_bert_predictor_mask_best.pth           # 二分类模型
│   └── QF_NIA_bert_predictor_2_mask_best_model.pth   # 八分类模型
├── log/
│   ├── embedding_generation.log       # Embedding生成日志
│   ├── training.log                   # 模型训练日志
│   ├── experiment.log                 # 实验运行日志
│   └── analysis.log                   # 结果分析日志
└── supervenn_output/
    ├── solve_time_distribution.png    # 时间分布图
    ├── speedup_distribution.png       # 加速比分布图
    ├── time_range_distribution.png    # 时间范围分布图
    └── solver_comparison.png          # 求解器比较图
```

## 下一步

- 阅读完整的[README.md](README.md)了解详细信息
- 查看[config.json](config.json)了解所有配置项
- 修改代码以适应您的具体需求
- 在不同的SMT逻辑上测试框架

## 获取帮助

如遇到问题：
1. 检查日志文件
2. 参考README.md中的"常见问题"部分
3. 联系项目维护者

祝实验顺利！🚀

