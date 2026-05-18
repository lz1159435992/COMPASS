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
- **State**: Constraint embedding + history (768-d CodeBERT for SMTimer, 8192-d LLM for QF_NIA)
- **Action**: Variable selection for simplification
- **Reward**: Solver time improvement + predictor confidence

## Project Structure

```
COMPASS/
├── pearl/                           # Pearl RL framework (from Meta)
├── test_rl/                         # COMPASS core code
│   ├── smtimer_experiments/         # SMTimer benchmark experiments (multi-solver)
│   ├── qf_nia_experiments/          # QF_NIA benchmark experiments
│   ├── test_overfit/                # Predictor model checkpoints
│   ├── test_LLM/                    # LLM variable selection experiments
│   ├── test_script/                 # Core utilities (variable normalization, etc.)
│   ├── test_solve/                  # Baseline solver caches
│   ├── predictor/                   # Predictor models and embeddings
│   ├── common/                      # Shared modules
│   ├── external_references/         # External dependency placeholders
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
git clone https://github.com/<ANON_USER>/COMPASS.git
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

| Solver | Type | Used For | Version / Build |
|--------|------|----------|-----------------|
| Z3 | Standard | General SMT solving | 4.12.4 |
| CVC5 | Standard | General SMT solving | 1.2.1 |
| MathSAT5 | Standard | General SMT solving | 5.6.11 |
| BVParti | External | Bit-vector constraints (QF_BV) in the SMTimer backend | SMT-COMP 2025 build (`STP-Parti-Bitwuzla-at-SMT-COMP-2025`); includes `bitwuzla-0.8.0` |
| AriParti | External | Non-linear integer arithmetic (QF_NIA) in the SMT-COMP backend | AriParti repository build (see `SOLVER_INSTALLATION.md`) |

For external solver setup details, see `SOLVER_INSTALLATION.md`.

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

Predictor training scripts are located in each solver experiment directory:

```bash
cd test_rl/smtimer_experiments/z3_process
python train_predictor.py

cd test_rl/qf_nia_experiments/z3_process_QF_NIA
python train_predictor.py
```

### Variable Normalization

```python
from test_rl.test_script.utils import normalize_smt_str

# Normalize SMT-LIB2 constraint
smtlib_str = "(declare-fun x () Int) (assert (> x 0))"
normalized, var_dict, constants = normalize_smt_str(smtlib_str)
```

## Reproduction

This section provides a minimal set of steps to reproduce the main paper experiments (RQ1–RQ3).

### Environment Setup

- Python 3.8+
- A CUDA-capable GPU is recommended for running the LLM/predictors

```bash
conda create -n compass python=3.8
conda activate compass

cd pearl && pip install -e . && cd ..
pip install -r requirements.txt
pip install z3-solver
```

### LLM Setup (Ollama)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:70b
ollama pull deepseek-r1:70b
```

### Running Experiments

```bash
cd test_rl

# RQ1 (SMTimer + Z3 backend)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py

# RQ1 (QF_NIA)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py

# RQ2 ablations
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_llm_only_v2.py
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_random_1223.py
```

## Path Migration / External Dependencies

Some scripts referenced external files in the original codebase. For open-source/reproducibility, these were migrated to local placeholders under `test_rl/external_references/`.

| Original Path (example) | Purpose | Replacement |
|---|---|---|
| `/home/<USER>/sibyl_3/src/networks/info_dict_rl.txt` | RL training data | `test_rl/external_references/info_dict_rl.txt` |
| `/home/<USER>/sibyl_3/src/networks/info_dict_predictor.txt` | Predictor data | `test_rl/external_references/info_dict_predictor.txt` |
| `/home/<USER>/sibyl_3/src/networks/result_dict_time.txt` | Timing results | `test_rl/external_references/result_dict_time.txt` |

If you encounter path errors, check `test_rl/external_references/README.md`.

## Reproducing Experimental Results

All experimental results can be reproduced using the provided scripts and data files. Pre-computed result files (JSON format) with machine-independent relative path keys are included in the repository under `test_rl/smtimer_experiments/` and `test_rl/qf_nia_experiments/`.

### Quick View

```bash
# Display all RQ results from project data files
python scripts/show_results.py --compute

# Show specific RQ (1, 2, or 3)
python scripts/show_results.py --rq 1 --compute

# Save plots to PDF files (requires matplotlib)
python scripts/show_results.py --compute --save-plots
```

### Reproducing RQ1 (Effectiveness)

