# COMPASS: Reinforcement Learning and LLM-Guided Variable Concretization for Efficient SMT Solving

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

COMPASS is a dual-agent AI framework for SMT (Satisfiability Modulo Theories) constraint simplification, combining Reinforcement Learning (RL) for variable selection with Large Language Models (LLM) for value generation.

## Overview

COMPASS addresses the challenge of solving complex SMT constraints by:

1. **Variable Selection (RL Agent)**: Uses reinforcement learning to identify which variables to simplify first, based on learned structural features of constraints.

2. **Value Generation (LLM Agent)**: Employs large language models to generate candidate values for selected variables, leveraging pattern recognition from training data.

3. **Hybrid Reward System**: Combines solver feedback with predictor confidence to guide the simplification process.

## Key Features

- **Variable Normalization**: Standardizes variable naming based on structural importance (clause size, frequency, logic operations)
- **Binary Predictor**: Predicts constraint satisfiability for efficient filtering
- **8-way Time Predictor**: Estimates solving time to enable selective simplification
- **Multi-solver Support**: Works with Z3, CVC5, MathSAT5, and BVParti

## Methodology

### Architecture

COMPASS employs a dual-agent architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMPASS Framework                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐         ┌─────────────┐                      │
│   │  RL Agent   │         │  LLM Agent  │                      │
│   │ (Variable   │         │  (Value     │                      │
│   │  Selection) │         │ Generation) │                      │
│   └──────┬──────┘         └──────┬──────┘                      │
│          │                       │                              │
│          ▼                       ▼                              │
│   ┌─────────────────────────────────────┐                      │
│   │         Hybrid Reward System        │                      │
│   │  (Solver Feedback + Predictor Conf) │                      │
│   └─────────────────────────────────────┘                      │
│                      │                                          │
│                      ▼                                          │
│   ┌─────────────────────────────────────┐                      │
│   │         SMT Solver (Z3, etc.)       │                      │
│   └─────────────────────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Variable Normalization

Before processing, constraints are normalized using structural features:

1. **Clause Size**: Sum of sizes of clauses containing the variable
2. **Clause Count**: Number of distinct clauses containing the variable
3. **Frequency**: Total occurrences in the formula
4. **Logic Operations**: Number of logic operations involving the variable
5. **Constant Co-occurrence**: Clauses where variable appears with constants

Variables are renamed as `VAR1, VAR2, ...` based on descending structural importance.

### Predictors

| Predictor | Purpose | Output |
|-----------|---------|--------|
| Binary Predictor | Satisfiability prediction | SAT/UNSAT |
| 8-way Time Predictor | Solving time estimation | Time bins: <1s, 1-5s, 5-30s, 30-60s, 60-120s, 120-300s, 300-600s, >600s |

### RL Training

- **Algorithm**: Soft Actor-Critic (SAC)
- **State**: Constraint embedding (CodeBERT) + history
- **Action**: Variable selection for simplification
- **Reward**: Solver time improvement + predictor confidence

## Project Structure

```
COMPASS/
├── pearl/                           # Pearl RL framework (from Meta)
├── test_rl/                         # COMPASS core code
│   ├── smtimer_experiments/         # SMTimer benchmark experiments (multi-solver)
│   ├── qf_nia_experiments/          # QF_NIA benchmark experiments
│   ├── test_overfit/                # Predictor training scripts
│   ├── test_LLM/                    # LLM variable selection experiments
│   ├── test_script/                 # Core utilities (variable normalization, etc.)
│   ├── test_solve/                  # Baseline solver caches
│   ├── predictor/                   # Predictor models and embeddings
│   ├── common/                      # Shared modules
│   ├── external_references/         # External dependency placeholders
│   └── archived/                    # Archived files
├── archived/                        # Project-level archived files
├── paper/                           # Paper source code (LaTeX)
├── docs/                            # Documentation
├── config.py                        # Centralized path configuration
└── requirements.txt                 # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended)
- Z3 solver (for constraint solving)

### Setup

```bash
# Clone the repository
git clone https://github.com/lz1159435992/COMPASS.git
cd COMPASS

# Install Pearl (RL framework)
cd pearl && pip install -e . && cd ..

# Install dependencies
pip install -r requirements.txt

# Install Z3 solver
pip install z3-solver
```

### Configuration

1. **External Dependencies**: Some scripts reference external data files. Placeholders are provided in `test_rl/external_references/`. Replace these with your actual data.

2. **Path Configuration**: Use `config.py` for centralized path management:

```python
from config import get_baseline_path, get_external_file

