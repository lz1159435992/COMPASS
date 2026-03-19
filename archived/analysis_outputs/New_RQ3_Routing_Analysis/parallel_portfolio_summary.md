# Parallel Portfolio Analysis Summary

## Metric definitions (aligned with `paper/eval.tex` RQ3)
- **Parallel portfolio rule**: run `baseline` and `COMPASS` concurrently; return the first **conclusive** result (`sat`/`unsat`).
- **Timeout/cap**: `1200s`. Any time larger than cap is treated as `unknown` with time `1200`.
- **If COMPASS result missing for a key**: treat as `no_compass` and return baseline (per your instruction).
- **Reported metrics**:
  - `sat/unsat/unknown` counts
  - `sat Avg. (s)`: average time over instances whose final status is `sat`
  - `Overall Avg. (s)`: average time over all instances
  - `Total (s)`: sum of times over all instances

## 1) QF_NIA (Z3 baseline vs Z3||COMPASS+Z3) — paper table reproduction
- **Script**: `New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py`
- **Key set**: `test_keys` (10,043)
- **Baseline**: `test_rl/test_solve/NIA/NIA.json`
- **COMPASS**: `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`

### Results (matches `paper/eval.tex` Table `tab:parallel-execution`)
- **Direct Solving**:
  - sat=6811
  - unsat=792
  - unknown=2440
  - sat Avg.=32.9
  - Overall Avg.=315.9
  - Total=3173055
- **Parallel Portfolio**:
  - sat=7135
  - unsat=792
  - unknown=2116
  - sat Avg.=32.8
  - Overall Avg.=279.1
  - Total=2803371

## 1.1) QF_NIA — CVC5 baseline vs CVC5||COMPASS+CVC5
- **Script**: `New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py`
- **Key set**: `test_keys` (10,043) — same as the Z3 reproduction above
- **Baseline**: `test_rl/test_QF_NIA/cvc5_QF_NIA.json`
- **COMPASS**: `test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`
- **Cap**: 1200

### Results (n=10043)
- **Direct Solving**:
  - sat=4736
  - unsat=278
  - unknown=5029
  - sat Avg.=50.2
  - Overall Avg.=626.5
  - Total=6292385
- **Parallel Portfolio**:
  - sat=6000
  - unsat=278
  - unknown=3765
  - sat Avg.=83.0
  - Overall Avg.=501.4
  - Total=5035761

## 1.2) QF_NIA — MathSAT baseline vs MathSAT||COMPASS+MathSAT
- **Script**: `New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py`
- **Key set**: `test_keys` (10,043) — same as the Z3 reproduction above
- **Baseline**: `test_rl/test_QF_NIA/mathsat5_QF_NIA.json`
- **COMPASS**: `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`
- **Cap**: 1200

### Results (n=10043)
- **Direct Solving**:
  - sat=6127
  - unsat=349
  - unknown=3567
  - sat Avg.=55.9
  - Overall Avg.=462.9
  - Total=4649246
- **Parallel Portfolio**:
  - sat=6344
  - unsat=349
  - unknown=3350
  - sat Avg.=43.6
  - Overall Avg.=430.4
  - Total=4322974

## 2) SMTimer — Z3 baseline full dataset vs Z3||COMPASS+Z3 (COMPASS partial cache=449)
- **Key set**: `baseline` full dataset (`n=87860`)
- **Baseline**: `test_rl/test_solve/info_dict_bingxing.txt` (already replaced from `new_disk` as requested)
- **COMPASS (available for 449 keys)**: `test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt`
- **Cap**: 1200

### Full baseline key set results (n=87860)
- **Baseline**:
  - sat=36297
  - unsat=50608
  - unknown=955
  - sat Avg.=11.5
  - Overall Avg.=23.6
  - Total=2074098
- **Parallel Portfolio** (missing COMPASS -> baseline; on the 449 cached keys, take the faster conclusive one):
  - sat=36320
  - unsat=50608
  - unknown=932
  - sat Avg.=10.9
  - Overall Avg.=23.1
  - Total=2025179
- **Delta (Portfolio - Baseline)**:
  - sat: +23
  - unknown: -23
  - total time saved: 48919s

### Intersection-only view (only keys with COMPASS cache, n=449)
(Useful to understand where gains come from; not the final reported population.)
- **Baseline**:
  - sat=120
  - unsat=0
  - unknown=329
  - sat Avg.=548.0
  - Overall Avg.=1025.8
  - Total=460563
- **Parallel Portfolio**:
  - sat=143
  - unsat=0
  - unknown=306
  - sat Avg.=310.8
  - Overall Avg.=916.8
  - Total=411645

## 3) SMTimer — CVC5 baseline full dataset vs CVC5||COMPASS+CVC5 (COMPASS partial cache=1073)
- **Key set**: `baseline` full dataset (`n=87827`, predictor+rl union)
- **Baseline**:
  - `test_rl/test_cvc5/cvc5_smtimer_results_predictor.json`
  - `test_rl/test_cvc5/cvc5_smtimer_results_rl.json`
- **COMPASS (available for 1073 keys)**: `test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`

### Full baseline key set results (n=87827)
- **Baseline**:
  - sat=35024
  - unsat=50935
  - unknown=1868
  - sat Avg.=13.9
  - Overall Avg.=30.4
  - Total=2670007
- **Parallel Portfolio** (missing COMPASS -> baseline):
  - sat=35341
  - unsat=50935
  - unknown=1551
  - sat Avg.=13.6
  - Overall Avg.=26.0
  - Total=2286923
- **Delta (Portfolio - Baseline)**:
  - sat: +317
  - unknown: -317
  - total time saved: 383084s

### Intersection-only view (only keys with COMPASS cache, n=1073)
- **Baseline**:
  - sat=228
  - unsat=0
  - unknown=845
  - sat Avg.=641.6
  - Overall Avg.=1071.9
  - Total=1150129
- **Parallel Portfolio**:
  - sat=545
  - unsat=0
  - unknown=528
  - sat Avg.=256.5
  - Overall Avg.=714.9
  - Total=767046

## 4) SMTimer — MathSAT baseline full dataset vs MathSAT||COMPASS+MathSAT (COMPASS partial cache=1913)
- **Key set**: `baseline` full dataset (`n=87827`, predictor+rl union; generated on the nju server)
- **Baseline**:
  - `New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/smtimer_710/mathsat5_smtimer_results_predictor.json`
  - `New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/smtimer_710/mathsat5_smtimer_results_rl.json`
- **COMPASS (available for 1913 keys)**:
  - `New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/mathsat5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt`
- **Note (RQ3 rule)**: for keys missing in COMPASS cache, we fall back to baseline (treated as direct execution).

### Full baseline key set results (n=87827)
- **Baseline**:
  - sat=36814
  - unsat=47070
  - unknown=3943
  - sat Avg.=2.7
  - Overall Avg.=60.0
  - Total=5270574
- **Parallel Portfolio**:
  - sat=36903
  - unsat=47070
  - unknown=3854
  - sat Avg.=3.8
  - Overall Avg.=59.3
  - Total=5205107
- **Delta (Portfolio - Baseline)**:
  - sat: +89
  - unknown: -89
  - total time saved: 65467s

### Intersection-only view (only keys with COMPASS cache, n=1913)
- **Baseline**:
  - sat=29
  - unsat=0
  - unknown=1884
  - sat Avg.=798.5
  - Overall Avg.=1193.9
  - Total=2283955
- **Parallel Portfolio**:
  - sat=118
  - unsat=0
  - unknown=1795
  - sat Avg.=546.5
  - Overall Avg.=1159.7
  - Total=2218488


