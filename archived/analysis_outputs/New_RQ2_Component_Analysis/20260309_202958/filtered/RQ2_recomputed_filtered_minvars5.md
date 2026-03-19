# RQ2 Recomputed Summary (cap=1200.0, min_vars=5)

## Universe selection

- Baseline: `New_RQ2_Component_Analysis/info_dict_bingxing.txt`
- Keep constraints where baseline status in {sat, unknown}, baseline_time>300, and unsat dropped
- Var filter: keep only constraints with |V| > 5 (from `New_RQ2_Component_Analysis/var_count.txt`)
- Kept universe size: 337

## Table RQ2-A: LLM ablation (recomputed)

| Variant | Total | Solved | Rate% | AvgT_all_cap(+tool)s | AvgT_solved_only(+tool)s |
| --- | --- | --- | --- | --- | --- |
| COMPASS_L3.1 | 337 | 94 | 27.9 | 925.0 | 213.9 |
| COMPASS_L3.3 | 337 | 86 | 25.5 | 996.7 | 403.5 |
| COMPASS_R1 | 337 | 65 | 19.3 | 1079.9 | 577.5 |

## Table RQ2-B: LLM effectiveness breakdown vs Z3 baseline (recomputed)

| Variant | Both(Z3&tool) | Only tool | Only Z3 | Z3 solved total |
| --- | --- | --- | --- | --- |
| COMPASS_L3.1 | 71 | 23 | 1 | 72 |
| COMPASS_L3.3 | 67 | 19 | 5 | 72 |
| COMPASS_R1 | 51 | 14 | 21 | 72 |

## Table RQ2-C: Component ablation (recomputed)

| Method | Total | Solved | Rate% | AvgT_all_cap(+tool)s | AvgT_solved_only(+tool)s |
| --- | --- | --- | --- | --- | --- |
| Random+Random | 337 | 62 | 18.4 | 1055.9 | 416.8 |
| LLM | 337 | 30 | 8.9 | 1093.6 | 4.1 |
| Random+LLM | 337 | 62 | 18.4 | 1040.7 | 334.3 |
| RL+Random | 337 | 84 | 24.9 | 1007.8 | 429.0 |
| RL+LLM | 337 | 94 | 27.9 | 925.0 | 213.9 |

## Inputs (paths and indices)

- var_count: `New_RQ2_Component_Analysis/var_count.txt`
- baseline Z3 info_dict: `New_RQ2_Component_Analysis/info_dict_bingxing.txt`
- COMPASS_L3.1: `test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- COMPASS_L3.3: `test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_llama3.3:70b_1200s_info_dict_rl.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- COMPASS_R1: `test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_deepseek-r1:70b_1200s_info_dict_rl.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- Random+Random: `test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_all_random.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- LLM: `test_rl/info_dict_gai_6_normal_1210_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_llm_only.txt`; idx={base_status:0, base_time:1, tool_time:4, tool_flag:3}
- Random+LLM: `test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- RL+Random: `test_rl/info_dict_gai_6_normal_1223_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random_1223.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
- RL+LLM: `test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`; idx={base_status:0, base_time:1, tool_time:3, tool_flag:4}
