#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
        raise SystemExit(p.returncode)
    return p.stdout.strip()


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    recompute = root / "RQ4_Analysis_Framework" / "recompute_intersection_20260308.py"

    print("# Recomputed key rows under mouth: var>=5 + cap (ROUND_HALF_UP to integer seconds)")
    print()

    print("## SMTimer / CVC5 (from cvc5_0628 cache)")
    out = run(
        [
            sys.executable,
            str(recompute),
            "--task",
            "smtimer_cvc5",
            "--info",
            str(
                root
                / "test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt"
            ),
            "--cap",
            "1200",
            "--min_vars",
            "5",
            "--compass_time_idx",
            "6",
            "--compass_flag_idx",
            "7",
        ]
    )
    print(out)
    print()

    print("## SMT-COMP / QF_NIA / Z3 (from Z3 QF_NIA cache)")
    out = run(
        [
            sys.executable,
            str(recompute),
            "--task",
            "qf_nia_z3",
            "--info",
            str(
                root
                / "test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt"
            ),
            "--cap",
            "1200",
        ]
    )
    print(out)


if __name__ == "__main__":
    main()
