================================================================================
Scope: ALL (missing COMPASS treated as 'no_compass') (n=10043, cap=1200.0, compass_time_field=total)
--------------------------------------------------------------------------------
Baseline:
  counts: sat=6811 unsat=792 unknown=2440
  time_sums: sat_sum=224301.326 unsat_sum=37946.788 unknown_sum=2910807.364
  total_time: 3173055.478  overall_avg: 315.947
  per_status_avg: sat=32.932 unsat=47.913 unknown=1192.954
Portfolio (Solver || COMPASS):
  counts: sat=7135 unsat=792 unknown=2116
  time_sums: sat_sum=234285.878 unsat_sum=37946.788 unknown_sum=2531137.930
  total_time: 2803370.596  overall_avg: 279.137
  per_status_avg: sat=32.836 unsat=47.913 unknown=1196.190
--------------------------------------------------------------------------------
Wins: {'no_compass': 8024, 'both_unknown': 1502, 'compass': 444, 'solver': 73}
Disagreements (both conclusive but different): 0
Conversions (baseline -> portfolio):
  sat -> sat: 6811
  unknown -> unknown: 2116
  unsat -> unsat: 792
  unknown -> sat: 324
--------------------------------------------------------------------------------
Time saved total: 369684.882  avg per instance: 36.810
Portfolio faster/slower/equal: 443/39/9561
--------------------------------------------------------------------------------
LaTeX row (portfolio):
Parallel Portfolio & 7135 & 792 & 2116 & 32.8 & 279.1 & 2803371 \\
================================================================================
Scope: INTERSECTION (only instances with COMPASS cache) (n=2019, cap=1200.0, compass_time_field=total)
--------------------------------------------------------------------------------
Baseline:
  counts: sat=193 unsat=0 unknown=1826
  time_sums: sat_sum=121011.077 unsat_sum=0.000 unknown_sum=2182069.434
  total_time: 2303080.511  overall_avg: 1140.704
  per_status_avg: sat=627.000 unsat=0.000 unknown=1195.000
Portfolio (Solver || COMPASS):
  counts: sat=517 unsat=0 unknown=1502
  time_sums: sat_sum=130995.629 unsat_sum=0.000 unknown_sum=1802400.000
  total_time: 1933395.629  overall_avg: 957.601
  per_status_avg: sat=253.376 unsat=0.000 unknown=1200.000
--------------------------------------------------------------------------------
Wins: {'both_unknown': 1502, 'compass': 444, 'solver': 73}
Disagreements (both conclusive but different): 0
Conversions (baseline -> portfolio):
  unknown -> unknown: 1502
  unknown -> sat: 324
  sat -> sat: 193
--------------------------------------------------------------------------------
Time saved total: 369684.882  avg per instance: 183.103
Portfolio faster/slower/equal: 443/39/1537
--------------------------------------------------------------------------------
LaTeX row (portfolio):
Parallel Portfolio & 517 & 0 & 1502 & 253.4 & 957.6 & 1933396 \\
