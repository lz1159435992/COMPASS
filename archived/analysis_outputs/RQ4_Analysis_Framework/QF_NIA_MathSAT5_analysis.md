# QF_NIA Analysis: MathSAT5

## Inputs

- **cap**: `1200.0`
- **test keys**: `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/QF_NIA_test.json`
- **baseline**: `test_rl/test_QF_NIA/mathsat5_QF_NIA.json`
- **COMPASS**: `test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt`

## Scope: ALL (missing COMPASS treated as 'no_compass')

- **n_keys**: 10088
- **missing_baseline**: 0
- **missing_COMPASS**: 6490

### Solved-set SuperVenn stats

- **baseline solved**: 6499
- **COMPASS solved**: 505
- **baseline only**: 6211
- **COMPASS only**: 217
- **both solved**: 288
- **improvement**: 6499 -> 505 (-5994, -92.23%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 217
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 217

### Baseline time stats (solved only)

- **count**: 6499
- **mean**: 56.824
- **median**: 3.470
- **p90**: 151.478
- **p99**: 909.088
- **min**: 0.003
- **max**: 1189.802

### COMPASS total time stats (succeed only)

- **count**: 505
- **mean**: 230.403
- **median**: 110.702
- **p90**: 708.551
- **p99**: 1091.886
- **min**: 4.666
- **max**: 1186.234

### COMPASS solve time stats (succeed only)

- **count**: 505
- **mean**: 190.801
- **median**: 85.056
- **p90**: 596.815
- **p99**: 956.996
- **min**: 0.041
- **max**: 1075.508

### COMPASS LLM time stats (succeed only)

- **count**: 505
- **mean**: 10.615
- **median**: 4.596
- **p90**: 26.061
- **p99**: 76.862
- **min**: 1.355
- **max**: 103.019

## Scope: INTERSECTION (only instances with COMPASS cache)

- **n_keys**: 3598
- **missing_baseline**: 0
- **missing_COMPASS**: 0

### Solved-set SuperVenn stats

- **baseline solved**: 345
- **COMPASS solved**: 505
- **baseline only**: 57
- **COMPASS only**: 217
- **both solved**: 288
- **improvement**: 345 -> 505 (+160, 46.38%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 217
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 217

### Baseline time stats (solved only)

- **count**: 345
- **mean**: 617.752
- **median**: 551.309
- **p90**: 1026.412
- **p99**: 1176.938
- **min**: 300.459
- **max**: 1189.802

### COMPASS total time stats (succeed only)

- **count**: 505
- **mean**: 230.403
- **median**: 110.702
- **p90**: 708.551
- **p99**: 1091.886
- **min**: 4.666
- **max**: 1186.234

### COMPASS solve time stats (succeed only)

- **count**: 505
- **mean**: 190.801
- **median**: 85.056
- **p90**: 596.815
- **p99**: 956.996
- **min**: 0.041
- **max**: 1075.508

### COMPASS LLM time stats (succeed only)

- **count**: 505
- **mean**: 10.615
- **median**: 4.596
- **p90**: 26.061
- **p99**: 76.862
- **min**: 1.355
- **max**: 103.019
