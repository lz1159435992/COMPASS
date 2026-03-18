# External Solvers Installation Guide

This document describes how to install and configure external SMT solvers used by COMPASS.

## BVParti Solver (for QF_BV theory)

BVParti is a partition-based solver for bit-vector constraints, combining STP, Parti, and Bitwuzla.

### Installation

#### Option 1: Use Pre-built Binaries

1. Download the SMT-COMP 2025 build:
   ```bash
   git clone https://github.com/sigpl-org/STP-Parti-Bitwuzla-at-SMT-COMP-2025.git
   cd STP-Parti-Bitwuzla-at-SMT-COMP-2025
   # Follow build instructions in the repository
   ```

2. Set environment variable:
   ```bash
   export BVPARTI_HOME=/path/to/STP-Parti-Bitwuzla-at-SMT-COMP-2025
   ```

3. Update `config.py`:
   ```python
   BVPARTI_HOME = os.environ.get('BVPARTI_HOME', '/path/to/default')
   ```

#### Option 2: Build from Source

Refer to the official repository for build instructions:
- STP: https://github.com/stp/stp
- Bitwuzla: https://github.com/bitwuzla/bitwuzla
- Parti: Contact authors for access

### Required Files

After installation, ensure these files exist:
- `$BVPARTI_HOME/solver/BVPartition-bin`
- `$BVPARTI_HOME/solver/partitioner-bin`
- `$BVPARTI_HOME/solver/bitwuzla-0.8.0-bin`
- `$BVPARTI_HOME/solver/run_BVParti.py`

---

## AriParti Solver (for QF_NIA theory)

AriParti is a partition-based solver for non-linear integer arithmetic.

### Installation

#### Option 1: Use Pre-built Version

1. Clone AriParti repository:
   ```bash
   git clone https://github.com/ariparti/AriParti.git
   cd AriParti
   ```

2. Set environment variable:
   ```bash
   export ARIPARTI_HOME=/path/to/AriParti
   ```

3. Build partitioner:
   ```bash
   cd $ARIPARTI_HOME
   mkdir -p bin
   # Build partitioner (refer to AriParti documentation)
   ```

#### Option 2: Use Docker

```bash
docker pull ariparti/ariparti:latest
# Mount the solver directory for use
```

### Required Files

- `$ARIPARTI_HOME/src/AriParti.py`
- `$ARIPARTI_HOME/bin/partitioner`
- Base solver (Z3 or CVC5)

### Configuration

Edit `test_rl/test_QF_NIA/ariparti_process_QF_NIA/config.json`:

```json
{
  "ariparti": {
    "home": "/path/to/AriParti",
    "partitioner_path": "bin/partitioner",
    "solver_path": "/path/to/z3",
    "max_running_tasks": 8
  }
}
```

---

## Standard SMT Solvers

### Z3 (Microsoft)

```bash
pip install z3-solver
```

Or install standalone binary:
```bash
wget https://github.com/Z3Prover/z3/releases/download/z3-4.12.4/z3-4.12.4-x64-glibc-2.35.zip
unzip z3-4.12.4-x64-glibc-2.35.zip
export PATH=$PATH:/path/to/z3/bin
```

### CVC5

```bash
# Ubuntu/Debian
sudo apt-get install cvc5

# Or download from https://cvc5.github.io/
```

### MathSAT5

```bash
# Download from https://mathsat.fbk.eu/
# Extract and add to PATH
export PATH=$PATH:/path/to/mathsat5/bin
```

---

## Verification

After installation, verify solvers are accessible:

```bash
# Test Z3
z3 --version

# Test CVC5
cvc5 --version

# Test BVParti (if installed)
python $BVPARTI_HOME/solver/run_BVParti.py --help

# Test AriParti (if installed)
python $ARIPARTI_HOME/src/AriParti.py --help
```

---

## Configuration in COMPASS

Update `config.py` to use environment variables:

```python
import os

# BVParti configuration
BVPARTI_HOME = os.environ.get('BVPARTI_HOME', '/path/to/default/bvparti')

# AriParti configuration  
ARIPARTI_HOME = os.environ.get('ARIPARTI_HOME', '/path/to/default/ariparti')

# Solver paths
SOLVER_PATHS = {
    'bvparti': {
        'base': BVPARTI_HOME,
        'bvparti_bin': os.path.join(BVPARTI_HOME, 'solver/BVPartition-bin'),
        'partitioner_bin': os.path.join(BVPARTI_HOME, 'solver/partitioner-bin'),
        'bitwuzla_bin': os.path.join(BVPARTI_HOME, 'solver/bitwuzla-0.8.0-bin'),
    },
    'ariparti': {
        'base': ARIPARTI_HOME,
        'entry': os.path.join(ARIPARTI_HOME, 'src/AriParti.py'),
        'partitioner': os.path.join(ARIPARTI_HOME, 'bin/partitioner'),
    }
}
```

---

## Troubleshooting

### BVParti not found

1. Check `$BVPARTI_HOME` environment variable
2. Verify all binary files are executable
3. Check Python path includes `run_BVParti.py`

### AriParti not found

1. Check `$ARIPARTI_HOME` environment variable
2. Verify `AriParti.py` exists in `src/` directory
3. Check partitioner binary is built

### Solver timeout

- Increase timeout in config.json
- Check system resources (CPU, memory)
- Verify solver is not blocked by other processes
