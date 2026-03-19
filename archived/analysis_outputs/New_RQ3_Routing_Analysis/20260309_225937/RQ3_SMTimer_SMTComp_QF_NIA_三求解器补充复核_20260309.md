# RQ3 补充数据复核：SMTimer 与 SMT-COMP（QF_NIA）除 parti 外的 3 个求解器（20260309_225937）

本文件用于补充/复核 RQ3 中 **除 Parallel Portfolio(parti) 之外的 3 个求解器**（Z3 / CVC5 / MathSAT）在两个数据集设置下的 Direct vs Parallel 结果，并检查 `New_RQ3_Routing_Analysis/parallel_portfolio_summary.md` 中对应数字的计算是否准确。

- **统一脚本**：`New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py`
- **Cap**：`1200s`
- **并行策略**：baseline solver 与 COMPASS 并行，返回最先得到的 conclusive 结果（`sat/unsat`）；超时视为 `unknown` 且时间按 `1200` 计。

本次复核的 stdout 已落盘在：`New_RQ3_Routing_Analysis/20260309_225937/verify_smtimer_smtcomp/`。

---

## 1) SMTimer（全量 baseline key set；missing COMPASS -> baseline）

对应 `parallel_portfolio_summary.md` 的章节：
- `## 2) SMTimer — Z3 ...`
- `## 3) SMTimer — CVC5 ...`
- `## 4) SMTimer — MathSAT ...`

### 1.1 Z3（SMTimer）
- **复核命令口径**：`--keys_source baseline`，baseline=`test_rl/test_solve/info_dict_bingxing.txt`，compass=`test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`
- **stdout**：`verify_smtimer_smtcomp/SMTimer_Z3_stdout.txt`

**ALL (n=87860)**（用于补充材料的最终口径）：
- **Direct**：sat=36297, unsat=50608, unknown=955, sat Avg.=11.5, Overall Avg.=23.6, Total=2074098
- **Parallel**：sat=36320, unsat=50608, unknown=932, sat Avg.=10.9, Overall Avg.=23.1, Total=2025179

与 `parallel_portfolio_summary.md`：一致（仅存在四舍五入误差）。

### 1.2 CVC5（SMTimer）
- **复核命令口径**：`--keys_source baseline`，baseline=`cvc5_smtimer_results_predictor.json + cvc5_smtimer_results_rl.json`，compass=`...info_dict_rl_cvc5_0628.txt`
- **stdout**：`verify_smtimer_smtcomp/SMTimer_CVC5_stdout.txt`

**ALL (n=87827)**：
- **Direct**：sat=35024, unsat=50935, unknown=1868, sat Avg.=13.9, Overall Avg.=30.4, Total=2670007
- **Parallel**：sat=35341, unsat=50935, unknown=1551, sat Avg.=13.6, Overall Avg.=26.0, Total=2286923

与 `parallel_portfolio_summary.md`：一致（仅存在四舍五入误差）。

### 1.3 MathSAT（SMTimer）
- **复核命令口径**：`--keys_source baseline`，baseline=`mathsat5_smtimer_results_predictor.json + mathsat5_smtimer_results_rl.json`，compass=`...info_dict_rl_mathsat5_0628.txt`
- **stdout**：`verify_smtimer_smtcomp/SMTimer_MathSAT_stdout.txt`

**ALL (n=87827)**：
- **Direct**：sat=36814, unsat=47070, unknown=3943, sat Avg.=2.7, Overall Avg.=60.0, Total=5270574
- **Parallel**：sat=36903, unsat=47070, unknown=3854, sat Avg.=3.8, Overall Avg.=59.3, Total=5205107

与 `parallel_portfolio_summary.md`：一致（仅存在四舍五入误差）。

---

## 2) SMT-COMP（QF_NIA；n=10,043 test keys）

这里你提出“需要补充 QF_NIA 除 parti 外的 3 个求解器结果”。在当前 `parallel_portfolio_summary.md` 中，QF_NIA（test_keys=10043）已经记录了：
- Z3（论文表复现）
- CVC5
- MathSAT

因此本次复核重点是确认 CVC5 / MathSAT 两个“非 Z3”求解器的计算准确性。

### 2.1 CVC5（SMT-COMP QF_NIA）
- **复核命令口径**：`--keys_source test_keys`，baseline=`test_rl/test_QF_NIA/cvc5_QF_NIA.json`，compass=`test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`
- **stdout**：`verify_smtimer_smtcomp/SMTComp_QF_NIA_CVC5_stdout.txt`

**ALL (n=10043)**（对应 summary 的 QF_NIA CVC5 一节）：
- **Direct**：sat=4736, unsat=278, unknown=5029, sat Avg.=50.2, Overall Avg.=626.5, Total=6292385
- **Parallel**：sat=6000, unsat=278, unknown=3765, sat Avg.=83.0, Overall Avg.=501.4, Total=5035761

与 `parallel_portfolio_summary.md`：一致（仅存在四舍五入误差）。

### 2.2 MathSAT（SMT-COMP QF_NIA）
- **复核命令口径**：`--keys_source test_keys`，baseline=`test_rl/test_QF_NIA/mathsat5_QF_NIA.json`，compass=`test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`
- **stdout**：`verify_smtimer_smtcomp/SMTComp_QF_NIA_MathSAT_stdout.txt`

**ALL (n=10043)**：
- **Direct**：sat=6127, unsat=349, unknown=3567, sat Avg.=55.9, Overall Avg.=462.9, Total=4649246
- **Parallel**：sat=6344, unsat=349, unknown=3350, sat Avg.=43.6, Overall Avg.=430.4, Total=4322974

与 `parallel_portfolio_summary.md`：一致（仅存在四舍五入误差）。

---

## 3) 关于 “parti” 的说明（本次额外跑了 AriParti，用于 sanity check）

你这次需求是“除 parti 之外”的 3 个求解器；但我额外跑了一次 AriParti 作为 sanity check：
- **stdout**：`verify_smtimer_smtcomp/SMTComp_QF_NIA_Ariparti_stdout.txt`

该结果不应写入你要求补充的 3-solver 表格中，可仅作为对脚本/口径的额外一致性检查。

---

## 4) 结论（数据是否计算准确？）

- **SMTimer 下 Z3/CVC5/MathSAT**：复算结果与 `parallel_portfolio_summary.md` 中记录的数值一致。
- **SMT-COMP QF_NIA 下 CVC5/MathSAT**：复算结果与 `parallel_portfolio_summary.md` 中记录的数值一致。
- 观测到的差异均为 **显示精度导致的四舍五入差异**（脚本输出保留 3 位小数/浮点累计，summary/paper 通常保留 1 位小数或取整）。
