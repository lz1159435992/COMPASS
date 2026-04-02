# RQ1 COMPASS time field mapping and solved-only AvgT (update)

Update time: 2026-03-10 17:06:50 (local)

## Purpose
This note re-verifies SMTimer Table 3 numbers using the latest artifacts, focusing on:
- SMTimer/CVC5 `+tool` Avg. Time (solved-only)
- SMTimer/BVParti `+tool` statistics using the latest COMPASS cache `..._0310.txt`

## Data sources
- SMTimer/CVC5 info_dict:
  - `/home/<USER>/PycharmProjects/Pearl/test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`
- SMTimer/BVParti latest info_dict (COMPASS cache):
  - `/home/<USER>/PycharmProjects/Pearl/test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0310.txt`

## Field mapping (COMPASS end-to-end time)
- For CVC5 predictor `info_dict`:
  - Use `v[3]` = `total_execution_time` (end-to-end)
  - Tool success indicator: `v[7] == "succeed"`
  - Solved criterion for AvgT: only instances with `v[7]=="succeed"`.

- For BVParti predictor `info_dict`:
  - The recorded `v[3]` (`total_execution_time`) can be saturated to `1200` and is not reliable for end-to-end time on tool-solved cases.
  - Use `v[4] + v[6]` (`total_solve_time + llm_total_time`) as the proxy end-to-end time.
  - Tool success indicator: `v[7] == "succeed"`.

## Recomputed results (solved-only)
### SMTimer / CVC5 (+tool)
- Total instances: 1073
- Tool succeed count: 360
- AvgT solved-only (mean of `v[3]` over `v[7]=="succeed"`):
  - raw mean = 69.92273531887267
  - rounded (ROUND_HALF_UP) = 70

### SMTimer / BVParti (+tool) using latest cache `..._0310.txt`
- Total instances: 33
- Tool succeed count: 0
- AvgT solved-only: N/A (no succeed instances)

## Paper update impact
- `paper/eval.tex` Table 3 (SMTimer):
  - CVC5 `+tool Avg. Time` remains `70`.
  - BVParti `+tool` should be updated to:
    - solved constraints: `0`
    - success rate: `0.0%`
    - Avg. Time: `--` (undefined under solved-only semantics)

- Intersection table (SMTimer/BVParti) should be consistent with the above:
  - Both solved = 0
  - Only tool = 0
  - Only baseline = 2
  - Retention rate = 0.0%
