#!/usr/bin/env python3

import argparse
import json
import os
import statistics
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


CAP_DEFAULT = 1200.0


def _is_number(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def _normalize_status(st: Any) -> str:
    if st is None:
        return "unknown"
    st = str(st).strip().lower()
    if st in {"sat", "unsat", "unknown"}:
        return st
    if st in {"timeout", "timedout", "time_out"}:
        return "unknown"
    return st


def _cap_time(t: Any, cap: float) -> float:
    if not _is_number(t):
        return float(cap)
    t = float(t)
    if t > cap:
        return float(cap)
    return t


def _percentile(sorted_vals: Sequence[float], p: float) -> Optional[float]:
    if not sorted_vals:
        return None
    if p <= 0:
        return float(sorted_vals[0])
    if p >= 100:
        return float(sorted_vals[-1])
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return float(d0 + d1)


def _summary_stats(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "p90": None,
            "p99": None,
            "min": None,
            "max": None,
        }
    vals = sorted(float(x) for x in values)
    return {
        "count": len(vals),
        "mean": float(statistics.mean(vals)) if vals else None,
        "median": float(statistics.median(vals)) if vals else None,
        "p90": _percentile(vals, 90),
        "p99": _percentile(vals, 99),
        "min": float(vals[0]),
        "max": float(vals[-1]),
    }


@dataclass
class CompassEntryParsed:
    baseline_status: str
    baseline_time: float
    baseline_timeout: float
    compass_total_time: float
    compass_solve_time: Optional[float]
    compass_final_solve_time: Optional[float]
    compass_llm_time: Optional[float]
    compass_flag: str


def parse_compass_entry(entry: Any, cap: float) -> Optional[CompassEntryParsed]:
    if not isinstance(entry, list) or len(entry) < 5:
        return None

    baseline_status = _normalize_status(entry[0])
    baseline_time = _cap_time(entry[1] if len(entry) > 1 else None, cap)
    baseline_timeout = float(entry[2]) if (len(entry) > 2 and _is_number(entry[2])) else float(cap)

    compass_total_time = _cap_time(entry[3] if len(entry) > 3 else None, cap)

    # Two formats exist in this repo:
    # 1) QF_NIA z3 cache (info_dict_gai_6_...QF_NIA.txt):
    #    [baseline_status, baseline_time, baseline_timeout, total_execution_time, flag, counterexamples...]
    # 2) SMTimer-style caches (test_QF_NIA/*/info_dict_SMTimer_*_QF_NIA.txt):
    #    [baseline_status, baseline_time, baseline_timeout, total_execution_time,
    #     total_solve_time, final_solve_time, llm_total_time, flag, ...]
    entry4 = str(entry[4]).strip().lower() if len(entry) > 4 else ""
    looks_like_flag_at_4 = entry4 in {"succeed", "failed", "cached_direct_solve"}

    if looks_like_flag_at_4:
        compass_flag = entry4
        compass_solve_time = None
        compass_final_solve_time = None
        compass_llm_time = None
    else:
        compass_solve_time = float(entry[4]) if (len(entry) > 4 and _is_number(entry[4])) else None
        compass_final_solve_time = float(entry[5]) if (len(entry) > 5 and _is_number(entry[5])) else None
        compass_llm_time = float(entry[6]) if (len(entry) > 6 and _is_number(entry[6])) else None
        compass_flag = str(entry[7]).strip().lower() if len(entry) > 7 else "failed"

    return CompassEntryParsed(
        baseline_status=baseline_status,
        baseline_time=baseline_time,
        baseline_timeout=baseline_timeout,
        compass_total_time=compass_total_time,
        compass_solve_time=compass_solve_time,
        compass_final_solve_time=compass_final_solve_time,
        compass_llm_time=compass_llm_time,
        compass_flag=compass_flag,
    )


def load_json_dict(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def solved_by_baseline(status: str) -> bool:
    return status in {"sat", "unsat"}


def solved_by_compass(flag: str) -> bool:
    return flag == "succeed"


def compute_set_stats(baseline_solved: set, compass_solved: set) -> Dict[str, Any]:
    baseline_only = baseline_solved - compass_solved
    compass_only = compass_solved - baseline_solved
    both = baseline_solved & compass_solved
    return {
        "baseline_total": len(baseline_solved),
        "compass_total": len(compass_solved),
        "baseline_only": len(baseline_only),
        "compass_only": len(compass_only),
        "both_solved": len(both),
        "total_unique": len(baseline_solved | compass_solved),
        "improvement": len(compass_solved) - len(baseline_solved),
        "relative_improvement": (
            (len(compass_solved) - len(baseline_solved)) / max(len(baseline_solved), 1)
        )
        * 100.0,
    }


def analyze_compass_vs_baseline(
    *,
    name: str,
    test_keys_path: str,
    baseline_path: Optional[str],
    compass_path: str,
    cap: float,
) -> Dict[str, Any]:
    test_dict = load_json_dict(test_keys_path)
    keys_all = list(test_dict.keys())

    baseline_dict = load_json_dict(baseline_path) if baseline_path else None
    compass_dict = load_json_dict(compass_path)

    # universe scopes
    keys_intersection = [k for k in keys_all if k in compass_dict]

    def parse_baseline_from_file(k: str) -> Tuple[str, float, float]:
        if baseline_dict is None:
            return "unknown", float(cap), float(cap)
        ent = baseline_dict.get(k)
        if not isinstance(ent, list) or len(ent) < 2:
            return "unknown", float(cap), float(cap)
        st = _normalize_status(ent[0])
        t = _cap_time(ent[1], cap)
        timeout = float(ent[2]) if (len(ent) > 2 and _is_number(ent[2])) else float(cap)
        return st, t, timeout

    def parse_compass_from_file(k: str) -> Optional[CompassEntryParsed]:
        ent = compass_dict.get(k)
        return parse_compass_entry(ent, cap)

    def run_scope(scope_name: str, keys: Iterable[str], require_compass: bool) -> Dict[str, Any]:
        baseline_solved = set()
        compass_solved = set()

        # for time statistics on succeed subset
        baseline_times_solved: List[float] = []
        compass_total_times_succeed: List[float] = []
        compass_solve_times_succeed: List[float] = []
        compass_llm_times_succeed: List[float] = []

        # conversions
        unknown_to_sat = 0
        timeout_to_sat = 0

        missing_baseline = 0
        missing_compass = 0

        for k in keys:
            b_st, b_t, _ = parse_baseline_from_file(k)
            if baseline_dict is not None and k not in baseline_dict:
                missing_baseline += 1

            ce = parse_compass_from_file(k)
            if ce is None:
                missing_compass += 1
                if require_compass:
                    continue
            else:
                # prefer compass-embedded baseline if baseline file not provided
                if baseline_dict is None:
                    b_st, b_t = ce.baseline_status, ce.baseline_time

            if solved_by_baseline(b_st):
                baseline_solved.add(k)
                baseline_times_solved.append(b_t)

            if ce is not None and solved_by_compass(ce.compass_flag):
                compass_solved.add(k)
                compass_total_times_succeed.append(ce.compass_total_time)
                if ce.compass_solve_time is not None:
                    compass_solve_times_succeed.append(float(ce.compass_solve_time))
                if ce.compass_llm_time is not None:
                    compass_llm_times_succeed.append(float(ce.compass_llm_time))

                if b_st == "unknown":
                    unknown_to_sat += 1
                if _normalize_status(b_st) == "unknown" and b_t >= cap - 1e-9:
                    timeout_to_sat += 1

        set_stats = compute_set_stats(baseline_solved, compass_solved)

        return {
            "scope": scope_name,
            "n_keys": len(list(keys)) if not isinstance(keys, list) else len(keys),
            "require_compass": require_compass,
            "missing_baseline": missing_baseline,
            "missing_compass": missing_compass,
            "set_stats": set_stats,
            "baseline_time_solved": _summary_stats(baseline_times_solved),
            "compass_total_time_succeed": _summary_stats(compass_total_times_succeed),
            "compass_solve_time_succeed": _summary_stats(compass_solve_times_succeed),
            "compass_llm_time_succeed": _summary_stats(compass_llm_times_succeed),
            "conversions": {
                "unknown_to_sat": unknown_to_sat,
                "timeout_to_sat": timeout_to_sat,
            },
        }

    result = {
        "name": name,
        "paths": {
            "test_keys": test_keys_path,
            "baseline": baseline_path,
            "compass": compass_path,
        },
        "cap": cap,
        "scopes": [
            run_scope(
                scope_name="ALL (missing COMPASS treated as 'no_compass')",
                keys=keys_all,
                require_compass=False,
            ),
            run_scope(
                scope_name="INTERSECTION (only instances with COMPASS cache)",
                keys=keys_intersection,
                require_compass=True,
            ),
        ],
    }

    return result


def _fmt_float(x: Any, digits: int = 3) -> str:
    if x is None:
        return "N/A"
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return "N/A"


def render_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# QF_NIA Analysis: {report['name']}")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- **cap**: `{report['cap']}`")
    lines.append(f"- **test keys**: `{report['paths']['test_keys']}`")
    if report['paths']['baseline']:
        lines.append(f"- **baseline**: `{report['paths']['baseline']}`")
    else:
        lines.append("- **baseline**: `None` (use baseline fields embedded in COMPASS file)")
    lines.append(f"- **COMPASS**: `{report['paths']['compass']}`")

    for scope in report["scopes"]:
        ss = scope["set_stats"]
        conv = scope["conversions"]
        lines.append("")
        lines.append(f"## Scope: {scope['scope']}")
        lines.append("")
        lines.append(f"- **n_keys**: {scope['n_keys']}")
        lines.append(f"- **missing_baseline**: {scope['missing_baseline']}")
        lines.append(f"- **missing_COMPASS**: {scope['missing_compass']}")
        lines.append("")
        lines.append("### Solved-set SuperVenn stats")
        lines.append("")
        lines.append(f"- **baseline solved**: {ss['baseline_total']}")
        lines.append(f"- **COMPASS solved**: {ss['compass_total']}")
        lines.append(f"- **baseline only**: {ss['baseline_only']}")
        lines.append(f"- **COMPASS only**: {ss['compass_only']}")
        lines.append(f"- **both solved**: {ss['both_solved']}")
        lines.append(f"- **improvement**: {ss['baseline_total']} -> {ss['compass_total']} ({ss['improvement']:+d}, {ss['relative_improvement']:.2f}%)")
        lines.append("")
        lines.append("### Conversions")
        lines.append("")
        lines.append(f"- **unknown -> sat (COMPASS succeed)**: {conv['unknown_to_sat']}")
        lines.append(f"- **timeout -> sat (COMPASS succeed, baseline time capped)**: {conv['timeout_to_sat']}")

        def add_time_block(title: str, stats: Dict[str, Any]):
            lines.append("")
            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"- **count**: {stats['count']}")
            lines.append(f"- **mean**: {_fmt_float(stats['mean'])}")
            lines.append(f"- **median**: {_fmt_float(stats['median'])}")
            lines.append(f"- **p90**: {_fmt_float(stats['p90'])}")
            lines.append(f"- **p99**: {_fmt_float(stats['p99'])}")
            lines.append(f"- **min**: {_fmt_float(stats['min'])}")
            lines.append(f"- **max**: {_fmt_float(stats['max'])}")

        add_time_block("Baseline time stats (solved only)", scope["baseline_time_solved"])
        add_time_block("COMPASS total time stats (succeed only)", scope["compass_total_time_succeed"])
        add_time_block("COMPASS solve time stats (succeed only)", scope["compass_solve_time_succeed"])
        add_time_block("COMPASS LLM time stats (succeed only)", scope["compass_llm_time_succeed"])

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--test_keys", required=True)
    parser.add_argument("--baseline", default=None)
    parser.add_argument("--compass", required=True)
    parser.add_argument("--cap", type=float, default=CAP_DEFAULT)
    parser.add_argument("--out_md", required=True)
    parser.add_argument("--out_json", default=None)

    args = parser.parse_args()

    report = analyze_compass_vs_baseline(
        name=args.name,
        test_keys_path=args.test_keys,
        baseline_path=args.baseline,
        compass_path=args.compass,
        cap=args.cap,
    )

    md = render_md(report)
    os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write(md)

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
