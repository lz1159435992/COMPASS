# COMPASS

COMPASS is an AI-assisted pre-solver framework for SMT (Satisfiability Modulo Theories) problems that combines Reinforcement Learning (RL) for variable selection with Large Language Models (LLMs) for value suggestions. It works as a solver-agnostic preprocessing layer in front of mainstream SMT solvers (Z3, CVC5, MathSAT, BVParti), improving solved counts and reducing solving time on hard instances.

- Intelligent routing selectively applies the expensive AI simplification to hard constraints, yielding system-wide time savings.
- Extensive evaluation on SMTimer and SMT-COMP (QF_LIA, QF_NIA) with reproducible scripts, logs, and figures.

## Key Features
- RL + LLM synergy: RL for variable selection (primary bottleneck), LLM for value assignment (structured reasoning).
- Solver-agnostic: plug-and-play in front of Z3, CVC5, MathSAT, BVParti, no internal changes required.
- Intelligent routing: predictive models (solvability/time-bucket) send only hard constraints to the AI pipeline.
- Reproducible experiments: end-to-end scripts, logs, and plotting tools for all RQs (effectiveness, ablation, routing).

## Repository Layout (high-level)
- `test_rl/`
  - `test_solve/`: solving experiments, profiling, and figure generation (e.g., SuperVenn, time profiles).
  - `test_cvc5/`: CVC5/Z3 integration for prediction, logs, models, and analysis utilities.
  - `predictor/`: features, time stats, and models for predictive routing.
  - Assorted `test_group_*`, `info_dict_*`, `time_dict_*` scripts and reports used to batch and reproduce experiments.
- `pearl/`: data handling utilities and SMTimer-related resources (e.g., `KNN_training_data`).
- `paper/`: paper sources and figures (e.g., `eval.tex`, `pics/`).
- `tutorials/`: interactive notebooks (e.g., actor-critic and safety modules).
- Misc results and logs: `*.log`, `result_dict_*.txt`, `var_count.txt`, etc.

Note: the repo may include large models and intermediate artifacts. We recommend using Git LFS for `*.pth`, `*.pt`, and large datasets (e.g., `NIA.json`).

## Requirements
- Python 3.10+
- Suggested packages: `z3-solver`, `cvc5` (or native binary), `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn`, `torch`, `transformers`, `tqdm`, `networkx`, etc.
- Optional:
  - Git LFS (for large files: models and datasets)
  - Ollama or another LLM service (if running LLMs locally/remotely)
  - Native SMT solver binaries (Z3, CVC5, MathSAT, BVParti)

Quick install (example):
```bash
pip install -r requirements.txt
# or install packages on demand
```

Enable Git LFS (recommended for large files):
```bash
git lfs install
git lfs track "*.pth" "*.pt" "NIA.json"
git add .gitattributes
git commit -m "track large files via Git LFS"
```

## Quick Start
Run a few example scripts end-to-end (adjust paths/arguments as needed):

```bash
# Generate Z3 SuperVenn and related figures
python test_rl/test_solve/generate_z3_supervenn.py

# CVC5/Z3 routing and prediction pipeline
python test_rl/test_cvc5/predict_z3_process/run_predictor.py

# RQ2: figure generation for ablations/scalability
python test_rl/test_solve/generate_graph_rq2_improved.py
```

Intelligent routing (example):
```bash
python test_rl/test_cvc5/predict_z3_process/rq5_hybrid_screening.py
```

Logs and results:
- `test_rl/test_solve/log/` — solver run logs, time statistics.
- `test_rl/test_cvc5/predict_z3_process/log/` — prediction/routing logs.
- `test_rl/test_solve/*.txt|*.json` — summaries and metrics.
- `paper/pics/` — generated plots (PDF/PNG).

## Datasets & Models
- SMTimer and SMT-COMP benchmarks (QF_LIA, QF_NIA) are used in experiments.
- Predictors and LLM processing may generate large intermediates; use Git LFS or ignore large artifacts locally.
- For full reproducibility, see `paper/` and the scripts in `test_rl/test_solve/` and `test_rl/test_cvc5/`.

## Reproducing Key Results
- Standardized timeout (e.g., 1200s), filtering (exclude baseline ≤300s; focus on `sat/unknown`).
- Compare baseline solvers vs `+COMPASS` preprocessing.
- Routing thresholds (e.g., time-bucket ≥ 4) to target hard cases while keeping routed fraction low.
- Scripts generate solved counts, success rates, mean time, SuperVenn diagrams, and time profiles.

## Large Files Policy (Git LFS)
- We strongly recommend tracking `*.pth`, `*.pt`, and `NIA.json` via Git LFS to avoid GitHub's 100MB hard limit:
```bash
git lfs track "*.pth" "*.pt" "NIA.json"
git add .gitattributes
git commit -m "track large files via Git LFS"
```
- If LFS is not an option, create an export-only branch or filtered mirror excluding >100MB blobs before pushing.

## License
TBD (please add a LICENSE to clarify usage terms).

## Citation
If you use COMPASS in academic work, please cite the accompanying paper (to be provided when available).
