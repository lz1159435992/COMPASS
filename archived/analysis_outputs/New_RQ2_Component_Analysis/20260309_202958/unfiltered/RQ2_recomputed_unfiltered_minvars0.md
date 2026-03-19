# RQ2 Recomputed Summary (cap=1200.0, min_vars=0)

## Universe selection

- Baseline: `New_RQ2_Component_Analysis/info_dict_bingxing.txt`
- Keep constraints where baseline status in {sat, unknown}, baseline_time>300, and unsat dropped
- Var filter: disabled
- Kept universe size: 1198

## Table RQ2-A: LLM ablation (recomputed)

| Variant | Total | Solved | Rate% | AvgT_all_cap(+tool)s | AvgT_solved_only(+tool)s |
| --- | --- | --- | --- | --- | --- |
| COMPASS_L3.1 | 449 | 96 | 21.4 | 988.5 | 210.6 |
| COMPASS_L3.3 | 449 | 88 | 19.6 | 1042.5 | 396.3 |
| COMPASS_R1 | 449 | 67 | 14.9 | 1105.4 | 566.3 |

## Table RQ2-B: LLM effectiveness breakdown vs Z3 baseline (recomputed)

| Variant | Both(Z3&tool) | Only tool | Only Z3 | Z3 solved total |
| --- | --- | --- | --- | --- |
| COMPASS_L3.1 | 73 | 23 | 170 | 243 |
| COMPASS_L3.3 | 69 | 19 | 174 | 243 |
| COMPASS_R1 | 53 | 14 | 190 | 243 |

## Table RQ2-C: Component ablation (recomputed)

| Method | Total | Solved | Rate% | AvgT_all_cap(+tool)s | AvgT_solved_only(+tool)s |
| --- | --- | --- | --- | --- | --- |
| Random+Random | 449 | 73 | 16.3 | 1066.8 | 380.7 |
| LLM | 449 | 30 | 6.7 | 1120.1 | 4.1 |
| Random+LLM | 449 | 69 | 15.4 | 1066.4 | 330.7 |
| RL+Random | 449 | 89 | 19.8 | 1043.8 | 411.7 |
| RL+LLM | 449 | 96 | 21.4 | 988.5 | 210.6 |

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