# Get baseline file path
nia_path = get_baseline_path('NIA')

# Get external reference file
rl_dict_path = get_external_file('info_dict_rl')
```

### Solver Installation

COMPASS supports multiple SMT solvers. Standard solvers can be installed via:

```bash
# Z3 (required)
pip install z3-solver

# CVC5 (optional)
sudo apt-get install cvc5

# MathSAT5 (optional)
# Download from https://mathsat.fbk.eu/
```

#### Solver Versions

The following solver versions were used in the experiments reported in the paper:

| Solver | Version |
|--------|---------|
| CVC5 | 1.2.1 |
| MathSAT5 | 5.6.11 |
| Z3 | 4.12.4 |

For external solvers, see `SOLVER_INSTALLATION.md` for detailed installation instructions:

| External Solver | Used For | Version / Build |
|----------------|----------|-----------------|
| BVParti | Bit-vector constraints (QF_BV) in the SMTimer backend | SMT-COMP 2025 build (`STP-Parti-Bitwuzla-at-SMT-COMP-2025`); includes `bitwuzla-0.8.0` |
| AriParti | Non-linear integer arithmetic (QF_NIA) in the SMT-COMP backend | AriParti repository build (see `SOLVER_INSTALLATION.md`) |

#### Checking Solver Availability

```python
from config import check_solver_available

# Check if a solver is installed
if check_solver_available('z3'):
    print("Z3 is available")
if check_solver_available('bvparti'):
    print("BVParti is available")
```

## Usage

### Running Experiments

#### SMTimer Z3 Experiment (RQ1)

```bash
cd test_rl
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py
```

#### QF_NIA Benchmark Experiment

```bash
cd test_rl
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py
```

#### RQ2 Ablation Experiments

```bash
# RL + LLM (full COMPASS)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py

# LLM only (no RL)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_llm_only_v2.py

# Random selection (baseline)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_random_1223.py
```

### Training Predictors

```bash
cd test_rl/test_overfit
python train_smtimer_llm_predictors.py
```

### Variable Normalization

```python
from test_rl.test_script.utils import normalize_smt_str

