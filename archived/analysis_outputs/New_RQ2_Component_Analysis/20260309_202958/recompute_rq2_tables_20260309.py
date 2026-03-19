#!/usr/bin/env python3

import argparse
import ast
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

CAP_DEFAULT = 1200.0


def round_half_up(x: float, ndigits: int = 0) -> float:
    q = Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def within_cap_rounding(t: Any, cap: float) -> bool:
    try:
        tf = float(t)
    except Exception:
        return False
    return round_half_up(tf, 0) <= cap


def capped_time_for_avg(t: Any, cap: float) -> float:
    try:
        tf = float(t)
    except Exception:
        return cap
    return tf if within_cap_rounding(tf, cap) else cap


def load_dict_any(path: str) -> Dict[str, Any]:
    text = Path(path).read_text(errors="ignore")
    try:
        return ast.literal_eval(text)
    except Exception:
        # Some files are strict JSON; try json after ast
        import json

        return json.loads(text)


def load_var_count(path: str) -> Dict[str, int]:
    obj = load_dict_any(path)
    out: Dict[str, int] = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            out[k] = len(v)
        elif isinstance(v, list):
            out[k] = len(v)
        else:
            out[k] = 0
    return out


@dataclass
class MethodSpec:
    name: str
    info_path: str
    base_status_idx: int
    base_time_idx: int
    tool_time_idx: int
    tool_flag_idx: int


@dataclass
class RowStats:
    total: int
    solved: int
    rate_pct: float
    avg_time_all_cap_s: float
    avg_time_solved_only_s: float


def filter_universe(
    *,
    base_info: Dict[str, Any],
    var_count: Optional[Dict[str, int]],
    min_vars: int,
    cap: float,
    only_sat_unknown: bool,
    drop_unsat: bool,
) -> List[str]:
    kept: List[str] = []
    for k, v in base_info.items():
        try:
            base_status = str(v[0]).strip().lower()
        except Exception:
            base_status = "unknown"
        try:
            base_time = float(v[1])
        except Exception:
            base_time = cap

        # Apply cap normalization for filtering (mirror paper protocol)
        if not within_cap_rounding(base_time, cap):
            base_status = "unknown"
            base_time = cap

        if only_sat_unknown and base_status not in {"sat", "unknown"}:
            continue
        if drop_unsat and base_status == "unsat":
            continue

        if base_time <= 300:
            continue

        if var_count is not None and min_vars > 0:
            n = var_count.get(k)
            if n is None:
                continue
            if n <= min_vars:
                continue

        kept.append(k)
    return kept


def compute_method_stats(
    *,
    keys: Iterable[str],
    info: Dict[str, Any],
    spec: MethodSpec,
    cap: float,
) -> Tuple[RowStats, Set[str]]:
    total = 0
    solved = 0
    sum_t_all = 0.0
    sum_t_solved = 0.0
    solved_set: Set[str] = set()

    for k in keys:
        v = info.get(k)
        if v is None:
            continue

        total += 1

        base_time = v[spec.base_time_idx] if len(v) > spec.base_time_idx else cap
        tool_t = v[spec.tool_time_idx] if len(v) > spec.tool_time_idx else cap
        tool_flag = str(v[spec.tool_flag_idx]).strip().lower() if len(v) > spec.tool_flag_idx else "failed"
        tool_t_avg = capped_time_for_avg(tool_t, cap)
        sum_t_all += tool_t_avg

        is_solved = tool_flag in {"succeed", "success"} and within_cap_rounding(tool_t, cap)
        if is_solved:
            solved += 1
            solved_set.add(k)
            try:
                sum_t_solved += float(tool_t)
            except Exception:
                # If parsing fails, fall back to cap; still counts as solved
                sum_t_solved += cap

    rate = 100.0 * solved / total if total else 0.0
    avg_all = sum_t_all / total if total else float("nan")
    avg_solved = sum_t_solved / solved if solved else float("nan")
    return (
        RowStats(
            total=total,
            solved=solved,
            rate_pct=rate,
            avg_time_all_cap_s=avg_all,
            avg_time_solved_only_s=avg_solved,
        ),
        solved_set,
    )


