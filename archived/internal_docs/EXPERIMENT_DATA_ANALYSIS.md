# 实验数据与脚本来源分析报告

## 一、Paper中的RQ结构

根据 `paper/eval.tex`，论文包含三个研究问题：

| RQ | 内容 | 数据集 | 求解器 |
|----|------|--------|--------|
| **RQ1** | Effectiveness | SMTimer + SMT-COMP QF_NIA | Z3, CVC5, MathSAT5, BVParti, AriParti |
| **RQ2** | Ablation (Component Analysis) | SMTimer | Z3 (固定后端) |
| **RQ3** | Parallel Portfolio Utility | SMTimer + SMT-COMP QF_NIA | Z3, CVC5, MathSAT5 |

---

## 二、目录时间线分析

| 目录 | 创建时间 | 状态 |
|------|----------|------|
| `RQ1_Analysis_Framework/` | 2025-08-09 | **已废弃** |
| `RQ2_Analysis_Framework/` | 2025-08-09 | **已废弃** |
| `RQ3_Analysis_Framework/` | 2025-08-09 | **已废弃** |
| `RQ4_Analysis_Framework/` | 2026-03-08 | 部分使用（RQ4未在论文中） |
| `New_RQ1_Effectiveness_Analysis/` | 2026-03-10 | **当前使用** |
| `New_RQ2_Component_Analysis/` | 2026-03-09 | **当前使用** |
| `New_RQ3_Routing_Analysis/` | 2026-03-15 | **当前使用** |

**结论**: `New_RQ*` 系列目录是最新版本，`RQ*_Analysis_Framework` 系列是旧版本（2025年8月），已被废弃。

---

## 三、实验数据来源

### 3.1 SMTimer 实验（RQ1/RQ2/RQ3）

| 求解器 | 数据文件位置 | 文件名模式 |
|--------|--------------|------------|
| Z3 | `test_rl/test_cvc5/z3_process/` | 待补充 |
| CVC5 | `test_rl/test_cvc5/cvc5_process/` | `info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_*.txt` |
| MathSAT5 | `test_rl/test_cvc5/mathsat5_process/` | 待补充 |
| BVParti | `test_rl/test_cvc5/bvparti_process/` | `info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_*.txt` |

### 3.2 SMT-COMP QF_NIA 实验（RQ1/RQ3）

| 求解器 | 数据文件位置 | 文件名模式 |
|--------|--------------|------------|
| Z3 | `test_rl/test_QF_NIA/z3_process_QF_NIA/` | 待补充 |
| CVC5 | `test_rl/test_QF_NIA/cvc5_process_QF_NIA/` | `info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt` |
| MathSAT5 | `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/` | `info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt` |
| AriParti | `test_rl/test_QF_NIA/ariparti_process_QF_NIA/` | `info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt` |

### 3.3 原始基准数据

| 数据集 | 位置 | 用途 |
|--------|------|------|
| SMTimer基准 | `test_rl/test_solve/` | 原始SMT2文件 |
| QF_NIA基准 | `test_rl/test_solve/NIA/` | `NIA.json`, `QF_NIA_test.json` |
| Baseline结果 | `test_rl/test_solve/` | `result_dict_z3solver.txt` 等 |

---

## 四、脚本来源分析

### 4.1 RQ1 (Effectiveness)

**当前使用** (`New_RQ1_Effectiveness_Analysis/`):
- `compute_smtcomp_qf_nia_table.py` - 计算QF_NIA表格
- `generate_rq1_plot.py` - 生成RQ1图表
- `unified_supervenn_generator.py` - SuperVenn图生成
- `Overall_RQ1_RQ2_RQ3_数据核算汇总_20260309.md` - 数据核算汇总

**已废弃** (`RQ1_Analysis_Framework/`):
- `generate_rq1_plot.py` (旧版本)
- `RQ1-effectiveness.pdf` (旧版本图表)

### 4.2 RQ2 (Component Analysis)

**当前使用** (`New_RQ2_Component_Analysis/`):
- `generate_llm_comparison_plot.py` - LLM对比图
- `generate_rq3_performance_plot.py` - 性能曲线图
- `20260309_202958/` - 复算产物目录

**已废弃** (`RQ2_Analysis_Framework/`):
- `generate_rq2_plot.py` (旧版本)
- `RQ2-effectiveness.pdf`, `RQ2-scalability.pdf` (旧版本图表)

### 4.3 RQ3 (Parallel Portfolio)

**当前使用** (`New_RQ3_Routing_Analysis/`):
- `simulate_parallel_portfolio_qf_nia.py` - QF_NIA并行portfolio模拟
- `simulate_parallel_execution.py` - 并行执行模拟
- `analyze_qf_nia_results.py` - QF_NIA结果分析
- `parallel_portfolio_summary.md` - 汇总文档

