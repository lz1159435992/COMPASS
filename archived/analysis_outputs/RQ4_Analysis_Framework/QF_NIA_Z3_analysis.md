# QF_NIA Analysis: Z3

## Inputs

- **cap**: `1200.0`
- **test keys**: `test_rl/predictor/smt_comp_NIA/QF_NIA_test.json`
- **baseline**: `test_rl/test_solve/NIA/NIA.json`
- **COMPASS**: `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`

## Scope: ALL (missing COMPASS treated as 'no_compass')

- **n_keys**: 10043
- **missing_baseline**: 0
- **missing_COMPASS**: 8024

### Solved-set SuperVenn stats

- **baseline solved**: 7603
- **COMPASS solved**: 467
- **baseline only**: 7461
- **COMPASS only**: 325
- **both solved**: 142
- **improvement**: 7603 -> 467 (-7136, -93.86%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 325
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 321

### Baseline time stats (solved only)

- **count**: 7603
- **mean**: 34.493
- **median**: 2.026
- **p90**: 55.246
- **p99**: 768.617
- **min**: 0.011
- **max**: 1199.818

### COMPASS total time stats (succeed only)

- **count**: 467
- **mean**: 225.323
- **median**: 86.397
- **p90**: 713.852
- **p99**: 1168.792
- **min**: 7.917
- **max**: 1200.000

### COMPASS solve time stats (succeed only)

- **count**: 0
- **mean**: N/A
- **median**: N/A
- **p90**: N/A
- **p99**: N/A
- **min**: N/A
- **max**: N/A

### COMPASS LLM time stats (succeed only)

- **count**: 0
- **mean**: N/A
- **median**: N/A
- **p90**: N/A
- **p99**: N/A
- **min**: N/A
- **max**: N/A

## Scope: INTERSECTION (only instances with COMPASS cache)

- **n_keys**: 2019
- **missing_baseline**: 0
- **missing_COMPASS**: 0

### Solved-set SuperVenn stats

- **baseline solved**: 193
- **COMPASS solved**: 467
- **baseline only**: 51
- **COMPASS only**: 325
- **both solved**: 142
- **improvement**: 193 -> 467 (+274, 141.97%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 325
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 321

### Baseline time stats (solved only)

- **count**: 193
- **mean**: 627.000
- **median**: 544.717
- **p90**: 1011.771
- **p99**: 1176.868
- **min**: 301.909
- **max**: 1199.818

### COMPASS total time stats (succeed only)

- **count**: 467
- **mean**: 225.323
- **median**: 86.397
- **p90**: 713.852
- **p99**: 1168.792
- **min**: 7.917
- **max**: 1200.000

### COMPASS solve time stats (succeed only)

- **count**: 0
- **mean**: N/A
- **median**: N/A
- **p90**: N/A
- **p99**: N/A
- **min**: N/A
- **max**: N/A

### COMPASS LLM time stats (succeed only)

- **count**: 0
- **mean**: N/A
- **median**: N/A
- **p90**: N/A
- **p99**: N/A
- **min**: N/A
- **max**: N/A
