# RQ1 Table Recompute Snapshot (20260308_230448)

This folder is a reproducibility snapshot for the unified **RQ1 mouth** used to update `paper/eval.tex`.

## Mouth (rules)

- **Variable filtering (SMTimer)**: keep constraints with `#vars >= 5`.
  - Variable count is computed by parsing the SMT2 script and counting distinct symbols in `(declare-fun ...)`.
- **Timeout cap decision**: determine whether a run is within cap by **ROUND_HALF_UP rounding to integer seconds first**.
  - Example: `1200.0035 -> 1200`, therefore it is still treated as within-cap.
- **Solved definition**:
  - Baseline solved: status in `{sat, unsat}` AND time is within-cap under the rounding rule.
  - +COMPASS solved: flag in `{succeed, success}` AND the chosen +COMPASS time field is within-cap under the rounding rule.

## Scripts

- `recompute_intersection_20260308.py`
  - Computes intersection stats under the mouth above.
  - Tasks:
    - `smtimer_cvc5`: reads the SMTimer CVC5 cache (python-literal dict), applies `min_vars`, and computes intersection.
    - `qf_nia_z3`: reads the QF_NIA Z3 cache (JSON dict) and computes intersection.

- `run_recompute_rq1_tables_20260308.py`
  - Convenience wrapper to reproduce the key rows used in `paper/eval.tex`.

## How to run

From repo root:

```bash
python New_RQ1_Effectiveness_Analysis/20260308_230448/run_recompute_rq1_tables_20260308.py
```

Or run the underlying script directly:

```bash
python New_RQ1_Effectiveness_Analysis/20260308_230448/recompute_intersection_20260308.py \
  --task qf_nia_z3 \
  --info test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt \
  --cap 1200
```

```bash
python New_RQ1_Effectiveness_Analysis/20260308_230448/recompute_intersection_20260308.py \
  --task smtimer_cvc5 \
  --info test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt \
  --cap 1200 \
  --min_vars 5 \
  --compass_time_idx 6 \
  --compass_flag_idx 7
```
