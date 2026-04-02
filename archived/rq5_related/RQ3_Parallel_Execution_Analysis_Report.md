# RQ3 并行执行分析报告

## 概述

本报告分析了基于原始数据源的并行执行模拟结果，并与论文中的数据进行对比。

## 数据源

1. **预测+求解结果**: `test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json` (10,043个)
2. **直接求解结果**: `/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json` (20,206个)
3. **COMPASS结果**: `/home/<USER>/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt` (2,019个)

## 预测+求解结果的Status分布

| Status | 数量 |
|--------|------|
| cached_direct_solve | 9,750 |
| failed | 19 |
| succeed | 81 |

## 关键发现

### 1. 直接求解Unknown案例的处理

- 直接求解为unknown的案例数量: 2,440
- 这些案例在Threshold文件中的Status: 全部是`cached_direct_solve`
- 这些案例在Threshold文件中的结果: 全部是`unknown`

**结论**: 预测器将所有unknown案例预测为"简单"或"不可解"，直接使用了直接求解缓存，没有发送到RL+LLM求解器。

### 2. Succeed案例的情况

- Succeed案例数量: 81
- 这些案例的直接求解结果: 全部是`sat`
- 这些案例在Threshold文件中的结果: 全部是`unknown`（结果字段为空）

**结论**: 预测器错误地将81个sat案例预测为"困难"，然后运行了RL+LLM。RL+LLM成功运行（succeed状态），但结果字段没有正确记录。

### 3. 结果差异分析

| 指标 | 直接求解 | Threshold文件 | 差异 |
|------|----------|---------------|------|
| SAT | 6,811 | 6,711 | -100 |
| Unknown | 2,440 | 2,540 | +100 |
| UNSAT | 792 | 792 | 0 |

100个差异案例的Status分布:
- succeed: 81
- failed: 19

## 并行执行模拟结果

### 直接求解 (Direct Solving)

| 指标 | 值 |
|------|-----|
| SAT | 6,811 (67.8%) |
| UNSAT | 792 (7.9%) |
| Unknown | 2,440 (24.3%) |
| SAT平均时间 | 32.9s |
| 总体平均时间 | 317.7s |
| 总时间 | 3,190,248s (886.2h) |

### 并行执行 (Parallel Execution)

| 指标 | 值 |
|------|-----|
| SAT | 6,811 (67.8%) |
| UNSAT | 792 (7.9%) |
| Unknown | 2,440 (24.3%) |
| SAT平均时间 | 22.1s |
| 总体平均时间 | 310.3s |
| 总时间 | 3,116,572s (865.7h) |

### 改进分析

| 指标 | 值 |
|------|-----|
| SAT增加 | +0 |
| Unknown减少 | -0 |
| 时间节省 | 73,676s (20.5h) |
| 时间减少比例 | 2.31% |

### 转换详情

| 类型 | 数量 | 节省时间 |
|------|------|----------|
| Unknown → SAT 转换 | 0 | - |
| SAT案例中COMPASS更快 | 120 | 59,714s |
| SAT案例中Succeed更快 | 66 | 13,962s (3.9h) |
| SAT案例中直接求解更快 | 73 | - |

## 与论文数据对比

### 论文中的Table 7数据

| Strategy | sat | unsat | unknown | sat Avg. (s) | Overall Avg. (s) | Total (s) |
|----------|-----|-------|---------|--------------|------------------|-----------|
| Direct Solving | 6,685 | 792 | 2,440 | 18.4 | 307.6 | 3,089,045 |
| Parallel Execution | 6,764 | 792 | 2,361 | 20.8 | 299.9 | 3,011,928 |

### 当前分析结果

| Strategy | sat | unsat | unknown | sat Avg. (s) | Overall Avg. (s) | Total (s) |
|----------|-----|-------|---------|--------------|------------------|-----------|
| Direct Solving | 6,811 | 792 | 2,440 | 32.9 | 317.7 | 3,190,248 |
| Parallel Execution | 6,811 | 792 | 2,440 | 22.1 | 310.3 | 3,116,572 |

### 差异分析

1. **SAT数量差异**: 论文显示6,685，当前分析显示6,811（差异+126）
2. **Unknown→SAT转换**: 论文显示79个转换，当前分析显示0个转换
3. **时间节省**: 论文显示77,117s，当前分析显示73,676s

## 根本原因分析

论文中的79个unknown→sat转换在当前数据中无法复现，原因是：

1. **预测器行为**: 预测器将所有2,440个unknown案例预测为"简单"或"不可解"，直接使用了直接求解缓存，没有发送到RL+LLM求解器。

2. **COMPASS数据**: COMPASS文件中的193个sat结果，对应的直接求解结果也是sat，没有任何unknown→sat的转换。

3. **Succeed案例**: 81个succeed案例的直接求解结果都是sat，不是unknown。

## 结论

当前的数据源显示并行执行的主要贡献是加速已经能解决的SAT案例，而不是解决新的unknown案例。论文中的79个unknown→sat转换可能来自：
1. 不同的预测器阈值设置
2. 不同的COMPASS实验运行
3. 不同的数据源

## 建议

1. 确认论文中79个转换的数据来源
2. 如果需要获取unknown→sat的转换，需要：
   - 调整预测器阈值，使更多unknown案例被发送到RL+LLM
   - 或者重新运行COMPASS实验，专门针对unknown案例
3. 考虑更新论文数据以反映当前分析结果
