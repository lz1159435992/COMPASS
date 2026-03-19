#!/usr/bin/env python3

import argparse
import ast
import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


CAP_DEFAULT = 1200.0

_DECL_RE = re.compile(r"\((?:declare-fun|declare-const)\s+(\|[^\|]*\||[^\s\)]+)")


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


def read_text_maybe_json_smt_script(file_path: str) -> str:
    s = Path(file_path).read_text(errors="ignore")
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return str(obj.get("script") or obj.get("smt_script") or "")
    except Exception:
        pass
    return s


def resolve_smt2_path(p: str) -> Optional[str]:
    cand = Path(p)
    if cand.exists():
        return str(cand)

    # Common path remapping across environments
    remaps = [
        ("/home/nju/Downloads/smt/", "/home/lz/baidudisk/smt/"),
        ("/home/nju/Downloads/smt/", "/home/lz/Downloads/smt/"),
        ("/home/nju/Downloads/", "/home/lz/Downloads/"),
    ]
    for a, b in remaps:
        if p.startswith(a):
            q = b + p[len(a) :]
            if Path(q).exists():
                return q

    # As a last resort, try to locate by suffix under known roots.
    # We keep it cheap: only try the relative tail after '/smt/' if present.
    marker = "/smt/"
    if marker in p:
        tail = p.split(marker, 1)[1]
        for root in ("/home/lz/baidudisk/smt/", "/home/lz/Downloads/smt/"):
            q = str(Path(root) / tail)
            if Path(q).exists():
                return q
    return None


def count_vars_by_declare_fun(file_path: str) -> int:
    p = resolve_smt2_path(file_path)
    try:
        text = Path(p).read_text(errors="ignore")
    except FileNotFoundError:
        return -1

    names = {m.group(1).strip("|") for m in _DECL_RE.finditer(text)}
    return len(names)


@dataclass
class SolverMouth:
    name: str
    dataset: str
    info_path: str
    parser: str  # 'ast' or 'json'
    base_status_idx: int
    base_time_idx: int
    tool_time_idx: int
    tool_flag_idx: int
    apply_min_vars_filter: bool


@dataclass
class SolverRow:
    solver: str
    total: int
    solved_base: int
    solved_tool: int
    rate_base_pct: float
    rate_tool_pct: float
    avg_base_s: float
    avg_tool_s: float


@dataclass
class IntersectionRow:
    dataset: str
    solver: str
    both: int
    only_tool: int
    only_base: int
    base_total: int
    retention_pct: float


def load_dict(path: str, parser: str) -> Dict[str, Any]:
    text = Path(path).read_text(errors="ignore")
    if parser == "json":
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict JSON in {path}")
        return obj
    return ast.literal_eval(text)


def compute_smtimer_row(
    mouth: SolverMouth,
    *,
    cap: float,
    min_vars: int,
    var_cache: Dict[str, int],
) -> Tuple[SolverRow, Set[str], Set[str], Dict[str, Any]]:
    info = load_dict(mouth.info_path, mouth.parser)

    total = 0
    solved_base = 0
    solved_tool = 0
    sum_base = 0.0
    sum_tool = 0.0

    base_solved_set: Set[str] = set()
    tool_solved_set: Set[str] = set()

    filtered_lt_min_vars = 0
    missing_smt2_for_var_count = 0

    for k, v in info.items():
        if mouth.apply_min_vars_filter:
            n_vars = var_cache.get(k)
            if n_vars is None:
                n_vars = count_vars_by_declare_fun(k)
                var_cache[k] = n_vars
            if n_vars < 0:
                # Cannot locate SMT2 on this machine; keep the instance to avoid silently changing
                # the universe size. We record it and disclose in the output.
                missing_smt2_for_var_count += 1
            elif n_vars < min_vars:
                filtered_lt_min_vars += 1
                continue

        total += 1

        base_st = str(v[mouth.base_status_idx]).strip().lower() if len(v) > mouth.base_status_idx else "unknown"
        base_t = v[mouth.base_time_idx] if len(v) > mouth.base_time_idx else cap
        base_t_avg = capped_time_for_avg(base_t, cap)
        sum_base += base_t_avg

        tool_t = v[mouth.tool_time_idx] if len(v) > mouth.tool_time_idx else cap
        tool_flag = str(v[mouth.tool_flag_idx]).strip().lower() if len(v) > mouth.tool_flag_idx else "failed"
        tool_t_avg = capped_time_for_avg(tool_t, cap)
        sum_tool += tool_t_avg

        if base_st in {"sat", "unsat"} and within_cap_rounding(base_t, cap):
            solved_base += 1
            base_solved_set.add(k)

        if tool_flag in {"succeed", "success"} and within_cap_rounding(tool_t, cap):
            solved_tool += 1
            tool_solved_set.add(k)

    row = SolverRow(
        solver=mouth.name,
        total=total,
        solved_base=solved_base,
        solved_tool=solved_tool,
        rate_base_pct=(100.0 * solved_base / total) if total else 0.0,
        rate_tool_pct=(100.0 * solved_tool / total) if total else 0.0,
        avg_base_s=(sum_base / total) if total else float("nan"),
        avg_tool_s=(sum_tool / total) if total else float("nan"),
    )

    meta = {
        "info_total": len(info),
        "filtered_lt_min_vars": filtered_lt_min_vars,
        "missing_smt2_for_var_count": missing_smt2_for_var_count,
        "kept": total,
        "cap": cap,
        "min_vars": min_vars,
        "cap_rounding": "ROUND_HALF_UP to integer seconds",
        "indices": {
            "base_status_idx": mouth.base_status_idx,
            "base_time_idx": mouth.base_time_idx,
            "tool_time_idx": mouth.tool_time_idx,
            "tool_flag_idx": mouth.tool_flag_idx,
        },
        "info_path": mouth.info_path,
    }
    return row, base_solved_set, tool_solved_set, meta


