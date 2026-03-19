#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
from typing import List


def run(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--var-count", default="New_RQ2_Component_Analysis/var_count.txt")
    ap.add_argument("--baseline-z3", default="New_RQ2_Component_Analysis/info_dict_bingxing.txt")
    ap.add_argument("--out-root", default="New_RQ2_Component_Analysis/20260309_202958")
    ap.add_argument("--min-vars", nargs="+", type=int, default=[5, 0])
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    out_root = (repo_root / args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    recompute_py = (repo_root / "New_RQ2_Component_Analysis/20260309_202958/recompute_rq2_tables_20260309.py").resolve()
    fig4_py = (repo_root / "New_RQ2_Component_Analysis/generate_llm_comparison_plot.py").resolve()
    fig5_py = (repo_root / "New_RQ2_Component_Analysis/generate_rq3_performance_plot.py").resolve()

    for mv in args.min_vars:
        sub = "filtered" if mv > 0 else "unfiltered"
        out_dir = out_root / sub
        out_dir.mkdir(parents=True, exist_ok=True)

        out_md = out_dir / ("RQ2_recomputed_filtered_minvars5.md" if mv > 0 else "RQ2_recomputed_unfiltered_minvars0.md")
        out_fig4 = out_dir / ("fig4_llm_effectiveness_filtered.pdf" if mv > 0 else "fig4_llm_effectiveness_unfiltered.pdf")
        out_fig5 = out_dir / ("fig5_rq3_performance_filtered.pdf" if mv > 0 else "fig5_rq3_performance_unfiltered.pdf")

        run(
            [
                "python3",
                str(recompute_py),
                "--cap",
                str(args.cap),
                "--min-vars",
                str(mv),
                "--var-count",
                str(args.var_count),
                "--baseline-z3",
                str(args.baseline_z3),
                "--out",
                str(out_md),
            ]
        )

        run(
            [
                "python3",
                str(fig4_py),
                "--cap",
                str(args.cap),
                "--min-vars",
                str(mv),
                "--var-count",
                str(args.var_count),
                "--baseline-z3",
                str(args.baseline_z3),
                "--out",
                str(out_fig4),
            ]
        )

        run(
            [
                "python3",
                str(fig5_py),
                "--cap",
                str(args.cap),
                "--min-vars",
                str(mv),
                "--var-count",
                str(args.var_count),
                "--baseline-z3",
                str(args.baseline_z3),
                "--out",
                str(out_fig5),
            ]
        )


if __name__ == "__main__":
    main()
