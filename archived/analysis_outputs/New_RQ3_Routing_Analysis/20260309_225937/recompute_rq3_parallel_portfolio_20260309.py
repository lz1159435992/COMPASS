#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


def run_capture(cmd: List[str], *, cwd: Path) -> str:
    p = subprocess.run(cmd, cwd=str(cwd), check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--out", required=True)

    ap.add_argument("--test-keys", default="test_rl/predictor/smt_comp_NIA/QF_NIA_test.json")
    ap.add_argument("--baseline", nargs="+", default=["test_rl/test_solve/NIA/NIA.json"])
    ap.add_argument(
        "--compass",
        nargs="+",
        default=["test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt"],
    )
    ap.add_argument("--keys-source", choices=("test_keys", "baseline", "compass", "union"), default="test_keys")
    ap.add_argument("--normalize-keys", action="store_true")
    ap.add_argument("--compass-time-field", choices=("total", "solve"), default="total")

    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py"

    cmd: List[str] = [
        "python3",
        str(script),
        "--test_keys",
        args.test_keys,
        "--baseline",
        *args.baseline,
        "--compass",
        *args.compass,
        "--cap",
        str(args.cap),
        "--keys_source",
        args.keys_source,
        "--compass_time_field",
        args.compass_time_field,
    ]
    if args.normalize_keys:
        cmd.append("--normalize_keys")

    out = run_capture(cmd, cwd=repo_root)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)


if __name__ == "__main__":
    main()
