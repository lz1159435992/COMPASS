# External References Directory

This directory contains placeholder files for external dependencies referenced by the COMPASS codebase.

## Required External Files

The following files are referenced by the scripts but are located outside the COMPASS repository:

### 1. `info_dict_rl.txt`

**Original Path**: `/home/lz/sibyl_3/src/networks/info_dict_rl.txt`

**Purpose**: Contains RL training data mapping for SMT constraints.

**Referenced by**:
- `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py`
- `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_llm_only_v2.py`
- `test_rl/test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl_random_1223.py`

**How to Generate**:
This file should be generated from your own RL training process. It maps SMT file paths to RL-related features.

### 2. `info_dict_predictor.txt`

**Original Path**: `/home/lz/sibyl_3/src/networks/info_dict_predictor.txt`

**Purpose**: Contains predictor-related data mapping.

### 3. `result_dict_time.txt`

**Original Path**: `/home/lz/sibyl_3/src/networks/result_dict_time.txt`

**Purpose**: Contains timing results for solver experiments.

## Configuration

To use your own data files, you have two options:

### Option 1: Create files in this directory
Create the required files in this `external_references/` directory with the expected format.

### Option 2: Modify the scripts
Update the hardcoded paths in the scripts to point to your actual data files.

See `PATH_MIGRATION_GUIDE.md` in the repository root for detailed instructions.
