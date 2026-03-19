# QF_NIA Analysis: AriParti

## Inputs

- **cap**: `1200.0`
- **test keys**: `test_rl/test_QF_NIA/ariparti_process_QF_NIA/QF_NIA_test.json`
- **baseline**: `test_rl/AriParti_sync/scripts/batch_output/default/QF_NIA_Ariparti_result_parallel.json`
- **COMPASS**: `test_rl/test_QF_NIA/ariparti_process_QF_NIA/info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt`

## Scope: ALL (missing COMPASS treated as 'no_compass')

- **n_keys**: 10043
- **missing_baseline**: 0
- **missing_COMPASS**: 8117

### Solved-set SuperVenn stats

- **baseline solved**: 8166
- **COMPASS solved**: 59
- **baseline only**: 8133
- **COMPASS only**: 26
- **both solved**: 33
- **improvement**: 8166 -> 59 (-8107, -99.28%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 26
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 26

### Baseline time stats (solved only)

- **count**: 8166
- **mean**: 26.246
- **median**: 1.360
- **p90**: 37.593
- **p99**: 628.970
- **min**: 0.016
- **max**: 1195.349

### COMPASS total time stats (succeed only)

- **count**: 59
- **mean**: 240.593
- **median**: 134.669
- **p90**: 506.404
- **p99**: 1129.413
- **min**: 8.849
- **max**: 1136.057

### COMPASS solve time stats (succeed only)

- **count**: 59
- **mean**: 177.602
- **median**: 116.977
- **p90**: 410.349
- **p99**: 862.113
- **min**: 3.058
- **max**: 943.953

### COMPASS LLM time stats (succeed only)

- **count**: 59
- **mean**: 18.184
- **median**: 11.738
- **p90**: 43.781
- **p99**: 87.525
- **min**: 1.388
- **max**: 116.961

## Scope: INTERSECTION (only instances with COMPASS cache)

- **n_keys**: 1926
- **missing_baseline**: 0
- **missing_COMPASS**: 0

### Solved-set SuperVenn stats

- **baseline solved**: 137
- **COMPASS solved**: 59
- **baseline only**: 104
- **COMPASS only**: 26
- **both solved**: 33
- **improvement**: 137 -> 59 (-78, -56.93%)

### Conversions

- **unknown -> sat (COMPASS succeed)**: 26
- **timeout -> sat (COMPASS succeed, baseline time capped)**: 26

### Baseline time stats (solved only)

- **count**: 137
- **mean**: 612.364
- **median**: 589.847
- **p90**: 938.175
- **p99**: 1129.159
- **min**: 301.831
- **max**: 1162.287

### COMPASS total time stats (succeed only)

- **count**: 59
- **mean**: 240.593
- **median**: 134.669
- **p90**: 506.404
- **p99**: 1129.413
- **min**: 8.849
- **max**: 1136.057

### COMPASS solve time stats (succeed only)

- **count**: 59
- **mean**: 177.602
- **median**: 116.977
- **p90**: 410.349
- **p99**: 862.113
- **min**: 3.058
- **max**: 943.953

### COMPASS LLM time stats (succeed only)

- **count**: 59
- **mean**: 18.184
- **median**: 11.738
- **p90**: 43.781
- **p99**: 87.525
- **min**: 1.388
- **max**: 116.961
