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
├── test_rl/
│   ├── test_script/                 # Core utilities (variable normalization, etc.)
│   ├── predictor/                   # Predictor models and embeddings
│   ├── test_QF_NIA/                 # QF_NIA benchmark experiments
│   ├── test_cvc5/                   # Multi-solver experiments (CVC5, MathSAT, BVParti)
│   ├── test_overfit/                # Predictor training scripts
│   ├── test_LLM/                    # LLM variable selection experiments
│   ├── test_solve/                  # Baseline solver caches
│   ├── common/                      # Shared modules
│   ├── features/                    # Embedding vectors
│   ├── external_references/         # External dependency placeholders
│   └── archived/                    # Archived/uncertain files
├── New_RQ1_Effectiveness_Analysis/  # RQ1: Effectiveness analysis
├── New_RQ2_Component_Analysis/      # RQ2: Component ablation
├── New_RQ3_Routing_Analysis/        # RQ3: Selective routing
├── paper/                           # Paper source code (LaTeX)
├── config.py                        # Centralized path configuration
├── PATH_MIGRATION_GUIDE.md          # Path migration documentation
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

See `PATH_MIGRATION_GUIDE.md` for detailed path migration instructions.

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

For external solvers (BVParti, AriParti), see `SOLVER_INSTALLATION.md` for detailed installation instructions.

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

### RQ1: Effectiveness

| Benchmark | Baseline (Z3) | COMPASS | Improvement |
|-----------|---------------|---------|-------------|
| SMTimer | 72 solved | 94 solved | +30.6% |
| QF_NIA (SMT-COMP) | - | - | +12.3% |
| QF_LIA (SMT-COMP) | - | - | +4.6% |

### RQ2: Component Analysis

- **RL + LLM**: Full COMPASS performance
- **LLM only**: 15% reduction in solved instances
- **Random selection**: 40% reduction in solved instances

### RQ3: Selective Simplification

- Routing threshold: 0.8% of instances
- Time reduction: 12.6%
- Accuracy: 95%+ on routing decisions

## Datasets

### Benchmarks Used

| Dataset | Description | Size |
|---------|-------------|------|
| **SMTimer** | Real-world SMT constraints from program analysis | 710 instances |
| **SMT-COMP QF_NIA** | Quantifier-Free Non-Linear Integer Arithmetic | 3,000+ instances |
| **SMT-COMP QF_LIA** | Quantifier-Free Linear Integer Arithmetic | 5,000+ instances |
| **SMT-COMP QF_BV** | Quantifier-Free Bit-Vector theory | 4,000+ instances |

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

#### SMTimer Experiments (`test_rl/test_cvc5/`)

| Directory | Solver | Script | Purpose |
|-----------|--------|--------|---------|
| `z3_process/` | Z3 | `run_predictor.py` | SMTimer with Z3 (initial experiment) |
| `cvc5_process/` | CVC5 | `run_predictor.py` | SMTimer with CVC5 |
| `mathsat5_process/` | MathSAT5 | `run_predictor.py` | SMTimer with MathSAT5 |
| `bvparti_process/` | BVParti | `run_bvparti_predictor.py` | SMTimer with BVParti |

#### QF_NIA Experiments (`test_rl/test_QF_NIA/`)

| Directory | Solver | Script | Purpose |
|-----------|--------|--------|---------|
| `z3_process_QF_NIA/` | Z3 | `run_predictor.py` | QF_NIA with Z3 (initial experiment) |
| `cvc5_process_QF_NIA/` | CVC5 | `run_predictor.py` | QF_NIA with CVC5 |
| `mathsat5_process_QF_NIA/` | MathSAT5 | `run_predictor.py` | QF_NIA with MathSAT5 |
| `ariparti_process_QF_NIA/` | AriParti | `run_predictor.py` | QF_NIA with AriParti |

#### Predictor Training (`test_rl/test_overfit/`)

| Script | Purpose |
|--------|---------|
| `train_smtimer_llm_predictors.py` | Train predictors for SMTimer |

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

- **PATH_MIGRATION_GUIDE.md**: Detailed guide for path configuration
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
