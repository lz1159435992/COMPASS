# RQ3 数据源/口径复核与 RL-only 复算结果（20260315_002937）

## 1) 你提出的约束（本次复核采用）

- RQ3 的评测数据不应混入 **predictor 训练/推断产生的数据**。
- QF\_NIA 的评测集应使用：`test_rl/predictor/smt_comp_NIA/QF_NIA_test.json`（10,043 keys）。
- SMTimer 的评测集应使用强化学习方法使用的、未经 300s 过滤的数据：`/home/lz/sibyl_3/src/networks/info_dict_rl.txt`。

## 2) 现有链路中存在的问题（为何需要修正）

### 2.1 SMTimer 的 baseline key set 混入 predictor 数据

在 `New_RQ3_Routing_Analysis/parallel_portfolio_summary.md` 中，SMTimer 的 CVC5/MathSAT baseline 明确使用了：

- `*_smtimer_results_predictor.json` + `*_smtimer_results_rl.json` 的 union

这意味着 SMTimer 的评测 key set 与 baseline 统计 **包含 predictor 数据覆盖的实例**，与“predictor 数据不应作为 RQ3 评测数据”的约束冲突。

此外，这也解释了旧汇总中 SMTimer 的 key set 规模为 `n≈87827`（predictor+rl union），而非 RL-only。

### 2.2 SMTimer 的 "RL-only" 实际 key set 与 `info_dict_rl.txt` 一致（可作为权威 key 集）

本次检查发现：

- `/home/lz/sibyl_3/src/networks/info_dict_rl.txt` 的 key 数为 **43,914**
- `test_rl/test_cvc5/cvc5_smtimer_results_rl.json` 的 key 数为 **43,914**
- `.../mathsat5_smtimer_results_rl.json` 的 key 数为 **43,914**

这说明 SMTimer 的 RL-only 结果文件与 `info_dict_rl.txt` 在 key 覆盖范围上是一致的，可以用 `info_dict_rl.txt` 作为统一的 SMTimer RL-only key set。

## 3) 新的复算脚本与输出（RL-only 口径）

- 新脚本：`New_RQ3_Routing_Analysis/20260315_002937/recompute_rq3_portfolio_rl_only_20260315.py`
- 输出目录：`New_RQ3_Routing_Analysis/20260315_002937/rl_only_outputs/`

该脚本复用统一统计逻辑：`New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py`。

### 3.1 QF\_NIA（test set 10,043）——口径未变，用于 sanity check

- 输出：`rl_only_outputs/QF_NIA_Z3_testkeys.txt`
- 结论：与论文 Table 8（Z3 QF\_NIA Direct vs Parallel）一致。

### 3.2 SMTimer（RL-only key set 43,914）——替换掉 predictor+rl union

#### (a) Z3（SMTimer RL-only）
- 输出：`rl_only_outputs/SMTimer_Z3_rl_only.txt`
- ALL (n=43914)
  - Baseline: sat=17476, unsat=24759, unknown=1679, sat Avg.=6.8, Overall Avg.=20.9, Total=917866
  - Parallel:  sat=17521, unsat=24759, unknown=1634, sat Avg.=6.8, Overall Avg.=21.3, Total=934485
  - Time saved total: **-16618s**（并行总时间略增）

#### (b) CVC5（SMTimer RL-only）
- 输出：`rl_only_outputs/SMTimer_CVC5_rl_only.txt`
- ALL (n=43914)
  - Baseline: sat=17499, unsat=25457, unknown=958,  sat Avg.=14.2, Overall Avg.=31.3, Total=1375910
  - Parallel:  sat=17816, unsat=25457, unknown=641,  sat Avg.=13.6, Overall Avg.=22.6, Total=992826
  - Time saved total: **383084s**

#### (c) MathSAT（SMTimer RL-only）
- 输出：`rl_only_outputs/SMTimer_MathSAT_rl_only.txt`
- ALL (n=43914)
  - Baseline: sat=18449, unsat=23470, unknown=1995, sat Avg.=2.6, Overall Avg.=60.8, Total=2669002
  - Parallel:  sat=18538, unsat=23470, unknown=1906, sat Avg.=4.8, Overall Avg.=59.3, Total=2603535
  - Time saved total: **65467s**

## 4) 备注：关于 key 规范化

- QF\_NIA 使用绝对路径 key（`/home/lz/Downloads/...`），baseline/compass/test_keys 三者一致，因此无需 normalize。
- SMTimer 的不同结果文件可能来自不同机器前缀（例如 `/home/lz/...` vs `/home/nju/...`），因此 SMTimer RL-only 复算默认开启了 `--normalize_keys`。

