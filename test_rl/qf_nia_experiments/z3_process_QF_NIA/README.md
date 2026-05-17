# Z3 Process - QF_NIA Experiment

This directory contains the Z3 solver experiment scripts for the QF_NIA (SMT-COMP) benchmark.

## Scripts

| Script | Purpose |
|--------|---------|
| `run_predictor.py` | Main QF_NIA experiment with Z3 solver (RL+LLM) |

## Original Location

This script was originally located at:
- `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py`

## Related Directories

Other solver experiments for QF_NIA:
- `../cvc5_process_QF_NIA/` - CVC5 solver experiments
- `../mathsat5_process_QF_NIA/` - MathSAT5 solver experiments
- `../ariparti_process_QF_NIA/` - AriParti solver experiments

## Output Files

Results are saved to:
- `info_dict_gai_6_normal_*_QF_NIA.txt`

## Usage

```bash
cd test_rl/qf_nia_experiments/z3_process_QF_NIA
python run_predictor.py
```