Run the solver-specific experiment scripts:

```bash
# SMTimer experiments (one per solver)
cd test_rl/smtimer_experiments/z3_process && python run_predictor.py
cd test_rl/smtimer_experiments/cvc5_process && python run_predictor.py
cd test_rl/smtimer_experiments/mathsat5_process && python run_predictor.py
cd test_rl/smtimer_experiments/bvparti_process && python run_bvparti_predictor.py

# QF_NIA experiments (one per solver)
cd test_rl/qf_nia_experiments/z3_process_QF_NIA && python run_predictor.py
cd test_rl/qf_nia_experiments/cvc5_process_QF_NIA && python run_predictor.py
cd test_rl/qf_nia_experiments/mathsat5_process_QF_NIA && python run_predictor.py
cd test_rl/qf_nia_experiments/ariparti_process_QF_NIA && python run_predictor.py
```

Results are saved as JSON files (`*_smtimer_results.json`, `*_QF_NIA.json`) in each process directory.

### Reproducing RQ2 (Component Analysis)

Run ablation studies by modifying the environment configuration:

```bash
# RL+LLM (full COMPASS) - default
cd test_rl/smtimer_experiments/z3_process && python run_predictor.py

# For other variants (LLM only, Random+LLM, etc.), modify env parameters
# in the respective run_predictor.py or env_gai_6_*.py files.
```

### Reproducing RQ3 (Parallel Portfolio)

```bash
# Run parallel portfolio simulation
cd test_rl/smtimer_experiments/predict_z3_process
python simulate_parallel_portfolio.py
```

### View Results Script

> **Quick View**: Run `python scripts/show_results.py` to display all experimental results in formatted tables.

> **Note**: Run `python scripts/show_results.py --compute` to display all experimental results in formatted tables from the included data files.

## Complete Workflow

This section describes the end-to-end workflow for running COMPASS from scratch: collecting solver data, training predictors, and executing the RL+LLM pipeline.

### Step 1: Collect Solver Ground Truth

Before training predictors, you need baseline solver results (SAT/UNSAT labels and solving times) for your benchmark set.

```python
from z3 import *
from test_rl.test_script.utils import solve_and_measure_time

# Load an SMT2 constraint
with open('path/to/constraint.smt2', 'r') as f:
    smtlib_str = f.read()

# Parse and solve
assertions = parse_smt2_string(smtlib_str)
solver = Solver()
for a in assertions:
    solver.add(a)

result, model, time_taken = solve_and_measure_time(solver, timeout=600000)
# result: sat/unsat/unknown
# time_taken: solving time in seconds
# model: variable assignment (if sat)
```

For batch processing, use the solver test scripts in `test_rl/test_solve/`. Results are saved as JSON/TXT files mapping benchmark identifiers to `[result, time, timeout, model_dict]`.

### Step 2: Extract Constraint Embeddings

COMPASS uses different embedding methods for each benchmark:

#### SMTimer — CodeBERT Embeddings (768-d)

SMTimer experiments use CodeBERT embeddings of the normalized SMT-LIB2 constraints.

```python
from test_rl.bert_embedder_test import CodeEmbedder_normalize

embedder = CodeEmbedder_normalize()

# Normalize the constraint first
from test_rl.test_script.utils import normalize_smt_str
normalized, var_dict, constants = normalize_smt_str(smtlib_str)

# Get embedding
embedding = embedder.get_max_pooling_embedding(normalized)
# embedding shape: (768,)
```

#### QF_NIA — LLM Embeddings (8192-d)

QF_NIA experiments use LLM embeddings via Ollama (`llama3.1:70b`). The embedding dimension is 8192.

```python
from ollama import Client

def process_embeding(text, llm_host='http://localhost:11434', llm_model='llama3.1:70b'):
    client = Client(host=llm_host)
    response = client.embeddings(model=llm_model, prompt=text, options={"temperature": 0})
    return torch.tensor(response['embedding'])
    # embedding shape: (8192,)

# Normalize first, then get LLM embedding
normalized, var_dict, constants = normalize_smt_str(smtlib_str)
embedding = process_embeding(normalized)
```

For batch feature extraction, the experiment scripts (`run_predictor.py`) automatically extract and cache embeddings to `features/` directories.

### Step 3: Train Predictor Models

COMPASS uses two predictors. The architecture differs by benchmark due to different embedding dimensions:

**SMTimer Predictors (CodeBERT-based, 768-d input):**