**已废弃** (`RQ3_Analysis_Framework/`):
- `generate_rq3_plot.py` (旧版本)
- `RQ3-effectiveness.pdf`, `RQ3_performance.pdf` (旧版本图表)
- 大量旧数据文件（`info_dict_bingxing.txt`, `info_dict_sygus.txt` 等）

### 4.4 RQ4 (未在论文中)

`RQ4_Analysis_Framework/` 包含：
- `analyze_qf_nia_results.py`
- `QF_NIA_*_analysis.json/md` - 各求解器分析
- `recompute_intersection_20260308.py`

**注意**: RQ4未出现在 `paper/eval.tex` 中，可能是额外分析或被移除的实验。

---

## 五、数据核算状态

根据 `Overall_RQ1_RQ2_RQ3_数据核算汇总_20260309.md`:

### 与论文一致

| RQ | 表格/图 | 状态 |
|----|---------|------|
| RQ1 | `tab:smtcomp-arith-overall` (QF_NIA) | ✅ 一致 |
| RQ1 | `tab:multi-solver-comparison` (Z3行) | ✅ 一致 |
| RQ1 | `tab:multi-solver-comparison` (CVC5行) | ✅ 一致 |
| RQ2 | `tab:RQ3-ablation` (消融实验) | ✅ 一致 |
| RQ3 | `tab:parallel-execution` | ✅ 一致 |

### 存在差异（需确认）

| RQ | 问题 | 说明 |
|----|------|------|
| RQ2 | `tab:llm-comparison` L3.3/R1行 | 复算与论文数值有差异，可能使用了不同批次数据 |
| RQ1 | SMTimer MathSAT行 | 论文Total=150，复算不一致 |

---

## 六、建议操作

### 6.1 可删除的废弃目录

```
RQ1_Analysis_Framework/
RQ2_Analysis_Framework/
RQ3_Analysis_Framework/
```

这些目录创建于2025年8月，已被 `New_RQ*` 系列替代。

### 6.2 需要保留的目录

```
New_RQ1_Effectiveness_Analysis/   # RQ1当前分析
New_RQ2_Component_Analysis/       # RQ2当前分析
New_RQ3_Routing_Analysis/         # RQ3当前分析
RQ4_Analysis_Framework/           # 额外分析（可选保留）
```

### 6.3 数据文件整理建议

1. **实验输出数据**: 位于 `test_rl/test_cvc5/*/info_dict_*.txt` 和 `test_rl/test_QF_NIA/*/info_dict_*.txt`
2. **基准数据**: 位于 `test_rl/test_solve/`
3. **旧数据文件**: `RQ3_Analysis_Framework/` 中的 `info_dict_bingxing.txt` 等可能是旧版本，可考虑归档

---

## 七、数据流图

```
原始数据
├── SMTimer基准 (test_rl/test_solve/)
│   └── 过滤 (300s timeout, sat only, |V|>=5)
│       ├── Z3实验 → test_rl/test_cvc5/z3_process/
│       ├── CVC5实验 → test_rl/test_cvc5/cvc5_process/
│       ├── MathSAT5实验 → test_rl/test_cvc5/mathsat5_process/
│       └── BVParti实验 → test_rl/test_cvc5/bvparti_process/
│
└── QF_NIA基准 (test_rl/test_solve/NIA/)
    └── 过滤
        ├── Z3实验 → test_rl/test_QF_NIA/z3_process_QF_NIA/
        ├── CVC5实验 → test_rl/test_QF_NIA/cvc5_process_QF_NIA/
        ├── MathSAT5实验 → test_rl/test_QF_NIA/mathsat5_process_QF_NIA/
        └── AriParti实验 → test_rl/test_QF_NIA/ariparti_process_QF_NIA/

分析脚本
├── New_RQ1_Effectiveness_Analysis/ → 生成 Table 3, 4
├── New_RQ2_Component_Analysis/ → 生成 Table 5, Figure 4
└── New_RQ3_Routing_Analysis/ → 生成 Table 6
```

---

## 八、总结

| 项目 | 状态 |
|------|------|
| **当前使用目录** | `New_RQ*_Analysis/` 系列 (2026年3月) |
| **废弃目录** | `RQ*_Analysis_Framework/` 系列 (2025年8月) |
| **实验数据** | 位于 `test_rl/test_cvc5/*/` 和 `test_rl/test_QF_NIA/*/` |
| **基准数据** | 位于 `test_rl/test_solve/` |
| **RQ4** | 未在论文中出现，可能是额外分析 |

**建议**: 将 `RQ1_Analysis_Framework/`, `RQ2_Analysis_Framework/`, `RQ3_Analysis_Framework/` 移动到 `archived/` 目录或删除，以避免混淆。
