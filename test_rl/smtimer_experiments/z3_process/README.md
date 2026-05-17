# Z3 Process - SMTimer Experiment

This directory contains the Z3 solver experiment scripts for the SMTimer dataset.

## Scripts

| Script | Purpose |
|--------|---------|
| `run_predictor.py` | Main SMTimer experiment with Z3 solver (RL+LLM) |

## Original Location

This script was originally located at:
- `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py`

## Related Directories

Other solver experiments for SMTimer:
- `../cvc5_process/` - CVC5 solver experiments
- `../mathsat5_process/` - MathSAT5 solver experiments
- `../bvparti_process/` - BVParti solver experiments

## Output Files

Results are saved to:
- `info_dict_gai_6_normal_*_SMTimer_*_info_dict_rl.txt`

## Usage

```bash
cd test_rl/smtimer_experiments/z3_process
python run_predictor.py
```
