# test_rl 目录清理分析报告

## 一、论文实验需求分析

根据 `paper/eval.tex`，论文包含三个研究问题：

| RQ | 内容 | 数据集 | 求解器 |
|----|------|--------|--------|
| **RQ1** | Effectiveness | SMTimer + SMT-COMP QF_NIA | Z3, CVC5, MathSAT5, BVParti, AriParti |
| **RQ2** | Ablation (Component Analysis) | SMTimer | Z3 (固定后端) |
| **RQ3** | Parallel Portfolio Utility | SMTimer + SMT-COMP QF_NIA | Z3, CVC5, MathSAT5 |

---

## 二、目录大小统计

| 目录 | 大小 | 状态 | 说明 |
|------|------|------|------|
| `test_overfit/` | 3.3G | **保留** | Predictor训练数据 |
| `predictor/` | 1.2G | **保留** | Predictor模型和嵌入 |
| `test_QF_NIA/` | 992M | **保留** | QF_NIA实验数据 |
| `AriParti_sync/` | 934M | **符号链接** | 外部求解器 |
| `test_LLM/` | 737M | **可归档** | LLM分析实验（非核心） |
| `test_cvc5/` | 403M | **保留** | SMTimer实验数据 |
| `test_solve/` | 273M | **保留** | 基准数据 |
| `features/` | 174M | **可归档** | 旧特征文件 |
| `test_script/` | 116M | **保留** | 工具函数 |
| `log/` | 72M | **可清理** | 日志文件 |
| 其他 | <1M | **待定** | 见详细分析 |

---

## 三、核心依赖文件（必须保留）

### 3.1 环境文件
```
test_rl/env_gai_6_llm_add_ce_predictor_docker.py      # 主环境
test_rl/env_gai_6_llm_add_ce_predictor_docker_llm_embed.py
test_rl/env_gai_6_llm_add_ce_predictor_local.py
```

### 3.2 Predictor相关
```
test_rl/bert_embedder_test.py                         # 嵌入器
test_rl/bert_predictor_2_mask.py                      # Predictor模型
test_rl/bert_predictor_mask.py
test_rl/predictor/                                    # Predictor目录
test_rl/test_overfit/                                 # 训练数据
```

### 3.3 工具函数
```
test_rl/test_script/utils.py                          # 核心工具
test_rl/test_script/online_learning_break.py          # 在线学习
test_rl/common/                                       # 公共模块
```

### 3.4 实验目录
```
test_rl/test_cvc5/z3_process/                         # Z3实验
test_rl/test_cvc5/cvc5_process/                      # CVC5实验
test_rl/test_cvc5/mathsat5_process/                  # MathSAT5实验
test_rl/test_cvc5/bvparti_process/                   # BVParti实验
test_rl/test_QF_NIA/z3_process_QF_NIA/               # QF_NIA Z3
test_rl/test_QF_NIA/cvc5_process_QF_NIA/             # QF_NIA CVC5
test_rl/test_QF_NIA/mathsat5_process_QF_NIA/         # QF_NIA MathSAT5
test_rl/test_QF_NIA/ariparti_process_QF_NIA/         # QF_NIA AriParti
test_rl/test_solve/                                   # 基准数据
test_rl/external_references/                          # 外部引用
```

---

## 四、可清理的文件/目录

### 4.1 空文件（共约20个）
```bash
# 空的pkl/pt/pth文件
test_rl/agent_save_1111.pkl
test_rl/bert_predictor_2_mask_best_model.pth
test_rl/BootstrappedDQN-LSTM-return.pt
test_rl/example.txt
test_rl/features.npy
test_rl/predictor.pkl

# 空的info_dict文件
test_rl/info_dict_gai_4_normal729.txt
test_rl/info_dict_gai_4_normal919_QF_BV.txt
test_rl/info_dict_gai_4_normal_924_QF_IDL.txt
test_rl/info_dict_gai_4_normal_924_QF_LRA.txt
```

### 4.2 旧版本实验文件（gai_3, gai_4, gai_5系列）
```
# 旧版本环境（已被env_gai_6替代）
test_rl/env_gai_3.py
test_rl/env_gai_4.py
test_rl/env_gai_4_v2.py

# 旧版本测试脚本
test_rl/test_group_gai_3_normal.py
test_rl/test_group_gai_5_normal_SMTimer.py
test_rl/test_group_gai_5_normal_smt_QF_BV.py
test_rl/test_group_gai_5_normal_smt_QF_LRA.py
```

### 4.3 旧版本info_dict文件（共约80个）
```
# 位于test_rl/根目录的旧实验输出
test_rl/info_dict_3.21.txt
test_rl/info_dict_4.4.txt
test_rl/info_dict_4.8.txt
test_rl/info_dict_4.9.txt
test_rl/info_dict_bingxing.txt
test_rl/info_dict_gai_2.txt
test_rl/info_dict_gai_3_normal.txt
test_rl/info_dict_gai_3_normal64.txt
test_rl/info_dict_gai_4_normal*.txt (约30个)
test_rl/info_dict_gai_6_normal_*.txt (约40个，非最终版本)
```

**注意**: 最终使用的info_dict位于各solver_process目录中

### 4.4 可归档的目录