| Predictor | Model File | Training Script | Input | Output |
|-----------|-----------|-----------------|-------|--------|
| Binary (SAT/UNSAT) | `bert_predictor_mask_best.pth` | `train_predictor.py --model_type binary` | CodeBERT embedding (768-d) | 0=sat, 1=unsat |
| 8-Way Time | `bert_predictor_2_mask_best_model.pth` | `train_predictor.py --model_type eight_class` | CodeBERT embedding (768-d) | Time bin (0-7) |

**QF_NIA Predictors (LLM-based, 8192-d input):**

| Predictor | Model File | Training Script | Input | Output |
|-----------|-----------|-----------------|-------|--------|
| Binary (SAT/UNSAT) | `QF_NIA_bert_predictor_mask_best_llm.pth` | `bert_predictor_mask_llm.py` | LLM embedding (8192-d) | 0=sat, 1=unsat |
| 8-Way Time | `QF_NIA_bert_predictor_2_mask_best_model_llm.pth` | `bert_predictor_2_mask_llm.py` | LLM embedding (8192-d) | Time bin (0-7) |

> **Note**: The `_llm` suffix on QF_NIA model files indicates they are trained on LLM embeddings (8192-d from `llama3.1:70b`), not CodeBERT embeddings. The QF_NIA RL agent uses `state_dim=8192` to match these embeddings.

#### Training from Scratch

```bash
cd test_rl/smtimer_experiments/z3_process

# 1. Prepare features and labels
#    - features/: directory containing features_normal_*.npy files
#    - labels.npy: binary SAT/UNSAT labels
#    - time.npy: 8-way time classification labels

# 2. Train binary predictor
python train_predictor.py \
    --model_type binary \
    --features_dir features/ \
    --labels_path labels.npy \
    --save_path models/binary_classifier.pth

# 3. Train 8-way time predictor
python train_predictor.py \
    --model_type eight_class \
    --features_dir features/ \
    --labels_path time.npy \
    --save_path models/eight_class_model.pth
```

Each solver experiment directory (`test_rl/smtimer_experiments/*/`, `test_rl/qf_nia_experiments/*/`) contains its own `train_predictor.py` adapted to that benchmark/solver combination.

#### Pre-trained Models

Small model files (<50MB) are included in the repository. Large QF_NIA predictor models (>50MB) are excluded from git due to GitHub file size limits.

