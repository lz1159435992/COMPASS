import argparse
import ast
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np


def round_half_up(x: float, ndigits: int = 0) -> float:
    q = Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def within_cap_rounding(t: Any, cap: float) -> bool:
    try:
        tf = float(t)
    except Exception:
        return False
    return round_half_up(tf, 0) <= cap


def load_dict_any(path: str) -> Dict[str, Any]:
    text = Path(path).read_text(errors="ignore")
    try:
        return ast.literal_eval(text)
    except Exception:
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


def filter_universe(
    *,
    base_info: Dict[str, Any],
    var_count: Optional[Dict[str, int]],
    min_vars: int,
    cap: float,
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

        if not within_cap_rounding(base_time, cap):
            base_status = "unknown"
            base_time = cap

        if base_status not in {"sat", "unknown"}:
            continue
        if base_status == "unsat":
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


@dataclass
class MethodSpec:
    name: str
    info_path: str
    tool_time_idx: int
    tool_flag_idx: int


def solved_times_sorted(*, keys: Sequence[str], info: Dict[str, Any], spec: MethodSpec, cap: float) -> List[float]:
    out: List[float] = []
    for k in keys:
        v = info.get(k)
        if v is None:
            continue
        tool_t = v[spec.tool_time_idx] if len(v) > spec.tool_time_idx else cap
        tool_flag = str(v[spec.tool_flag_idx]).strip().lower() if len(v) > spec.tool_flag_idx else "failed"
        is_solved = tool_flag in {"succeed", "success"} and within_cap_rounding(tool_t, cap)
        if not is_solved:
            continue
        try:
            out.append(float(tool_t))
        except Exception:
            continue
    out.sort()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--min-vars", type=int, default=5)
    ap.add_argument("--var-count", required=True)
    ap.add_argument("--baseline-z3", required=True)
    ap.add_argument("--out", required=True)

    ap.add_argument(
        "--random-random",
        default="test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_all_random.txt",
    )
    ap.add_argument(
        "--llm-only",
        default="test_rl/info_dict_gai_6_normal_1210_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_llm_only.txt",
    )
    ap.add_argument(
        "--random-llm",
        default="test_rl/info_dict_gai_6_normal_1217_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random.txt",
    )
    ap.add_argument(
        "--rl-random",
        default="test_rl/info_dict_gai_6_normal_1223_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl_random_1223.txt",
    )
    ap.add_argument(
        "--rl-llm",
        default="test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt",
    )
    args = ap.parse_args()

    cap = float(args.cap)
    min_vars = int(args.min_vars)
    base_z3 = load_dict_any(args.baseline_z3)
    var_count = load_var_count(args.var_count)
    keys = filter_universe(base_info=base_z3, var_count=var_count, min_vars=min_vars, cap=cap)

    specs = [
        MethodSpec(name="Random+Random", info_path=args.random_random, tool_time_idx=3, tool_flag_idx=4),
        MethodSpec(name="LLM", info_path=args.llm_only, tool_time_idx=4, tool_flag_idx=3),
        MethodSpec(name="Random+LLM", info_path=args.random_llm, tool_time_idx=3, tool_flag_idx=4),
        MethodSpec(name="RL+Random", info_path=args.rl_random, tool_time_idx=3, tool_flag_idx=4),
        MethodSpec(name="RL+LLM", info_path=args.rl_llm, tool_time_idx=3, tool_flag_idx=4),
    ]

    infos: Dict[str, Dict[str, Any]] = {s.name: load_dict_any(s.info_path) for s in specs}
    times_by_method: Dict[str, List[float]] = {s.name: solved_times_sorted(keys=keys, info=infos[s.name], spec=s, cap=cap) for s in specs}

    font_size_base = 14
    plt.rcParams["font.size"] = font_size_base
    plt.rcParams["axes.labelsize"] = font_size_base
    plt.rcParams["figure.figsize"] = (10, 3.072)
    plt.rcParams["figure.dpi"] = 300

    styles = {
        "Random+Random": {"marker": "h", "linestyle": "--", "markersize": 4, "color": "#66c2a5"},
        "LLM": {"marker": "D", "linestyle": ":", "markersize": 4, "color": "#fc8d62"},
        "Random+LLM": {"marker": "H", "linestyle": "-.", "markersize": 4, "color": "#8da0cb"},
        "RL+Random": {"marker": "8", "linestyle": ":", "markersize": 4, "color": "#e78ac3"},
        "RL+LLM": {"marker": "v", "linestyle": "-", "markersize": 4, "color": "#a6d854"},
    }

    fig, ax = plt.subplots()
    for name in [s.name for s in specs]:
        y = times_by_method[name]
        x = range(1, len(y) + 1)
        ax.plot(list(x), y, label=f"{name} ({len(y)} solved)", **styles[name], linewidth=1.5)

    ax.set_xlabel("Number of Solved Instances")
    ax.set_ylabel("Solving Time (s)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.02, 0.98),
        borderaxespad=0.2,
        frameon=False,
        fancybox=True,
        shadow=False,
        fontsize=font_size_base,
        labelspacing=0.4,
    )
    ax.margins(x=0.01, y=0.02)
    plt.tight_layout(pad=0.3)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), bbox_inches="tight", format="pdf", pad_inches=0.02)


if __name__ == "__main__":
    main()