def md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    out: List[str] = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=CAP_DEFAULT)
    ap.add_argument("--min-vars", type=int, default=5, help="Use 5 to mimic |V|>5 filtering; use 0 to disable var filtering")
    ap.add_argument("--var-count", required=True)
    ap.add_argument("--baseline-z3", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cap = float(args.cap)
    min_vars = int(args.min_vars)

    # Load baseline Z3 info_dict and var_count
    base_z3 = load_dict_any(args.baseline_z3)
    var_count = load_var_count(args.var_count)

    # Universe selection: emulate the historical RQ2 pipeline
    # - status in {sat, unknown}
    # - baseline time > 300
    # - apply |V|>min_vars only when min_vars>0
    # - drop unsat
    keys = filter_universe(
        base_info=base_z3,
        var_count=var_count,
        min_vars=min_vars,
        cap=cap,
        only_sat_unknown=True,
        drop_unsat=True,
    )

    # Method specs (indices inferred from run scripts / file formats)
    # RL+LLM (COMPASS) with different LLMs
    llm_variants: List[MethodSpec] = [
        MethodSpec(
            name="COMPASS_L3.1",
            info_path="test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
        MethodSpec(
            name="COMPASS_L3.3",
            info_path="test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_llama3.3:70b_1200s_info_dict_rl.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
        MethodSpec(
            name="COMPASS_R1",
            info_path="test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_deepseek-r1:70b_1200s_info_dict_rl.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
    ]

    # Component ablation variants (all on L3.1)
    # Note: these files have slightly different internal formats.
    ablations: List[MethodSpec] = [
        MethodSpec(
            name="Random+Random",
            info_path="test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_all_random.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
        MethodSpec(
            name="LLM",
            info_path="test_rl/info_dict_gai_6_normal_1210_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_llm_only.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=4,
            tool_flag_idx=3,
        ),
        MethodSpec(
            name="Random+LLM",
            info_path="test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
        MethodSpec(
            name="RL+Random",
            info_path="test_rl/info_dict_gai_6_normal_1223_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random_1223.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
        MethodSpec(
            name="RL+LLM",
            info_path="test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
        ),
    ]

    # Load all method info
    infos: Dict[str, Dict[str, Any]] = {"Z3": base_z3}
    for spec in llm_variants + ablations:
        infos[spec.name] = load_dict_any(spec.info_path)

    # Baseline Z3 solved set
    base_solved: Set[str] = set()
    for k in keys:
        v = base_z3.get(k)
        if not v:
            continue
        base_st = str(v[0]).strip().lower() if len(v) > 0 else "unknown"
        base_t = v[1] if len(v) > 1 else cap
        if base_st == "sat" and within_cap_rounding(base_t, cap):
            base_solved.add(k)

    # LLM ablation table + intersection
    llm_rows = []
    llm_inter_rows = []
    for spec in llm_variants:
        stats, tool_solved = compute_method_stats(keys=keys, info=infos[spec.name], spec=spec, cap=cap)
        both = len(tool_solved & base_solved)
        only_tool = len(tool_solved - base_solved)
        only_base = len(base_solved - tool_solved)
        llm_rows.append(
            [
                spec.name,
                stats.total,
                stats.solved,
                f"{stats.rate_pct:.1f}",
                f"{stats.avg_time_all_cap_s:.1f}",
                f"{stats.avg_time_solved_only_s:.1f}",
            ]
        )
        llm_inter_rows.append([spec.name, both, only_tool, only_base, len(base_solved)])

    # Component ablation table
    abl_rows = []
    for spec in ablations:
        stats, _ = compute_method_stats(keys=keys, info=infos[spec.name], spec=spec, cap=cap)
        abl_rows.append(
            [
                spec.name,
                stats.total,
                stats.solved,
                f"{stats.rate_pct:.1f}",
                f"{stats.avg_time_all_cap_s:.1f}",
                f"{stats.avg_time_solved_only_s:.1f}",
            ]
        )

    out_lines: List[str] = []
    out_lines.append(f"# RQ2 Recomputed Summary (cap={cap}, min_vars={min_vars})")
    out_lines.append("")
    out_lines.append("## Universe selection")
    out_lines.append("")
    out_lines.append(f"- Baseline: `{args.baseline_z3}`")
    out_lines.append(f"- Keep constraints where baseline status in {{sat, unknown}}, baseline_time>300, and unsat dropped")
    if min_vars > 0:
        out_lines.append(f"- Var filter: keep only constraints with |V| > {min_vars} (from `{args.var_count}`)")
    else:
        out_lines.append("- Var filter: disabled")
    out_lines.append(f"- Kept universe size: {len(keys)}")

    out_lines.append("")
    out_lines.append("## Table RQ2-A: LLM ablation (recomputed)")
    out_lines.append("")
    out_lines.append(md_table(["Variant", "Total", "Solved", "Rate%", "AvgT_all_cap(+tool)s", "AvgT_solved_only(+tool)s"], llm_rows))

    out_lines.append("")
    out_lines.append("## Table RQ2-B: LLM effectiveness breakdown vs Z3 baseline (recomputed)")
    out_lines.append("")
    out_lines.append(md_table(["Variant", "Both(Z3&tool)", "Only tool", "Only Z3", "Z3 solved total"], llm_inter_rows))

    out_lines.append("")
    out_lines.append("## Table RQ2-C: Component ablation (recomputed)")
    out_lines.append("")
    out_lines.append(md_table(["Method", "Total", "Solved", "Rate%", "AvgT_all_cap(+tool)s", "AvgT_solved_only(+tool)s"], abl_rows))

    out_lines.append("")
    out_lines.append("## Inputs (paths and indices)")
    out_lines.append("")
    out_lines.append(f"- var_count: `{args.var_count}`")
    out_lines.append(f"- baseline Z3 info_dict: `{args.baseline_z3}`")
    for spec in llm_variants + ablations:
        out_lines.append(
            f"- {spec.name}: `{spec.info_path}`; idx={{base_status:{spec.base_status_idx}, base_time:{spec.base_time_idx}, tool_time:{spec.tool_time_idx}, tool_flag:{spec.tool_flag_idx}}}"
        )

    Path(args.out).write_text("\n".join(out_lines) + "\n")


if __name__ == "__main__":
    main()
