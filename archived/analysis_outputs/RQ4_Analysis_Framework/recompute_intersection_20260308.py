#!/usr/bin/env python3

import argparse
import ast
import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set, Tuple


CAP_DEFAULT = 1200.0

_DECL_RE = re.compile(r"\(declare-fun\s+([^\s\)]+)")


def round_half_up(x: float, ndigits: int = 0) -> float:
    q = Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def within_cap_rounding(t: Any, cap: float) -> bool:
    try:
        tf = float(t)
    except Exception:
        return False
    return round_half_up(tf, 0) <= cap


def read_text_maybe_json_smt_script(file_path: str) -> str:
    s = Path(file_path).read_text(errors="ignore")
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return str(obj.get("script") or obj.get("smt_script") or "")
    except Exception:
        pass
    return s


def count_vars_by_declare_fun(file_path: str) -> int:
    smt = read_text_maybe_json_smt_script(file_path)
    names = {m.group(1).strip("|") for m in _DECL_RE.finditer(smt)}
    return len(names)


@dataclass
class IntersectionStats:
    n_universe: int
    baseline_total: int
    compass_total: int
    baseline_only: int
    compass_only: int
    both_solved: int

    @property
    def improvement(self) -> int:
        return self.compass_total - self.baseline_total

    @property
    def retention_pct(self) -> float:
        return 100.0 * self.both_solved / self.baseline_total if self.baseline_total else 0.0


def compute_intersection(baseline_solved: Set[str], compass_solved: Set[str], universe: Iterable[str]) -> IntersectionStats:
    # Restrict to universe
    u = set(universe)
    b = baseline_solved & u
    c = compass_solved & u
    both = b & c
    return IntersectionStats(
        n_universe=len(u),
        baseline_total=len(b),
        compass_total=len(c),
        baseline_only=len(b - c),
        compass_only=len(c - b),
        both_solved=len(both),
    )


def smtimer_cvc5_from_info_dict(
    *,
    info_dict_path: str,
    min_vars: int,
    cap: float,
    compass_time_idx: int,
    compass_flag_idx: int,
) -> Tuple[IntersectionStats, Dict[str, Any]]:
    info: Dict[str, Any] = ast.literal_eval(Path(info_dict_path).read_text())

    universe = []
    baseline_solved: Set[str] = set()
    compass_solved: Set[str] = set()

    filtered_lt_min_vars = 0

    for k, v in info.items():
        n_vars = count_vars_by_declare_fun(k)
        if n_vars < min_vars:
            filtered_lt_min_vars += 1
            continue

        universe.append(k)

        base_st = str(v[0]).strip().lower() if len(v) > 0 else "unknown"
        base_t = v[1] if len(v) > 1 else cap
        if base_st in {"sat", "unsat"} and within_cap_rounding(base_t, cap):
            baseline_solved.add(k)

        flag = str(v[compass_flag_idx]).strip().lower() if len(v) > compass_flag_idx else "failed"
        t_tool = v[compass_time_idx] if len(v) > compass_time_idx else cap
        if flag in {"succeed", "success"} and within_cap_rounding(t_tool, cap):
            compass_solved.add(k)

    stats = compute_intersection(baseline_solved, compass_solved, universe)
    meta = {
        "info_total": len(info),
        "filtered_lt_min_vars": filtered_lt_min_vars,
        "kept": len(universe),
        "cap": cap,
        "min_vars": min_vars,
        "cap_rounding": "ROUND_HALF_UP to integer seconds",
        "compass_time_idx": compass_time_idx,
        "compass_flag_idx": compass_flag_idx,
    }
    return stats, meta


def qf_nia_z3_from_info_dict(*, info_dict_path: str, cap: float) -> Tuple[IntersectionStats, Dict[str, Any]]:
    # Format: [baseline_status, baseline_time, baseline_timeout, total_execution_time, flag, ...]
    info = json.loads(Path(info_dict_path).read_text())

    universe = list(info.keys())
    baseline_solved: Set[str] = set()
    compass_solved: Set[str] = set()

    for k, v in info.items():
        base_st = str(v[0]).strip().lower()
        base_t = v[1]
        if base_st in {"sat", "unsat"} and within_cap_rounding(base_t, cap):
            baseline_solved.add(k)

        exec_t = v[3]
        flag = str(v[4]).strip().lower()
        if flag in {"succeed", "success"} and within_cap_rounding(exec_t, cap):
            compass_solved.add(k)

    stats = compute_intersection(baseline_solved, compass_solved, universe)
    meta = {
        "info_total": len(info),
        "cap": cap,
        "cap_rounding": "ROUND_HALF_UP to integer seconds",
    }
    return stats, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["smtimer_cvc5", "qf_nia_z3"], required=True)
    ap.add_argument("--cap", type=float, default=CAP_DEFAULT)

    ap.add_argument("--info", required=True, help="Path to info_dict (CVC5 SMTimer uses python-literal dict; QF_NIA Z3 uses JSON dict)")

    ap.add_argument("--min_vars", type=int, default=5)
    ap.add_argument("--compass_time_idx", type=int, default=6)
    ap.add_argument("--compass_flag_idx", type=int, default=7)

    args = ap.parse_args()

    if args.task == "smtimer_cvc5":
        stats, meta = smtimer_cvc5_from_info_dict(
            info_dict_path=args.info,
            min_vars=args.min_vars,
            cap=args.cap,
            compass_time_idx=args.compass_time_idx,
            compass_flag_idx=args.compass_flag_idx,
        )
    else:
        stats, meta = qf_nia_z3_from_info_dict(info_dict_path=args.info, cap=args.cap)

    print(json.dumps({"meta": meta, "stats": stats.__dict__}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
