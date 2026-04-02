#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
from typing import List


def run_capture(cmd: List[str], *, cwd: Path) -> str:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return p.stdout


def run_one(
    *,
    repo_root: Path,
    script: Path,
    name: str,
    out_dir: Path,
    cap: float,
    test_keys: str,
    baseline: List[str],
    compass: List[str],
    keys_source: str,
    normalize_keys: bool,
    compass_time_field: str,
) -> Path:
    cmd: List[str] = [
        "python3",
        str(script),
        "--test_keys",
        test_keys,
        "--baseline",
        *baseline,
        "--compass",
        *compass,
        "--cap",
        str(cap),
        "--keys_source",
        keys_source,
        "--compass_time_field",
        compass_time_field,
    ]
    if normalize_keys:
        cmd.append("--normalize_keys")

    out = run_capture(cmd, cwd=repo_root)
    out_path = out_dir / f"{name}.txt"
    out_path.write_text(out)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--compass-time-field", choices=("total", "solve"), default="total")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "New_RQ3_Routing_Analysis/simulate_parallel_portfolio_qf_nia.py"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # =============================
    # QF_NIA (SMT-COMP test set)
    # =============================
    run_one(
        repo_root=repo_root,
        script=script,
        name="QF_NIA_Z3_testkeys",
        out_dir=out_dir,
        cap=args.cap,
        test_keys="test_rl/predictor/smt_comp_NIA/QF_NIA_test.json",
        baseline=["test_rl/test_solve/NIA/NIA.json"],
        compass=["test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt"],
        keys_source="test_keys",
        normalize_keys=False,
        compass_time_field=args.compass_time_field,
    )

    # =============================
    # SMTimer (RL-only key set)
    # Per user requirement: do NOT mix predictor training/eval data into RQ3.
    # Use the RL-used, unfiltered key set for SMTimer.
    # =============================

    smtimer_rl_keys = "/home/<USER>/sibyl_3/src/networks/info_dict_rl.txt"

    # Z3: baseline is the same RL info_dict (status/time);
    # COMPASS cache is partial, missing keys fall back to baseline.
    run_one(
        repo_root=repo_root,
        script=script,
        name="SMTimer_Z3_rl_only",
        out_dir=out_dir,
        cap=args.cap,
        test_keys=smtimer_rl_keys,
        baseline=[smtimer_rl_keys],
        compass=["test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt"],
        keys_source="test_keys",
        normalize_keys=True,
        compass_time_field=args.compass_time_field,
    )

    # CVC5: baseline from RL-only results JSON (same key population as smtimer_rl_keys)
    run_one(
        repo_root=repo_root,
        script=script,
        name="SMTimer_CVC5_rl_only",
        out_dir=out_dir,
        cap=args.cap,
        test_keys=smtimer_rl_keys,
        baseline=["test_rl/test_cvc5/cvc5_smtimer_results_rl.json"],
        compass=["test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt"],
        keys_source="test_keys",
        normalize_keys=True,
        compass_time_field=args.compass_time_field,
    )

    # MathSAT: baseline from RL-only results JSON (generated on NJU machine; requires key normalization)
    run_one(
        repo_root=repo_root,
        script=script,
        name="SMTimer_MathSAT_rl_only",
        out_dir=out_dir,
        cap=args.cap,
        test_keys=smtimer_rl_keys,
        baseline=[
            "New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/smtimer_710/mathsat5_smtimer_results_rl.json"
        ],
        compass=[
            "New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/mathsat5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt"
        ],
        keys_source="test_keys",
        normalize_keys=True,
        compass_time_field=args.compass_time_field,
    )


if __name__ == "__main__":
    main()