# Normalize SMT-LIB2 constraint
smtlib_str = "(declare-fun x () Int) (assert (> x 0))"
normalized, var_dict, constants = normalize_smt_str(smtlib_str)
```

## Experimental Results

> **Quick View**: Run `python scripts/show_results.py` to display all experimental results in formatted tables.

### RQ1: Effectiveness

**Question**: How effectively does COMPASS improve the solving capability of diverse SMT solver architectures on hard satisfiable constraints?

#### SMTimer Results (hard satisfiable subset)

| Solver | Total | Baseline Solved | COMPASS Solved | Baseline Avg.Time(s) | COMPASS Avg.Time(s) | Retention(%) |
|--------|-------|-----------------|----------------|----------------------|---------------------|--------------|
| Z3 | 449 | 120 | 96 | 548.0 | 210.6 | 60.8 |
| CVC5 | 1073 | 228 | 360 | 641.6 | 69.9 | 18.9 |
| MathSAT | 1913 | 29 | 100 | 798.5 | 499.5 | 37.9 |
| BVParti | 33 | 2 | 0 | 693.8 | - | 0.0 |

#### SMT-COMP QF_NIA Results (hard satisfiable subset)

| Solver | Total | Baseline Solved | COMPASS Solved | Baseline Avg.Time(s) | COMPASS Avg.Time(s) | Retention(%) |
|--------|-------|-----------------|----------------|----------------------|---------------------|--------------|
| Z3 | 2019 | 193 | 467 | 627.0 | 225.3 | 73.6 |
| CVC5 | 4849 | 234 | 1419 | 612.7 | 252.9 | 65.0 |
| MathSAT | 3598 | 345 | 505 | 617.8 | 230.4 | 83.5 |
| AriParti | 1926 | 137 | 59 | 612.4 | 240.6 | 24.1 |

**Answer**: COMPASS improves effectiveness for several major solver families, with the strongest gain on CVC5, which solves **506.4%** more QF_NIA instances. The benefits are less stable on partitioning-based backends (BVParti, AriParti).

### RQ2: Component Analysis

**Question**: How do RL-guided variable selection and LLM value proposal contribute to the overall effectiveness?

#### LLM Ablation Study (SMTimer, Z3 backend, Total=449)

| Model Variant | Solved | Success Rate(%) | Avg.Time(s) | Retention(%) |
|---------------|--------|-----------------|-------------|--------------|
| COMPASS (LLaMA 3.1 70B) | 96 | 21.4 | 210.6 | 60.8 |
| COMPASS (LLaMA 3.3 70B) | 88 | 19.6 | 396.3 | 57.5 |
| COMPASS (DeepSeek-R1 70B) | 67 | 14.9 | 566.3 | 44.2 |

#### Component Ablation Study (SMTimer, Z3 backend, Total=449)

| Method | Solved | Success Rate(%) | Avg.Time(s) |
|--------|--------|-----------------|-------------|
| Random+Random | 73 | 16.3 | 380.7 |
| LLM only | 30 | 6.7 | 4.1 |
| Random+LLM | 69 | 15.4 | 330.7 |
| RL+Random | 89 | 19.8 | 411.7 |
| **RL+LLM (COMPASS)** | **96** | **21.4** | **210.6** |

**Answer**: Effectiveness is governed primarily by **RL-guided variable selection**. The LLM contributes modestly to coverage but significantly improves efficiency when paired with good variable choices.

### RQ3: Parallel Portfolio Utility

**Question**: Can COMPASS improve practical deployment performance when used as a parallel portfolio component?

#### Parallel Portfolio Results (SMTimer: 43,914 instances)

| Solver | Strategy | SAT Solved | Unknown | Total(h) | Total Red.(%) |
|--------|----------|------------|---------|----------|---------------|
| Z3 | Direct | 17,476 | 1,679 | 255.0 | - |
| Z3 | Parallel | 17,521 | 1,634 | 259.6 | -1.8 |
| CVC5 | Direct | 17,499 | 958 | 382.2 | - |
| CVC5 | Parallel | 17,816 | 641 | 275.8 | **27.8** |
| MathSAT | Direct | 18,449 | 1,995 | 741.4 | - |
| MathSAT | Parallel | 18,538 | 1,906 | 723.2 | 2.5 |

#### Parallel Portfolio Results (SMT-COMP QF_NIA: 10,043 instances)

| Solver | Strategy | SAT Solved | Unknown | Total(h) | Total Red.(%) |
|--------|----------|------------|---------|----------|---------------|
| Z3 | Direct | 6,811 | 2,440 | 881.4 | - |
| Z3 | Parallel | 7,135 | 2,116 | 778.7 | **11.7** |
| CVC5 | Direct | 4,736 | 5,029 | 1,747.9 | - |
| CVC5 | Parallel | 6,000 | 3,765 | 1,398.8 | **20.0** |
| MathSAT | Direct | 6,127 | 3,567 | 1,291.5 | - |
| MathSAT | Parallel | 6,344 | 3,350 | 1,200.8 | 7.0 |

**Answer**: COMPASS is effective as a parallel portfolio component, reducing total time by **2.5%-27.8%** in five of six solver-dataset pairs.

### View Results Script

Display all experimental results using `scripts/show_results.py`:

```bash
# Show all RQ results (default: using paper data)
python scripts/show_results.py

# Show specific RQ (1, 2, or 3)
python scripts/show_results.py --rq 1

# Compute from actual project data files instead of paper data
python scripts/show_results.py --compute

# Save plots to PDF files (requires matplotlib)
python scripts/show_results.py --save-plots

