# RQ1 Recomputed Summary (cap=1200.0, min_vars=0)

## Mouth (unified rules)

- Variable filtering on SMTimer: keep instances with `#vars >= min_vars` (counted from SMT2 `(declare-fun ...)` / `(declare-const ...)`, including quoted symbols like `|...|`).
- Timeout cap: decide within-cap by `ROUND_HALF_UP` rounding to integer seconds first, then compare with cap.
- Solved (baseline): status in `{sat, unsat}` AND within-cap.
- Solved (+tool): flag in `{succeed, success}` AND within-cap.
- Avg time: per-instance time is `t` if within-cap else `cap`; then averaged over all instances in the row.

## Table A: SMTimer multi-solver performance (recomputed)

| Solver | Total | Solved(Base) | Solved(+tool) | Rate(Base)% | Rate(+tool)% | AvgT(Base)s | AvgT(+tool)s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Z3 | 449 | 120 | 96 | 26.7 | 21.4 | 1025.8 | 988.5 |
| CVC5 | 1073 | 228 | 360 | 21.2 | 33.6 | 1072.0 | 402.5 |
| BVParti | 33 | 2 | 19 | 6.1 | 57.6 | 1169.4 | 132.8 |
| MathSAT | 1913 | 29 | 100 | 1.5 | 5.2 | 1193.9 | 206.1 |

## Table B: SMT-COMP/QF_NIA multi-solver performance (recomputed)

| Solver | Total | Solved(Base) | Solved(+tool) | Rate(Base)% | Rate(+tool)% | AvgT(Base)s | AvgT(+tool)s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Z3 | 2019 | 193 | 467 | 9.6 | 23.1 | 1140.8 | 974.6 |
| CVC5 | 4849 | 234 | 1419 | 4.8 | 29.3 | 1171.8 | 922.3 |
| MathSAT5 | 3598 | 345 | 505 | 9.6 | 14.0 | 1144.2 | 646.7 |
| AriParti | 1926 | 137 | 59 | 7.1 | 3.1 | 1158.2 | 1113.9 |

## Table C: Intersection analysis (recomputed)

### SMTimer

| Solver | Both | Only +tool | Only Base | Base Total | Retention% |
| --- | --- | --- | --- | --- | --- |
| Z3 | 73 | 23 | 47 | 120 | 60.8 |
| CVC5 | 43 | 317 | 185 | 228 | 18.9 |
| BVParti | 2 | 17 | 0 | 2 | 100.0 |
| MathSAT | 11 | 89 | 18 | 29 | 37.9 |

### SMT-COMP/QF_NIA

| Solver | Both | Only +tool | Only Base | Base Total | Retention% |
| --- | --- | --- | --- | --- | --- |
| Z3 | 142 | 325 | 51 | 193 | 73.6 |
| CVC5 | 152 | 1267 | 82 | 234 | 65.0 |
| MathSAT5 | 288 | 217 | 57 | 345 | 83.5 |
| AriParti | 33 | 26 | 104 | 137 | 24.1 |

## Self-checks

- Intersection identity: `Solved(+tool) == Both + Only +tool`, `Solved(Base) == Both + Only Base` (should hold per row).

## Inputs (paths and indices)

- **SMT-COMP/QF_NIA/AriParti**: `test_rl/test_QF_NIA/ariparti_process_QF_NIA/info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 3, 'tool_flag_idx': 7}; kept=1926 (from total=1926, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMT-COMP/QF_NIA/CVC5**: `test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 3, 'tool_flag_idx': 7}; kept=4849 (from total=4849, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMT-COMP/QF_NIA/MathSAT5**: `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 3, 'tool_flag_idx': 7}; kept=3598 (from total=3598, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMT-COMP/QF_NIA/Z3**: `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 3, 'tool_flag_idx': 4}; kept=2019 (from total=2019, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMTimer/BVParti**: `test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0728.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 4, 'tool_flag_idx': 7}; kept=33 (from total=33, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMTimer/CVC5**: `test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 6, 'tool_flag_idx': 7}; kept=1073 (from total=1073, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMTimer/MathSAT**: `RQ4_Analysis_Framework/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 6, 'tool_flag_idx': 7}; kept=1913 (from total=1913, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
- **SMTimer/Z3**: `test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`; idx={'base_status_idx': 0, 'base_time_idx': 1, 'tool_time_idx': 3, 'tool_flag_idx': 4}; kept=449 (from total=449, filtered_lt_min_vars=0, missing_smt2_for_var_count=0)
