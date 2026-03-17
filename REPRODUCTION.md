# COMPASS Experiment Reproduction Guide

This document provides detailed instructions for reproducing the experiments from the COMPASS paper.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Data Preparation](#data-preparation)
3. [RQ1: Effectiveness Experiments](#rq1-effectiveness-experiments)
4. [RQ2: Component Analysis](#rq2-component-analysis)
5. [RQ3: Selective Routing](#rq3-selective-routing)
6. [Expected Results](#expected-results)

---

## Environment Setup

### Hardware Requirements

- **GPU**: NVIDIA GPU with 16GB+ VRAM (recommended: RTX 3090 or A100)
- **CPU**: 16+ cores
- **RAM**: 64GB+
- **Storage**: 50GB+ for datasets and models

### Software Requirements

```bash
# Install Python 3.8+
conda create -n compass python=3.8
conda activate compass

# Install Pearl RL framework
cd pearl && pip install -e . && cd ..

# Install dependencies
pip install -r requirements.txt

# Install Z3 solver
pip install z3-solver
```

### LLM Setup

COMPASS uses Ollama for local LLM inference:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.1:70b
ollama pull deepseek-r1:70b
```

---

## Data Preparation

### Benchmark Datasets

1. **SMTimer Dataset**
   - Download from: [SMTimer repository](https://github.com/...)
   - Place in: `test_rl/test_solve/`

2. **SMT-COMP Benchmarks**
   - QF_NIA: Download from SMT-LIB
   - QF_LIA: Download from SMT-LIB
   - Place in: `test_rl/predictor/smt_comp_NIA/`

### Baseline Caches

Pre-computed baseline solver results are provided:

```
test_rl/test_solve/
├── NIA/NIA.json              # Z3 baseline for QF_NIA
├── info_dict_bingxing.txt    # Parallel experiment data
└── result_dict_z3solver_300s.txt
```

### External Dependencies

Some scripts reference external data files. Configure these in `test_rl/external_references/`:

```bash
# Create placeholder files
cd test_rl/external_references

# info_dict_rl.txt - RL training data mapping
# Replace with your actual data or generate from training
```

---

## RQ1: Effectiveness Experiments

### Experiment 1.1: SMTimer Z3

**Purpose**: Evaluate COMPASS on the SMTimer dataset with Z3 solver.

**Script**: `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py`

```bash
cd test_rl

# Run COMPASS (RL + LLM)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py

# Results will be saved to:
# info_dict_gai_6_normal_*_info_dict_rl.txt
```

**Configuration**:
- Timeout: 1200 seconds per instance
- LLM: llama3.1:70b
- Solver: Z3

### Experiment 1.2: QF_NIA SMT-COMP

**Purpose**: Evaluate on SMT-COMP QF_NIA division.

**Script**: `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py`

```bash
cd test_rl

# Run on QF_NIA benchmark
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py

# Results:
# info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt
```

### Experiment 1.3: Multi-solver Comparison

**Purpose**: Compare COMPASS across different solvers.

**Scripts**: Located in `test_rl/test_cvc5/`

```bash
cd test_rl/test_cvc5

# CVC5 solver
python cvc5_process/run_predictor.py

# MathSAT5 solver
python mathsat5_process/run_predictor.py

# BVParti solver
python bvparti_process/run_bvparti_predictor.py
```

---

## RQ2: Component Analysis

### Ablation Study Setup

Three variants are compared:

| Variant | Description | Script |
|---------|-------------|--------|
| RL + LLM | Full COMPASS | `test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py` |
| LLM only | No RL variable selection | `test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_llm_only_v2.py` |
| Random | Random variable selection | `test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_random_1223.py` |

### Running Ablation Experiments

```bash
cd test_rl

# 1. Full COMPASS (RL + LLM)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py

# 2. LLM only (no RL)
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_llm_only_v2.py

# 3. Random selection baseline
python test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_random_1223.py
```

### Predictor Training

To train predictors from scratch:

```bash
cd test_rl/test_overfit

# Build dataset
python build_smtimer_llm_dataset.py

# Train predictors
python train_smtimer_llm_predictors.py

# Cross-evaluate
python cross_eval_predictors_llm.py
```

---

## RQ3: Selective Routing

### Routing Analysis

**Purpose**: Evaluate selective simplification routing.

**Scripts**: Located in `New_RQ3_Routing_Analysis/`

```bash
cd New_RQ3_Routing_Analysis

# Simulate parallel portfolio
python simulate_parallel_portfolio_qf_nia.py

# Analyze routing results
python analyze_qf_nia_results.py
```

### Parallel Portfolio Simulation

```bash
cd test_rl/test_cvc5/predict_z3_process

# Run parallel portfolio simulation
python simulate_parallel_portfolio_qf_nia.py
```

---

## Expected Results

### RQ1 Results

| Benchmark | Baseline | COMPASS | Improvement |
|-----------|----------|---------|-------------|
| SMTimer (Z3) | ~72 solved | ~94 solved | +30% |
| QF_NIA | Baseline | +12% more solved | +12% |
| QF_LIA | Baseline | +5% more solved | +5% |

### RQ2 Results

| Component | Solved Instances | Relative Performance |
|-----------|------------------|---------------------|
| RL + LLM | 100% (baseline) | Full COMPASS |
| LLM only | ~85% | -15% from full |
| Random | ~60% | -40% from full |

### RQ3 Results

- Routing accuracy: 95%+
- Time reduction: 12.6%
- Instances routed: 0.8% of total

---

## Analysis Scripts

### Generate Plots

```bash
# RQ1 plots
cd New_RQ1_Effectiveness_Analysis
python generate_rq1_plot.py
python generate_all_supervenn.py

# RQ2 plots
cd New_RQ2_Component_Analysis
python generate_llm_comparison_plot.py
python generate_rq3_performance_plot.py

# RQ3 plots
cd New_RQ3_Routing_Analysis
python simulate_parallel_execution.py
```

---

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size in predictor scripts
   - Use smaller LLM model (e.g., llama3.1:8b)

2. **Path Not Found Errors**
   - Check `config.py` for correct paths
   - Verify external dependencies in `external_references/`

3. **Z3 Timeout**
   - Increase timeout in experiment scripts
   - Check for malformed SMT constraints

4. **LLM Connection Error**
   - Verify Ollama is running: `ollama serve`
   - Check model availability: `ollama list`

### Path Configuration

If you encounter path errors, update `config.py`:

```python
from config import get_baseline_path, get_external_file

# Verify paths exist
import os
print(os.path.exists(get_baseline_path('NIA')))
```

---

## Reproducibility Notes

- All experiments use fixed random seeds for reproducibility
- Results may vary slightly due to GPU non-determinism
- LLM outputs may vary between runs; use temperature=0 for deterministic results

## Contact

For issues with reproduction, please open a GitHub issue with:
- Experiment name
- Error message
- System configuration
