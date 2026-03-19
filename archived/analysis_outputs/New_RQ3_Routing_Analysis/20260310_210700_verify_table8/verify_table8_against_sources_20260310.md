# Table 8 (tab:parallel-execution) Data Verification Record (20260310)

## Sources
- Paper table: `paper/eval.tex` Table `tab:parallel-execution`
- Authoritative summary: `New_RQ3_Routing_Analysis/parallel_portfolio_summary.md`
- Cross-check note: `New_RQ3_Routing_Analysis/20260309_225937/RQ3_SMTimer_SMTComp_QF_NIA_三求解器补充复核_20260309.md`

## Semantics
- Parallel portfolio rule: run `baseline` and `COMPASS` concurrently; return the first **conclusive** result (`sat`/`unsat`).
- Timeout/cap: `1200s`. Any time > cap is treated as `unknown` with time `1200`.
- If COMPASS missing for a key: fall back to baseline.

## Verified Table Values (match `parallel_portfolio_summary.md`)

### SMTimer
- Z3
  - Direct: sat=36297, unsat=50608, unknown=955, sat Avg.=11.5, Overall Avg.=23.6, Total=2074098
  - Parallel: sat=36320, unsat=50608, unknown=932, sat Avg.=10.9, Overall Avg.=23.1, Total=2025179
- CVC5
  - Direct: sat=35024, unsat=50935, unknown=1868, sat Avg.=13.9, Overall Avg.=30.4, Total=2670007
  - Parallel: sat=35341, unsat=50935, unknown=1551, sat Avg.=13.6, Overall Avg.=26.0, Total=2286923
- MathSAT
  - Direct: sat=36814, unsat=47070, unknown=3943, sat Avg.=2.7, Overall Avg.=60.0, Total=5270574
  - Parallel: sat=36903, unsat=47070, unknown=3854, sat Avg.=3.8, Overall Avg.=59.3, Total=5205107

### SMT-COMP (QF_NIA, n=10,043)
- Z3
  - Direct: sat=6811, unsat=792, unknown=2440, sat Avg.=32.9, Overall Avg.=315.9, Total=3173055
  - Parallel: sat=7135, unsat=792, unknown=2116, sat Avg.=32.8, Overall Avg.=279.1, Total=2803371
- CVC5
  - Direct: sat=4736, unsat=278, unknown=5029, sat Avg.=50.2, Overall Avg.=626.5, Total=6292385
  - Parallel: sat=6000, unsat=278, unknown=3765, sat Avg.=83.0, Overall Avg.=501.4, Total=5035761
- MathSAT
  - Direct: sat=6127, unsat=349, unknown=3567, sat Avg.=55.9, Overall Avg.=462.9, Total=4649246
  - Parallel: sat=6344, unsat=349, unknown=3350, sat Avg.=43.6, Overall Avg.=430.4, Total=4322974

## Total Time Reduction (derived)
Computed as `(Direct - Parallel) / Direct`.

- SMTimer
  - Z3: (2074098-2025179)/2074098 = 2.36%
  - CVC5: (2670007-2286923)/2670007 = 14.35%
  - MathSAT: (5270574-5205107)/5270574 = 1.24%

- QF_NIA
  - Z3: (3173055-2803371)/3173055 = 11.65% (paper text reports 11.7%, consistent after rounding)
  - CVC5: (6292385-5035761)/6292385 = 19.97%
  - MathSAT: (4649246-4322974)/4649246 = 7.02%

## Conclusion
All numeric entries currently in `paper/eval.tex` Table `tab:parallel-execution` exactly match the authoritative recomputed results in `parallel_portfolio_summary.md` and the supplemental cross-check note, up to the paper's displayed rounding precision.
