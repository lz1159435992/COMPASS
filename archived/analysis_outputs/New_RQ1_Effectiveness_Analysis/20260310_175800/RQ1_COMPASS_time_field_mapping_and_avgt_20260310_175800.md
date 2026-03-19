# RQ1 COMPASS time field mapping and solved-only AvgT (update)

Update time: 2026-03-10 17:58:00 (local)

## Purpose
This note fixes the rounding/formatting rule for Table 3/4 Avg. Time and **confirms the final solved-only semantics (Option A)**:

- For \tool runs, we count an instance as solved only if:
  - the run is marked as `succeed`, and
  - the end-to-end time used for AvgT is **\le 1200s** (timeout semantics).

This avoids including edge cases where the log marks `succeed` but the recorded end-to-end time slightly exceeds the timeout.

## Data sources
### SMTimer (Table 3)
- Z3: `/home/lz/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`
- CVC5: `/home/lz/PycharmProjects/Pearl/test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`
- MathSAT: `/home/lz/PycharmProjects/Pearl/RQ4_Analysis_Framework/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt`
- BVParti (latest cache): `/home/lz/PycharmProjects/Pearl/test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0310.txt`

### SMT-COMP / QF_NIA (Table 4)
- Z3: `/home/lz/PycharmProjects/Pearl/test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`
- CVC5: `/home/lz/PycharmProjects/Pearl/test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`
- MathSAT5: `/home/lz/PycharmProjects/Pearl/test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`
- AriParti: `/home/lz/PycharmProjects/Pearl/test_rl/test_QF_NIA/ariparti_process_QF_NIA/info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt`

## Field mapping (COMPASS end-to-end time)
- CVC5/MathSAT/AriParti/QF_NIA variants:
  - time for AvgT: `v[3]` = `total_execution_time`
  - tool success flag: `v[7] == "succeed"`

- Z3 (SMTimer/QF_NIA `info_dict_gai_6_normal_*` format):
  - time for AvgT: `v[3]` = end-to-end execution time
  - tool success flag: `v[4] == "succeed"`

- BVParti (SMTimer):
  - time for AvgT proxy: `v[4] + v[6]` (`total_solve_time + llm_total_time`)
  - tool success flag: `v[7] == "succeed"`

## Final rounding / formatting rule
- Avg. Time values in Table 3 and Table 4 are reported with **1 decimal place**.
- Rounding: `ROUND_HALF_UP`.

## Recomputed AvgT (solved-only, Option A) used in the paper
### Table 3 (SMTimer)
- Z3:
  - Baseline AvgT = 548.0 (n=120, baseline `sat` with time<=1200)
  - +tool AvgT = 210.6 (n=96, `succeed` with time<=1200)
- CVC5:
  - Baseline AvgT = 641.6 (n=228)
  - +tool AvgT = 69.9 (n=360)
- MathSAT:
  - Baseline AvgT = 798.5 (n=29)
  - +tool AvgT = 499.5 (n=100)
- BVParti (latest cache 0310):
  - Baseline AvgT = 693.8 (n=2)
  - +tool succeed count = 0, AvgT = N/A

### Table 4 (SMT-COMP / QF_NIA)
- Z3:
  - Baseline AvgT = 627.0 (n=193)
  - +tool AvgT = 225.3 (n=467)
- CVC5:
  - Baseline AvgT = 612.7 (n=234)
  - +tool AvgT = 252.9 (n=1419)
- MathSAT5:
  - Baseline AvgT = 617.8 (n=345)
  - +tool AvgT = 230.4 (n=505)
- AriParti:
  - Baseline AvgT = 612.4 (n=137)
  - +tool AvgT = 240.6 (n=59)

## Paper update impact
- `paper/eval.tex` Table 3 has been updated to show one decimal place.
- `paper/eval.tex` Table 4 already uses one decimal place, so no data changes were needed.