def compute_intersection_row(
    *,
    dataset: str,
    solver: str,
    base_solved: Set[str],
    tool_solved: Set[str],
    universe: Iterable[str],
) -> IntersectionRow:
    u = set(universe)
    b = base_solved & u
    c = tool_solved & u
    both = b & c
    base_total = len(b)
    return IntersectionRow(
        dataset=dataset,
        solver=solver,
        both=len(both),
        only_tool=len(c - b),
        only_base=len(b - c),
        base_total=base_total,
        retention_pct=(100.0 * len(both) / base_total) if base_total else 0.0,
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
    ap.add_argument("--min-vars", type=int, default=5)
    ap.add_argument("--out", required=True, help="Output markdown path")
    args = ap.parse_args()

    cap = float(args.cap)
    min_vars = int(args.min_vars)

    # Authoritative inputs (matched to the values currently used in paper/eval.tex)
    mouths: List[SolverMouth] = [
        # SMTimer
        SolverMouth(
            name="Z3",
            dataset="SMTimer",
            info_path="test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
            apply_min_vars_filter=True,
        ),
        SolverMouth(
            name="CVC5",
            dataset="SMTimer",
            info_path="test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=True,
        ),
        SolverMouth(
            name="BVParti",
            dataset="SMTimer",
            info_path="test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0728.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=False,
        ),
        SolverMouth(
            name="MathSAT",
            dataset="SMTimer",
            info_path="RQ4_Analysis_Framework/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=True,
        ),
        # SMT-COMP (QF_NIA)
        SolverMouth(
            name="Z3",
            dataset="SMT-COMP/QF_NIA",
            info_path="test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=3,
            tool_flag_idx=4,
            apply_min_vars_filter=False,
        ),
        SolverMouth(
            name="CVC5",
            dataset="SMT-COMP/QF_NIA",
            info_path="test_rl/test_QF_NIA/cvc5_process_QF_NIA/info_dict_SMTimer_cvc5_llama3.1_70b_QF_NIA.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=False,
        ),
        SolverMouth(
            name="MathSAT5",
            dataset="SMT-COMP/QF_NIA",
            info_path="test_rl/test_QF_NIA/mathsat5_process_QF_NIA/info_dict_SMTimer_mathsat_llama3.1_70b_QF_NIA.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=False,
        ),
        SolverMouth(
            name="AriParti",
            dataset="SMT-COMP/QF_NIA",
            info_path="test_rl/test_QF_NIA/ariparti_process_QF_NIA/info_dict_SMTimer_ariparti_llama3.1_70b_QF_NIA.txt",
            parser="ast",
            base_status_idx=0,
            base_time_idx=1,
            tool_time_idx=6,
            tool_flag_idx=7,
            apply_min_vars_filter=False,
        ),
    ]

    var_cache: Dict[str, int] = {}

    smtimer_rows: List[SolverRow] = []
    smtcomp_rows: List[SolverRow] = []
    inter_rows: List[IntersectionRow] = []

    metas: Dict[str, Dict[str, Any]] = {}

    for mouth in mouths:
        row, base_set, tool_set, meta = compute_smtimer_row(mouth, cap=cap, min_vars=min_vars, var_cache=var_cache)
        metas[f"{mouth.dataset}/{mouth.name}"] = meta

        if mouth.dataset == "SMTimer":
            smtimer_rows.append(row)
            universe = set(load_dict(mouth.info_path, mouth.parser).keys())
            # Note: intersection universe should match the *kept* universe after filtering
            # We reconstruct it by applying the same filtering: reuse base_set/tool_set union is insufficient,
            # so we re-filter by vars.
            kept_universe = []
            info = load_dict(mouth.info_path, mouth.parser)
            for k in info.keys():
                if not mouth.apply_min_vars_filter:
                    kept_universe.append(k)
                    continue

                n_vars = var_cache.get(k)
                if n_vars is None:
                    n_vars = count_vars_by_declare_fun(k)
                    var_cache[k] = n_vars
                if n_vars == -1:
                    kept_universe.append(k)
                elif n_vars >= min_vars:
                    kept_universe.append(k)
            inter_rows.append(
                compute_intersection_row(
                    dataset="SMTimer",
                    solver=mouth.name,
                    base_solved=base_set,
                    tool_solved=tool_set,
                    universe=kept_universe,
                )
            )
        else:
            smtcomp_rows.append(row)
            universe = load_dict(mouth.info_path, mouth.parser).keys()
            inter_rows.append(
                compute_intersection_row(
                    dataset="SMT-COMP",
                    solver=mouth.name,
                    base_solved=base_set,
                    tool_solved=tool_set,
                    universe=universe,
                )
            )

    smtimer_rows.sort(key=lambda r: ["Z3", "CVC5", "BVParti", "MathSAT"].index(r.solver) if r.solver in {"Z3","CVC5","BVParti","MathSAT"} else 999)
    smtcomp_rows.sort(key=lambda r: ["Z3", "CVC5", "MathSAT5", "AriParti"].index(r.solver) if r.solver in {"Z3","CVC5","MathSAT5","AriParti"} else 999)

    # Split intersection rows by dataset
    inter_smtimer = [r for r in inter_rows if r.dataset == "SMTimer"]
    inter_smtcomp = [r for r in inter_rows if r.dataset == "SMT-COMP"]

    # Format output
    out_lines: List[str] = []
    out_lines.append(f"# RQ1 Recomputed Summary (cap={cap}, min_vars={min_vars})")
    out_lines.append("")
    out_lines.append("## Mouth (unified rules)")
    out_lines.append("")
    out_lines.append("- Variable filtering on SMTimer: keep instances with `#vars >= min_vars` (counted from SMT2 `(declare-fun ...)` / `(declare-const ...)`, including quoted symbols like `|...|`).")
    out_lines.append("- Timeout cap: decide within-cap by `ROUND_HALF_UP` rounding to integer seconds first, then compare with cap.")
    out_lines.append("- Solved (baseline): status in `{sat, unsat}` AND within-cap.")
    out_lines.append("- Solved (+tool): flag in `{succeed, success}` AND within-cap.")
    out_lines.append("- Avg time: per-instance time is `t` if within-cap else `cap`; then averaged over all instances in the row.")

    out_lines.append("")
    out_lines.append("## Table A: SMTimer multi-solver performance (recomputed)")
    out_lines.append("")
    out_lines.append(
        md_table(
            ["Solver", "Total", "Solved(Base)", "Solved(+tool)", "Rate(Base)%", "Rate(+tool)%", "AvgT(Base)s", "AvgT(+tool)s"],
            [
                [
                    r.solver,
                    r.total,
                    r.solved_base,
                    r.solved_tool,
                    f"{r.rate_base_pct:.1f}",
                    f"{r.rate_tool_pct:.1f}",
                    f"{r.avg_base_s:.1f}",
                    f"{r.avg_tool_s:.1f}",
                ]
                for r in smtimer_rows
            ],
        )
    )

    out_lines.append("")
    out_lines.append("## Table B: SMT-COMP/QF_NIA multi-solver performance (recomputed)")
    out_lines.append("")
    out_lines.append(
        md_table(
            ["Solver", "Total", "Solved(Base)", "Solved(+tool)", "Rate(Base)%", "Rate(+tool)%", "AvgT(Base)s", "AvgT(+tool)s"],
            [
                [
                    r.solver,
                    r.total,
                    r.solved_base,
                    r.solved_tool,
                    f"{r.rate_base_pct:.1f}",
                    f"{r.rate_tool_pct:.1f}",
                    f"{r.avg_base_s:.1f}",
                    f"{r.avg_tool_s:.1f}",
                ]
                for r in smtcomp_rows
            ],
        )
    )

    out_lines.append("")
    out_lines.append("## Table C: Intersection analysis (recomputed)")
    out_lines.append("")

    out_lines.append("### SMTimer")
    out_lines.append("")
    out_lines.append(
        md_table(
            ["Solver", "Both", "Only +tool", "Only Base", "Base Total", "Retention%"],
            [[r.solver, r.both, r.only_tool, r.only_base, r.base_total, f"{r.retention_pct:.1f}"] for r in inter_smtimer],
        )
    )

    out_lines.append("")
    out_lines.append("### SMT-COMP/QF_NIA")
    out_lines.append("")
    out_lines.append(
        md_table(
            ["Solver", "Both", "Only +tool", "Only Base", "Base Total", "Retention%"],
            [[r.solver, r.both, r.only_tool, r.only_base, r.base_total, f"{r.retention_pct:.1f}"] for r in inter_smtcomp],
        )
    )

    out_lines.append("")
    out_lines.append("## Self-checks")
    out_lines.append("")
    out_lines.append("- Intersection identity: `Solved(+tool) == Both + Only +tool`, `Solved(Base) == Both + Only Base` (should hold per row).")

    out_lines.append("")
    out_lines.append("## Inputs (paths and indices)")
    out_lines.append("")
    for k in sorted(metas.keys()):
        m = metas[k]
        out_lines.append(
            f"- **{k}**: `{m['info_path']}`; idx={m['indices']}; kept={m['kept']} "
            f"(from total={m['info_total']}, filtered_lt_min_vars={m['filtered_lt_min_vars']}, missing_smt2_for_var_count={m['missing_smt2_for_var_count']})"
        )

    Path(args.out).write_text("\n".join(out_lines) + "\n")


if __name__ == "__main__":
    main()