# Combine options
python scripts/show_results.py --compute --save-plots
```

#### Command-line Options

| Option | Description |
|--------|-------------|
| `--rq N` | Show results for specific RQ (1, 2, or 3). Default: show all |
| `--compute` | Compute statistics from actual project data files instead of using pre-computed paper data. Useful for verification or when re-running experiments. |
| `--save-plots` | Generate and save visualization plots to PDF files (`RQ1_effectiveness.pdf`, `RQ2_component_ablation.pdf`, `RQ3_parallel_portfolio.pdf`). Requires `matplotlib` and `numpy`. |

### Data Sources

The script can use two data sources:

| Mode | Source | Description |
|------|--------|-------------|
| **Default** | `paper/eval.tex` | Pre-computed results from the paper (Tables 1-5). Always available and matches published results. |
| **`--compute`** | Project data files | Raw experimental data files in the repository. Computes statistics on-the-fly. |

#### Data Files by RQ

| RQ | Paper Source | Project Data Files |
|----|--------------|-------------------|
| **RQ1** | Tables 1-2 | `test_rl/smtimer_experiments/*_smtimer_results.json` (baseline solver results)<br>`test_rl/qf_nia_experiments/*_QF_NIA.json` (QF_NIA results) |
| **RQ2** | Tables 3-4 | `archived/analysis_outputs/New_RQ2_Component_Analysis/time_dict_*.txt` (ablation timing data) |
| **RQ3** | Table 5 | `archived/analysis_outputs/New_RQ3_Routing_Analysis/simulate_parallel_*.py` (parallel portfolio simulation) |

> **Note**: Project data files may be incomplete or located in `archived/` directories. The script falls back to paper data when files are unavailable.

## Datasets

### Benchmarks Used

| Dataset | Description | Size |
|---------|-------------|------|
| **SMTimer** | Real-world SMT constraints from program analysis (Coreutils, BusyBox, angr, KLEE) | ~1,900 instances (hard sat subset varies by solver) |
| **SMT-COMP QF_NIA** | Quantifier-Free Non-Linear Integer Arithmetic | ~3,200 instances (hard sat subset varies by solver) |

### Data Location

- **Baseline caches**: `test_rl/test_solve/`
- **Predictor training data**: `test_rl/test_overfit/`
- **Experiment results**: `test_rl/info_dict_*.txt`

## Code Structure

### Core Modules

| Module | Location | Description |
|--------|----------|-------------|
| Variable Normalization | `test_rl/test_script/utils.py` | `normalize_smt_str()` function |
| RL Environment | `test_rl/env_gai_6_llm_add_ce_predictor_docker.py` | COMPASS RL environment |
| Binary Predictor | `test_rl/bert_predictor_mask.py` | SAT/UNSAT prediction |
| Time Predictor | `test_rl/bert_predictor_2_mask.py` | 8-way time classification |
| Embedding | `test_rl/embedding.py` | CodeBERT-based embedding |

### Key Scripts

#### SMTimer Experiments (`test_rl/smtimer_experiments/`)

| Directory | Solver | Script | Purpose |
|-----------|--------|--------|---------|
| `z3_process/` | Z3 | `run_predictor.py` | SMTimer with Z3 |
| `cvc5_process/` | CVC5 | `run_predictor.py` | SMTimer with CVC5 |
| `mathsat5_process/` | MathSAT5 | `run_predictor.py` | SMTimer with MathSAT5 |
| `bvparti_process/` | BVParti | `run_bvparti_predictor.py` | SMTimer with BVParti |

#### QF_NIA Experiments (`test_rl/qf_nia_experiments/`)

| Directory | Solver | Script | Purpose |
|-----------|--------|--------|---------|
| `z3_process_QF_NIA/` | Z3 | `run_predictor.py` | QF_NIA with Z3 |
| `cvc5_process_QF_NIA/` | CVC5 | `run_predictor.py` | QF_NIA with CVC5 |
| `mathsat5_process_QF_NIA/` | MathSAT5 | `run_predictor.py` | QF_NIA with MathSAT5 |
| `ariparti_process_QF_NIA/` | AriParti | `run_predictor.py` | QF_NIA with AriParti |

#### Overfitting Tests (`test_rl/test_overfit/`)

| Script | Purpose |
|--------|---------|
| `train_smtimer_llm_predictors.py` | Standalone overfitting tests / sanity checks for predictors |

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to new functions
- Update documentation for API changes

## Citation

If you use COMPASS in your research, please cite:

```bibtex
@article{compass2024,
  title={COMPASS: Constraint Simplification via Dual-Agent AI},
  author={...},
  journal={...},
  year={2024}
}
```

## Documentation

- **REPRODUCTION.md**: Detailed reproduction instructions for experiments
- **SOLVER_INSTALLATION.md**: Solver installation guide (BVParti, AriParti)
- **test_rl/external_references/README.md**: External dependency documentation
- **pearl/README.md**: Pearl RL framework documentation
- **paper/**: Full paper source with methodology details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pearl](https://github.com/facebookresearch/Pearl) - RL framework by Meta
- [Z3](https://github.com/Z3Prover/z3) - SMT solver by Microsoft
- [CVC5](https://cvc5.github.io/) - SMT solver
- [MathSAT5](https://mathsat.fbk.eu/) - SMT solver
- [BVParti](https://github.com/sigpl-org/STP-Parti-Bitwuzla-at-SMT-COMP-2025) - Bit-vector partition-based solver
- [AriParti](https://github.com/ariparti/AriParti) - Arithmetic partition-based solver
- [CodeBERT](https://github.com/microsoft/CodeBERT) - Code embedding model

## Contact

For questions and issues, please open a GitHub issue.
