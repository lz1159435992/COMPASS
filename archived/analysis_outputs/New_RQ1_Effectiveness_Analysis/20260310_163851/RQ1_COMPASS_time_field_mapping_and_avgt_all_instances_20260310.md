# RQ1 COMPASS total-time field mapping and AvgT recomputation (all instances, 20260310)

This note records the **time-field mapping** for computing COMPASS end-to-end time from the existing `info_dict` artifacts, and the corresponding **AvgT over all instances** (timeouts are capped at 1200s) used to update `paper/eval.tex` Table 3 (SMTimer) and Table 4 (SMT-COMP/QF_NIA).

## Field mapping rules
- For Z3 (SMTimer/QF_NIA): use `v[3]` as end-to-end total execution time.
- For CVC5/MathSAT/AriParti: use `v[3]` (`total_execution_time`).
- For BVParti: use `v[4] + v[6]` (`total_solve_time + llm_total_time`) as end-to-end time, because `v[3]` may be fixed to 1200 for tool-solved cases.

## AvgT over all instances (cap=1200s, ROUND_HALF_UP, 1 decimal)

- SMTimer/Z3: Total `449`, Baseline AvgT `1025.8`, +tool AvgT `988.5`
- SMTimer/CVC5: Total `1073`, Baseline AvgT `1071.9`, +tool AvgT `756.5`
- SMTimer/MathSAT: Total `1913`, Baseline AvgT `1193.9`, +tool AvgT `1155.4`
- SMTimer/BVParti: Total `33`, Baseline AvgT `1169.3`, +tool AvgT `1073.5`
- QF_NIA/Z3: Total `2019`, Baseline AvgT `1140.7`, +tool AvgT `974.6`
- QF_NIA/CVC5: Total `4849`, Baseline AvgT `1171.7`, +tool AvgT `922.3`
- QF_NIA/MathSAT: Total `3598`, Baseline AvgT `1144.2`, +tool AvgT `646.7`
- QF_NIA/AriParti: Total `1926`, Baseline AvgT `1158.2`, +tool AvgT `1113.9`
