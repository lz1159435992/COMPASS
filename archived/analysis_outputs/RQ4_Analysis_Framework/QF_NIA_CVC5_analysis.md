# QF_NIA Analysis: CVC5

## Inputs

- **cap**: `1200.0`
- **test keys**: `test_rl/test_QF_NIA/cvc5_process_QF_NIA/QF_NIA_test.json`
- **baseline**: `test_rl/test_QF_NIA/cvc5_QF_NIA.json`
- **COMPASS**: `test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt`

## Scope: ALL (missing COMPASS treated as 'no_compass')

- **n_keys**: 10088
- **missing_baseline**: 0
- **missing_COMPASS**: 5239

### Solved-set SuperVenn stats

- **baseline solved**: 5030
- **COMPASS solved**: 1419
- **baseline only**: 4878
- **COMPASS only**: 1267
- **both solved**: 152
- **improvement**: 5030 -> 1419 (-3611, -71.79%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 1267
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 1267

### Baseline time stats (solved only)

- **count**: 5030
- **mean**: 51.371
- **median**: 2.940
- **p90**: 128.185
- **p99**: 872.823
- **min**: 0.003
- **max**: 1178.832

### COMPASS total time stats (succeed only)

- **count**: 1419
- **mean**: 252.902
- **median**: 127.075
- **p90**: 728.888
- **p99**: 1136.723
- **min**: 4.608
- **max**: 1191.160

### COMPASS solve time stats (succeed only)

- **count**: 1419
- **mean**: 230.480
- **median**: 108.407
- **p90**: 677.339
- **p99**: 1077.806
- **min**: 0.028
- **max**: 1144.747

### COMPASS LLM time stats (succeed only)

- **count**: 1419
- **mean**: 6.376
- **median**: 3.170
- **p90**: 15.556
- **p99**: 37.863
- **min**: 1.346
- **max**: 84.595

## Scope: INTERSECTION (only instances with COMPASS cache)

- **n_keys**: 4849
- **missing_baseline**: 0
- **missing_COMPASS**: 0

### Solved-set SuperVenn stats

- **baseline solved**: 234
- **COMPASS solved**: 1419
- **baseline only**: 82
- **COMPASS only**: 1267
- **both solved**: 152
- **improvement**: 234 -> 1419 (+1185, 506.41%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 1267
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 1267

### Baseline time stats (solved only)

- **count**: 234
- **mean**: 612.704
- **median**: 524.594
- **p90**: 994.045
- **p99**: 1155.575
- **min**: 300.831
- **max**: 1178.832

### COMPASS total time stats (succeed only)

- **count**: 1419
- **mean**: 252.902
- **median**: 127.075
- **p90**: 728.888
- **p99**: 1136.723
- **min**: 4.608
- **max**: 1191.160

### COMPASS solve time stats (succeed only)

- **count**: 1419
- **mean**: 230.480
- **median**: 108.407
- **p90**: 677.339
- **p99**: 1077.806
- **min**: 0.028
- **max**: 1144.747

### COMPASS LLM time stats (succeed only)

- **count**: 1419
- **mean**: 6.376
- **median**: 3.170
- **p90**: 15.556
- **p99**: 37.863
- **min**: 1.346
- **max**: 84.595