| Model Set | Location | Size | Download |
|-----------|----------|------|----------|
| SMTimer predictors | `test_rl/smtimer_experiments/*/models/` | <1MB each | Included |
| QF_NIA predictors | `test_rl/predictor/smt_comp_NIA/` | 75-103MB each | [Google Drive](https://drive.google.com/file/d/12pzzJ_qZThePu6_LOJMtK1MkJ3K5uyci/view?usp=sharing) |

To use pre-trained QF_NIA models, download and extract to `test_rl/predictor/smt_comp_NIA/`:

```bash
# After downloading QF_NIA_predictor_models.tar.gz
tar -xzf QF_NIA_predictor_models.tar.gz -C /path/to/COMPASS
```

### Step 4: Run RL + LLM Experiments

With predictors trained, execute the full COMPASS pipeline:

```bash
cd test_rl

# SMTimer + Z3 (RQ1)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py

# QF_NIA + Z3 (RQ1)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py
```

#### Environment Configuration

The main experiment scripts load predictors from `config.py` paths. Ensure your model files are in the expected locations:

**SMTimer (CodeBERT-based, 768-d input):**
```python
# Binary predictor (SAT/UNSAT)
test_rl/bert_predictor_mask_best.pth          # SimpleClassifier(768→128→1)

# Time predictor (8-way)
test_rl/bert_predictor_2_mask_best_model.pth  # EnhancedEightClassModel(768→...→8)
```

**QF_NIA (LLM-based, 8192-d input):**
```python
# Binary predictor (SAT/UNSAT)
test_rl/predictor/smt_comp_NIA/QF_NIA_bert_predictor_mask_best_llm.pth      # EnhancedClassifier(8192→...→1)

# Time predictor (8-way)
test_rl/predictor/smt_comp_NIA/QF_NIA_bert_predictor_2_mask_best_model_llm.pth  # EnhancedEightClassModelLargeInput(8192→...→8)
```

#### LLM Setup

Experiments use Ollama for local LLM inference. The default models are:

| Experiment | Default LLM |
|------------|-------------|
| SMTimer | `deepseek-r1:70b` |
| QF_NIA | `llama3.1:70b` |

Configure the LLM endpoint in the experiment script or via environment variables.

### Workflow Summary

**SMTimer Pipeline:**

```
SMT2 Benchmarks
       |
       v
[Solver Baseline] ---> labels.npy + time.npy
       |
       v
[CodeBERT Embedding (768-d)] ---> features/*.npy
       |
       v
[Train Predictors (768-d input)] ---> binary_classifier.pth + eight_class_model.pth
       |
       v
[RL + LLM Agent (state_dim=768)] ---> simplified constraints + improved solve times
```

**QF_NIA Pipeline:**

```
SMT2 Benchmarks
       |
       v
[Solver Baseline] ---> labels.npy + time.npy
       |
       v
[LLM Embedding via Ollama (8192-d)] ---> features/*.npy
       |
       v
[Train Predictors (8192-d input)] ---> binary_classifier_llm.pth + eight_class_model_llm.pth
       |
       v
[RL + LLM Agent (state_dim=8192)] ---> simplified constraints + improved solve times
```

## Datasets

### Benchmarks Used

| Dataset | Description | Size |
|---------|-------------|------|
| **SMTimer** | Real-world SMT constraints from program analysis (Coreutils, BusyBox, angr, KLEE) | ~1,900 instances (hard sat subset varies by solver) |
| **SMT-COMP QF_NIA** | Quantifier-Free Non-Linear Integer Arithmetic | ~3,200 instances (hard sat subset varies by solver) |

### Obtaining Original SMT2 Benchmark Files

To run experiments from scratch, you need the original `.smt2` benchmark files. The repository includes pre-computed result files, but not the original benchmarks due to their large size.

#### SMTimer Dataset

SMTimer benchmarks are extracted from real-world program analysis artifacts (Coreutils, BusyBox, angr, KLEE).

- **Source**: [Google Drive](https://drive.google.com/drive/folders/1fiYNM4EymKbAjBFGwInHQXXb2y5mJ15N?usp=sharing)
- **Expected structure**: The tar.gz archives contain `single_test/<program>/<instance>` files
- **Environment variable**: Set `SMTIMER_DATA_ROOT` to the directory containing the extracted archives, or use the default (`/tmp/cloud_disk`)

#### QF_NIA Dataset (SMT-COMP)

QF_NIA benchmarks are from the SMT Competition.

- **Source**: Download from [SMT-COMP](https://smt-comp.github.io/) or use the non-incremental track
- **Expected path**: `~/Downloads/non-incremental_Hierarchy/non-incremental/QF_NIA/`
- **Environment variable**: Set `QF_NIA_DATA_ROOT` to override the default location

## Code Structure

### Core Modules

| Module | Location | Description |
|--------|----------|-------------|
| Variable Normalization | `test_rl/test_script/utils.py` | `normalize_smt_str()` function |
| RL Environment (SMTimer) | `test_rl/env_gai_6_llm_add_ce_predictor_docker.py` | COMPASS RL environment (state_dim=768) |
| RL Environment (QF_NIA) | `test_rl/env_gai_6_llm_add_ce_predictor_docker_llm_embed.py` | COMPASS RL environment (state_dim=8192) |
| Binary Predictor (SMTimer) | `test_rl/bert_predictor_mask.py` | SAT/UNSAT prediction (768-d input) |
| Time Predictor (SMTimer) | `test_rl/bert_predictor_2_mask.py` | 8-way time classification (768-d input) |
| Binary Predictor (QF_NIA) | `test_rl/predictor/smt_comp_NIA/bert_predictor_mask_llm.py` | SAT/UNSAT prediction (8192-d LLM input) |
| Time Predictor (QF_NIA) | `test_rl/predictor/smt_comp_NIA/bert_predictor_2_mask_llm.py` | 8-way time classification (8192-d LLM input) |
| CodeBERT Embedding | `test_rl/bert_embedder_test.py` | CodeBERT-based embedding (768-d, for SMTimer) |
| LLM Embedding | `test_rl/qf_nia_experiments/*/test_group_get_dis_smt_comp_bert_embeding_single.py` | Ollama LLM embedding (8192-d, for QF_NIA) |

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
| *(No standalone predictor training script — use `solver_process/train_predictor.py`)* | Predictor training is integrated into each solver process |

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

- **SOLVER_INSTALLATION.md**: Solver installation guide (BVParti, AriParti)
- **test_rl/external_references/README.md**: External dependency documentation
- **pearl/README.md**: Pearl RL framework documentation


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
