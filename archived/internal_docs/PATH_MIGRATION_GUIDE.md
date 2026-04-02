# PATH_MIGRATION_GUIDE.md

## COMPASS Path Migration Guide

This document records all path modifications made during the repository reorganization for open-source release.

---

## 1. External Dependencies

### Hardcoded External Paths

The following external paths were referenced in the original codebase:

| Original Path | Purpose | Solution |
|---------------|---------|----------|
| `/home/<USER>/sibyl_3/src/networks/info_dict_rl.txt` | RL training data | Created placeholder in `test_rl/external_references/` |
| `/home/<USER>/sibyl_3/src/networks/info_dict_predictor.txt` | Predictor data | Created placeholder in `test_rl/external_references/` |
| `/home/<USER>/sibyl_3/src/networks/result_dict_time.txt` | Timing results | Created placeholder in `test_rl/external_references/` |
| `/home/<USER>/PycharmProjects/Pearl/test_rl/...` | Old Pearl path | Changed to relative paths or current repo paths |
| `/home/nju/PycharmProjects/Pearl/test_rl` | Old NJU path | Removed `sys.path.append` calls |

---

## 2. Scripts Requiring Path Updates

### A. Main Experiment Scripts

#### `test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_info_dict_rl.py`

**Lines to modify**:
```python
# OLD:
with open('/home/<USER>/sibyl_3/src/networks/info_dict_rl.txt', 'r') as file:
    rl_dict = json.load(file)

# NEW:
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
rl_dict_path = os.path.join(script_dir, 'external_references', 'info_dict_rl.txt')
with open(rl_dict_path, 'r') as file:
    rl_dict = json.load(file)
```

**Also modify**:
```python
# OLD:
with open('/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/info_dict_bingxing.txt', 'r') as file:

# NEW:
with open(os.path.join(script_dir, 'test_solve', 'info_dict_bingxing.txt'), 'r') as file:
```

#### `test_group_gai_6_llm_add_ce_predictor_SMTimer_docker_QF_NIA.py`

**Lines to modify**:
```python
# OLD:
with open('/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/NIA/NIA.json', 'r') as file:
with open('/home/<USER>/PycharmProjects/Pearl/test_rl/predictor/smt_comp_NIA/QF_NIA_test.json', 'r') as file:

# NEW:
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'test_solve', 'NIA', 'NIA.json'), 'r') as file:
with open(os.path.join(script_dir, 'predictor', 'smt_comp_NIA', 'QF_NIA_test.json'), 'r') as file:
```

#### `test_group_gai_6_llm_add_ce_predictor_smt_comp.py`

**Lines to modify**:
```python
# OLD:
with open('/home/<USER>/PycharmProjects/Pearl/test_rl/test_solve/info_dict_smt_comp.txt', 'r') as file:

# NEW:
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'test_solve', 'info_dict_smt_comp.txt'), 'r') as file:
```

---

## 3. sys.path.append Cleanup

The following `sys.path.append` calls should be removed (imports already work correctly):

| File | Line to Remove |
|------|----------------|
| `test_script/*.py` | `sys.path.append('/home/nju/PycharmProjects/Pearl/test_rl')` |
| Various scripts | `sys.path.append('/home/<USER>/PycharmProjects/Pearl')` |

---

## 4. Relative Import Patterns (Already Correct)

The following import patterns are correct and should NOT be modified:

```python
from test_rl.bert_predictor_2_mask import EnhancedEightClassModel
from test_rl.bert_predictor_mask import SimpleClassifier
from test_rl.test_script.utils import normalize_smt_str, load_dictionary
from test_rl.test_script.online_learning_break import online_learning
from test_rl.common.cmd_args import cmd_args
from test_rl.common.constants import NUM_EDGE_TYPES
```

---

## 5. Output File Paths

Output files use relative paths and should work correctly:

```python
info_name = 'info_dict_gai_6_normal_*.txt'  # Written to current directory
```

---

## 6. Model File Paths

Model files are loaded using relative paths within the project:

```python
# Correct pattern (uses os.path.join with script_dir):
save_path = os.path.join(script_dir, 'models', 'QF_NIA_bert_predictor_mask_best.pth')
```

---

## 7. Configuration File Approach (Recommended)

For better maintainability, consider creating a configuration file:

### `config.py` (to be created)

```python
import os

# Get the repository root directory
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_RL_ROOT = os.path.join(REPO_ROOT, 'test_rl')

# External references directory
EXTERNAL_REF_DIR = os.path.join(TEST_RL_ROOT, 'external_references')

# Data directories
DATA_DIRS = {
    'solve': os.path.join(TEST_RL_ROOT, 'test_solve'),
    'predictor': os.path.join(TEST_RL_ROOT, 'predictor'),
    'features': os.path.join(TEST_RL_ROOT, 'features'),
}

# External files
EXTERNAL_FILES = {
    'info_dict_rl': os.path.join(EXTERNAL_REF_DIR, 'info_dict_rl.txt'),
    'info_dict_predictor': os.path.join(EXTERNAL_REF_DIR, 'info_dict_predictor.txt'),
}

# Baseline files
BASELINE_FILES = {
    'NIA': os.path.join(DATA_DIRS['solve'], 'NIA', 'NIA.json'),
    'QF_NIA_test': os.path.join(DATA_DIRS['predictor'], 'smt_comp_NIA', 'QF_NIA_test.json'),
}
```

---

## 8. Files Moved to Archived

The following types of files have been moved to `test_rl/archived/`:

- Old experiment results that are no longer referenced
- Duplicate or backup files
- Temporary test files

**Note**: No files have been deleted. All uncertain content is preserved in `archived/`.

---

## 9. Verification Checklist

After path migration, verify:

- [ ] All scripts can import `test_rl.*` modules correctly
- [ ] External reference placeholders are replaced with actual data
- [ ] Baseline JSON files are accessible
- [ ] Model files can be loaded
- [ ] Output files are written to correct locations

---

## 10. Contact

For questions about path migration, please open an issue on the GitHub repository.
