# RQ3 并行执行分析更新总结

## 修改概述

将 RQ3 从"选择性简化（基于阈值预测）"改为"并行执行策略"。

## 核心思想

**旧方案**: 使用预测器判断约束难度，阈值≥4的约束才应用 COMPASS 预处理
**新方案**: 求解器与 COMPASS 并行执行，谁先完成用谁的结果

## 数据分析结果

基于 `QF_NIA_advanced_solver_results_all.json` (10,043 约束):

### 数据分布
| 类别 | 数量 |
|------|------|
| Direct solve (cached) | 9,917 |
| - SAT | 6,685 |
| - UNSAT | 792 |
| - Unknown | 2,440 |
| COMPASS SAT | 79 |
| COMPASS other | 10 |
| Failed | 4 |

### 性能对比
| 指标 | 直接求解 | 并行执行 |
|------|----------|----------|
| SAT | 6,685 | 6,764 (+79) |
| UNSAT | 792 | 792 |
| Unknown | 2,440 | 2,361 (-79) |
| SAT 平均时间 | 18.4s | 20.8s |
| 整体平均时间 | 307.6s | 299.9s |
| 总时间 | 3,089,045s | 3,011,928s |

## 关键发现

1. **SAT 提升**: +79 个约束从 unknown 转为 sat (+1.2%)
2. **时间节省**: 总时间减少 77,117s (约 21.4 小时)
3. **平均时间**: 每约束平均时间减少 2.5%
4. **COMPASS 效率**: 新解决的 79 个案例平均执行时间 223.8s（远低于 1200s 超时）

## 修改的文件

1. `paper/eval.tex`:
   - 更新了 RQ3 开头的描述（第 8 行）
   - 重写了 RQ3 小节内容（第 169-220 行）
   - 更新了表格标签从 `tab:routing-performance` 到 `tab:parallel-execution`
   - 更新了表格数据和分析文本

2. `analyze_parallel_execution_rq3.py`:
   - 分析脚本，用于生成并行执行统计数据
   - 包含数据验证功能

## 论文文本变更

### 开头描述（第 8 行）
- 删除: "a mechanism to selectively apply it only to genuinely difficult cases is essential"
- 新增: "RQ3 investigates a parallel execution strategy where the baseline solver and COMPASS run concurrently"

### RQ3 小节
- 删除: 基于预测器阈值的选择性简化策略
- 新增: 并行执行策略，无需预测器，谁先完成用谁的结果

## 验证结果

所有关键数据已验证通过：
- ✓ Direct SAT: 6685
- ✓ Direct UNSAT: 792
- ✓ Direct Unknown: 2440
- ✓ Direct SAT Avg: 18.4s
- ✓ Direct Overall Avg: 307.6s
- ✓ Direct Total: ~3,089,045s
- ✓ Parallel SAT: 6764
- ✓ Parallel Unknown: 2361
- ✓ Parallel SAT Avg: 20.8s
- ✓ Parallel Overall Avg: 299.9s
- ✓ Parallel Total: ~3,011,928s

## 注意事项

1. 原始阈值4方案报告转换了81个 unknown→sat，当前并行执行数据显示79个
2. 差异可能来自数据处理方式或数据集版本的不同
3. 当前分析基于 `QF_NIA_advanced_solver_results_all.json` 的实际数据
