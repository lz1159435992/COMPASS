# RQ1 COMPASS total-time field mapping and AvgT recomputation (20260310)

This note records the **authoritative time-field mapping** for computing COMPASS end-to-end time from the existing `info_dict` artifacts, and the corresponding **solved-only AvgT** values used to update `paper/eval.tex` Table 3 (SMTimer) and Table 4 (SMT-COMP/QF_NIA).

## 1. Field mapping rules

### 1.1 SMTimer / Z3
- **info_dict**: `test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`
- **record format (partial)**:
  - `v[0]`: baseline status
  - `v[1]`: baseline time
  - `v[3]`: COMPASS total execution time (end-to-end)
  - `v[4]`: COMPASS status flag (`succeed`/`success`)
- **COMPASS total time**: `v[3]`

### 1.2 SMTimer / CVC5
- **info_dict**: `test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`
- **record format (partial)**:
  - `v[0]`: baseline status
  - `v[1]`: baseline time
  - `v[3]`: `total_execution_time` (end-to-end)
  - `v[4]`: `total_solve_time` (accumulated solver time)
  - `v[5]`: `final_solve_time`
  - `v[6]`: `llm_total_time`
  - `v[7]`: status flag
- **COMPASS total time**: `v[3]`

### 1.3 SMTimer / MathSAT
- **info_dict**: `RQ4_Analysis_Framework/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt`
- **record format** is the same as SMTimer/CVC5.
- **COMPASS total time**: `v[3]`

### 1.4 SMTimer / BVParti
- **info_dict**: `test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0728.txt`
- **record format** is the same as SMTimer/CVC5.
- **Important caveat**: `v[3]` (`total_execution_time`) is fixed to `1200.0` for tool-solved cases (not usable as end-to-end time).
- **COMPASS total time (workaround)**: use `v[4] + v[6]` (solver accumulated time + LLM accumulated time) as end-to-end time.
- **Solved (+tool)**: BVParti uses `rl_solutions` (index `9`) rather than status flag.

### 1.5 QF_NIA / Z3
- **info_dict**: `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`
- **record format (partial)**:
  - `v[0]`: baseline status
  - `v[1]`: baseline time
  - `v[3]`: COMPASS total execution time (end-to-end)
  - `v[4]`: COMPASS status flag
- **COMPASS total time**: `v[3]`

### 1.6 QF_NIA / CVC5, MathSAT, AriParti
- **info_dicts**:
  - `test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`
  - `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`
  - `test_rl/test_QF_NIA/ariparti_process_QF_NIA/info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt`
- **record format** is the same as SMTimer/CVC5.
- **COMPASS total time**: `v[3]`

## 2. Solved-only AvgT values (cap=1200s, ROUND_HALF_UP)

Solved-only average time is computed over instances where:
- baseline solved: status in `{sat,unsat}` and within-cap
- tool solved: status flag in `{succeed,success}` and within-cap
- BVParti tool solved: `rl_solutions` contains at least one non-empty assignment list and within-cap

### 2.1 Table 3 (SMTimer) AvgT
- Z3: Baseline `548.0`, +tool `210.6` (time index `3`)
- CVC5: Baseline `641.6`, +tool `69.9` (time index `3`)
- MathSAT: Baseline `798.5`, +tool `499.5` (time index `3`)
- BVParti: Baseline `693.8`, +tool `462.9` (time index `4+6`)

### 2.2 Table 4 (SMT-COMP/QF_NIA) AvgT
- Z3: Baseline `627.0`, +tool `225.3` (time index `3`)
- CVC5: Baseline `612.7`, +tool `252.9` (time index `3`)
- MathSAT: Baseline `617.8`, +tool `230.4` (time index `3`)
- AriParti: Baseline `612.4`, +tool `240.6` (time index `3`)