| 目录 | 大小 | 原因 |
|------|------|------|
| `test_LLM/` | 737M | LLM分析实验，非论文核心实验 |
| `features/` | 174M | 旧特征缓存，已整合到predictor/ |
| `log/` | 72M | 日志文件，可压缩归档 |
| `fig/` | 604K | 旧图表，已整合到New_RQ* |
| `ge_cons/` | 224K | 约束生成测试 |
| `graph_encoder/` | 96K | 图编码器（未使用） |
| `prog_generator/` | 256K | 程序生成器（未使用） |
| `chat_gpt/` | 68K | ChatGPT测试脚本 |
| `test_save/` | 108K | 保存测试 |
| `mathsat_process/` | 32K | 空目录（mathsat5_process在test_cvc5/下） |
| `result_collect/` | 4K | 空目录 |
| `test_rl/archived/` | 16K | 已有归档目录（空） |

### 4.5 重复/备份文件
```
test_rl/AriParti_sync_backup_20250724_221815/  # 476K，已有符号链接
test_rl/test_cvc5/QF_NIA_results/              # 可能在test_QF_NIA/中重复
test_rl/test_cvc5/predict_z3_process/          # RQ5实验，非论文核心
```

### 4.6 日志文件
```
test_rl/log/                                    # 72M日志
test_rl/test_cvc5/solver_script*.log           # 约50M
test_rl/test_LLM/experiment*.log               # 约80M
```

---

## 五、清理建议

### 5.1 立即可删除（空文件）
```bash
find test_rl -maxdepth 1 -type f -empty -delete
```

### 5.2 归档到archived目录
```bash
# 创建归档目录
mkdir -p test_rl/archived/old_experiments
mkdir -p test_rl/archived/old_results
mkdir -p test_rl/archived/old_logs

# 归档旧实验
mv test_rl/env_gai_3.py test_rl/archived/old_experiments/
mv test_rl/env_gai_4.py test_rl/archived/old_experiments/
mv test_rl/env_gai_4_v2.py test_rl/archived/old_experiments/
mv test_rl/test_group_gai_3_normal.py test_rl/archived/old_experiments/
mv test_rl/test_group_gai_5_normal*.py test_rl/archived/old_experiments/

# 归档旧info_dict
mv test_rl/info_dict_3.*.txt test_rl/archived/old_results/
mv test_rl/info_dict_4.*.txt test_rl/archived/old_results/
mv test_rl/info_dict_bingxing.txt test_rl/archived/old_results/
mv test_rl/info_dict_gai_2.txt test_rl/archived/old_results/
mv test_rl/info_dict_gai_3_normal*.txt test_rl/archived/old_results/
mv test_rl/info_dict_gai_4_normal*.txt test_rl/archived/old_results/
mv test_rl/info_dict_gai_6_normal_0*.txt test_rl/archived/old_results/
mv test_rl/info_dict_gai_6_normal_1[0-2]*.txt test_rl/archived/old_results/

# 归档大目录
mv test_LLM test_rl/archived/
mv features test_rl/archived/
mv fig test_rl/archived/
mv ge_cons test_rl/archived/
mv graph_encoder test_rl/archived/
mv prog_generator test_rl/archived/
mv chat_gpt test_rl/archived/
mv test_save test_rl/archived/

# 归档日志
mv log test_rl/archived/old_logs/
```

### 5.3 删除备份和符号链接目标
```bash
# 删除备份（已有符号链接）
rm -rf test_rl/AriParti_sync_backup_20250724_221815

# 删除空目录
rmdir test_rl/mathsat_process
rmdir test_rl/result_collect
```

### 5.4 压缩日志
```bash
tar -czvf test_rl/archived/logs_$(date +%Y%m%d).tar.gz test_rl/test_cvc5/*.log
rm test_rl/test_cvc5/*.log
```

---

## 六、清理后预期结构

```
test_rl/
├── archived/                    # 归档目录
│   ├── old_experiments/
│   ├── old_results/
│   ├── old_logs/
│   └── [其他归档目录]
├── common/                      # 公共模块
├── external_references/         # 外部引用
├── predictor/                   # Predictor模型
├── test_cvc5/                   # SMTimer实验
│   ├── z3_process/
│   ├── cvc5_process/
│   ├── mathsat5_process/
│   └── bvparti_process/
├── test_overfit/                # 训练数据
├── test_QF_NIA/                 # QF_NIA实验
│   ├── z3_process_QF_NIA/
│   ├── cvc5_process_QF_NIA/
│   ├── mathsat5_process_QF_NIA/
│   └── ariparti_process_QF_NIA/
├── test_script/                 # 工具函数
├── test_solve/                  # 基准数据
├── env_gai_6_*.py              # 环境文件
├── bert_*.py                   # Predictor定义
├── embedding*.py               # 嵌入相关
└── [必要的.pth/.pkl模型文件]
```

---

## 七、预计释放空间

| 操作 | 释放空间 |
|------|----------|
| 删除空文件 | ~1M |
| 归档test_LLM | 737M |
| 归档features | 174M |
| 归档log | 72M |
| 删除备份 | 476K |
| 归档其他小目录 | ~1M |
| **总计** | **~1G** |

---

## 八、注意事项

1. **不要删除**:
   - `test_rl/test_solve/NIA/` - 基准数据
   - `test_rl/predictor/smt_comp_NIA/` - QF_NIA predictor
   - `test_rl/test_overfit/models_smtimer_llm/` - 训练好的模型
   - 各solver_process目录下的info_dict文件

2. **符号链接**:
   - `test_rl/AriParti_sync` 是符号链接，不要删除

3. **验证后再删除**:
   - 建议先归档，运行实验确认无问题后再删除归档
