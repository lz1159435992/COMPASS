"""
COMPASS Configuration File

This module provides centralized path configuration for the COMPASS project.
All hardcoded paths should be replaced with references to this configuration.

Usage:
    from config import REPO_ROOT, TEST_RL_ROOT, get_baseline_path, get_external_file
    
    # Get baseline file path
    nia_path = get_baseline_path('NIA')
    
    # Get external reference file
    rl_dict_path = get_external_file('info_dict_rl')
"""

import os

# =============================================================================
# Repository Root Directories
# =============================================================================

# Get the repository root directory (parent of test_rl)
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_RL_ROOT = os.path.join(REPO_ROOT, 'test_rl')

# =============================================================================
# External References Directory
# =============================================================================

EXTERNAL_REF_DIR = os.path.join(TEST_RL_ROOT, 'external_references')

# =============================================================================
# Data Directories
# =============================================================================

DATA_DIRS = {
    'solve': os.path.join(TEST_RL_ROOT, 'test_solve'),
    'predictor': os.path.join(TEST_RL_ROOT, 'predictor'),
    'features': os.path.join(TEST_RL_ROOT, 'features'),
    'log': os.path.join(TEST_RL_ROOT, 'log'),
    'archived': os.path.join(TEST_RL_ROOT, 'archived'),
}

# =============================================================================
# External Reference Files
# =============================================================================

EXTERNAL_FILES = {
    'info_dict_rl': os.path.join(EXTERNAL_REF_DIR, 'info_dict_rl.txt'),
    'info_dict_predictor': os.path.join(EXTERNAL_REF_DIR, 'info_dict_predictor.txt'),
    'result_dict_time': os.path.join(EXTERNAL_REF_DIR, 'result_dict_time.txt'),
}

# =============================================================================
# Baseline Files
# =============================================================================

BASELINE_FILES = {
    'NIA': os.path.join(DATA_DIRS['solve'], 'NIA', 'NIA.json'),
    'QF_NIA_test': os.path.join(DATA_DIRS['predictor'], 'smt_comp_NIA', 'QF_NIA_test.json'),
    'info_dict_smt_comp': os.path.join(DATA_DIRS['solve'], 'info_dict_smt_comp.txt'),
    'info_dict_bingxing': os.path.join(DATA_DIRS['solve'], 'info_dict_bingxing.txt'),
    'result_dict_z3solver': os.path.join(DATA_DIRS['solve'], 'result_dict_z3solver.txt'),
    'result_dict_z3solver_300s': os.path.join(DATA_DIRS['solve'], 'result_dict_z3solver_300s.txt'),
    'result_dict_RL_LLM': os.path.join(DATA_DIRS['solve'], 'result_dict_RL+LLM_108.txt'),
}

# =============================================================================
# Model Directories
# =============================================================================

MODEL_DIRS = {
    'predictor': os.path.join(TEST_RL_ROOT, 'predictor'),
    'test_overfit': os.path.join(TEST_RL_ROOT, 'test_overfit', 'models_smtimer_llm'),
    'test_QF_NIA': os.path.join(TEST_RL_ROOT, 'test_QF_NIA'),
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_baseline_path(name):
    """Get the absolute path to a baseline file.
    
    Args:
        name: Key from BASELINE_FILES dict (e.g., 'NIA', 'QF_NIA_test')
    
    Returns:
        Absolute path to the baseline file
    
    Raises:
        KeyError: If name is not in BASELINE_FILES
    """
    return BASELINE_FILES[name]

def get_external_file(name):
    """Get the absolute path to an external reference file.
    
    Args:
        name: Key from EXTERNAL_FILES dict (e.g., 'info_dict_rl')
    
    Returns:
        Absolute path to the external file
    
    Raises:
        KeyError: If name is not in EXTERNAL_FILES
    """
    return EXTERNAL_FILES[name]

def get_data_dir(name):
    """Get the absolute path to a data directory.
    
    Args:
        name: Key from DATA_DIRS dict (e.g., 'solve', 'predictor')
    
    Returns:
        Absolute path to the directory
    
    Raises:
        KeyError: If name is not in DATA_DIRS
    """
    return DATA_DIRS[name]

def get_model_dir(name):
    """Get the absolute path to a model directory.
    
    Args:
        name: Key from MODEL_DIRS dict
    
    Returns:
        Absolute path to the model directory
    
    Raises:
        KeyError: If name is not in MODEL_DIRS
    """
    return MODEL_DIRS[name]

def get_script_dir():
    """Get the directory of the calling script.
    
    This is useful for scripts that need to reference files relative to themselves.
    
    Returns:
        Directory path of the calling script
    """
    import inspect
    return os.path.dirname(os.path.abspath(inspect.stack()[1].filename))

def get_test_rl_path(*parts):
    """Get a path relative to test_rl directory.
    
    Args:
        *parts: Path components to join with TEST_RL_ROOT
    
    Returns:
        Absolute path under test_rl/
    
    Example:
        get_test_rl_path('test_solve', 'NIA', 'NIA.json')
    """
    return os.path.join(TEST_RL_ROOT, *parts)

# =============================================================================
# Validation Functions
# =============================================================================

def validate_paths():
    """Validate that all configured paths exist.
    
    Returns:
        dict: {'valid': [list of valid paths], 'missing': [list of missing paths]}
    """
    valid = []
    missing = []
    
    # Check baseline files
    for name, path in BASELINE_FILES.items():
        if os.path.exists(path):
            valid.append(f"BASELINE[{name}]: {path}")
        else:
            missing.append(f"BASELINE[{name}]: {path}")
    
    # Check data directories
    for name, path in DATA_DIRS.items():
        if os.path.exists(path):
            valid.append(f"DATA_DIR[{name}]: {path}")
        else:
            missing.append(f"DATA_DIR[{name}]: {path}")
    
    return {'valid': valid, 'missing': missing}

if __name__ == '__main__':
    # Print configuration when run directly
    print("=" * 60)
    print("COMPASS Configuration")
    print("=" * 60)
    print(f"\nRepository Root: {REPO_ROOT}")
    print(f"Test RL Root: {TEST_RL_ROOT}")
    print(f"\nExternal Reference Dir: {EXTERNAL_REF_DIR}")
    
    print("\n" + "-" * 60)
    print("Path Validation:")
    print("-" * 60)
    
    results = validate_paths()
    
    if results['valid']:
        print("\nValid paths:")
        for p in results['valid']:
            print(f"  ✓ {p}")
    
    if results['missing']:
        print("\nMissing paths (need to be created/provided):")
        for p in results['missing']:
            print(f"  ✗ {p}")
