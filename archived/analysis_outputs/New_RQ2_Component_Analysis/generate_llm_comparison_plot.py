import argparse
import ast
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


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


def get_solved_set(*, info: Dict[str, Any], keys: Sequence[str], cap: float) -> Tuple[int, int, set]:
    total = 0
    solved = 0
    solved_set = set()
    for k in keys:
        v = info.get(k)
        if v is None:
            continue
        total += 1
        st = str(v[0]).strip().lower() if len(v) > 0 else "unknown"
        t = v[1] if len(v) > 1 else cap
        if st == "sat" and within_cap_rounding(t, cap):
            solved += 1
            solved_set.add(k)
    return total, solved, solved_set


def count_tool_outcomes(*, info: Dict[str, Any], keys: Sequence[str], tool_time_idx: int, tool_flag_idx: int, cap: float) -> Tuple[int, int]:
    solved = 0
    failed = 0
    for k in keys:
        v = info.get(k)
        if v is None:
            continue
        tool_t = v[tool_time_idx] if len(v) > tool_time_idx else cap
        tool_flag = str(v[tool_flag_idx]).strip().lower() if len(v) > tool_flag_idx else "failed"
        is_solved = tool_flag in {"succeed", "success"} and within_cap_rounding(tool_t, cap)
        if is_solved:
            solved += 1
        else:
            failed += 1
    return solved, failed


def add_labels(ax, bars, bottom_values, font_size: int, color: str = "black"):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bottom_values[i] + height / 2.0,
                f"{int(height)}",
                ha="center",
                va="center",
                color=color,
                fontsize=font_size,
                fontweight="bold",
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--min-vars", type=int, default=5)
    ap.add_argument("--var-count", required=True)
    ap.add_argument("--baseline-z3", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--l3-1",
        default="test_rl/info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt",
    )
    ap.add_argument(
        "--l3-3",
        default="test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_llama3.3:70b_1200s_info_dict_rl.txt",
    )
    ap.add_argument(
        "--r1",
        default="test_rl/info_dict_gai_6_normal_0107_pre_SMTimer_deepseek-r1:70b_1200s_info_dict_rl.txt",
    )
    args = ap.parse_args()

    cap = float(args.cap)
    min_vars = int(args.min_vars)

    base_z3 = load_dict_any(args.baseline_z3)
    var_count = load_var_count(args.var_count)
    keys = filter_universe(base_info=base_z3, var_count=var_count, min_vars=min_vars, cap=cap)

    l3_1 = load_dict_any(args.l3_1)
    l3_3 = load_dict_any(args.l3_3)
    r1 = load_dict_any(args.r1)
    variants = [
        ("COMPASS$_{L3.1}$", l3_1),
        ("COMPASS$_{L3.3}$", l3_3),
        ("COMPASS$_{R1}$", r1),
    ]

    # For fair comparison, further restrict the universe to keys that exist in ALL method info_dicts.
    # This aligns Z3 totals with method totals (e.g., unfiltered case becomes 449 instead of 1198).
    common_keys = [k for k in keys if k in l3_1 and k in l3_3 and k in r1]

    _, z3_solved, z3_solved_set = get_solved_set(info=base_z3, keys=common_keys, cap=cap)
    z3_total = len(common_keys)
    z3_failed = z3_total - z3_solved

    z3_solved_keys = list(z3_solved_set)
    z3_failed_keys = [k for k in common_keys if k not in z3_solved_set]

    solved_on_failed = []
    failed_on_failed = []
    solved_on_solved = []
    failed_on_solved = []
    for _, info in variants:
        s1, f1 = count_tool_outcomes(info=info, keys=z3_failed_keys, tool_time_idx=3, tool_flag_idx=4, cap=cap)
        s2, f2 = count_tool_outcomes(info=info, keys=z3_solved_keys, tool_time_idx=3, tool_flag_idx=4, cap=cap)
        solved_on_failed.append(s1)
        failed_on_failed.append(f1)
        solved_on_solved.append(s2)
        failed_on_solved.append(f2)

    data_on_z3_failed = {
        "Solved": np.array(solved_on_failed),
        "Failed": np.array(failed_on_failed),
    }
    data_on_z3_solved = {
        "Solved": np.array(solved_on_solved),
        "Failed": np.array(failed_on_solved),
    }

    font_size_base = 28
    colors = {"Solved": "#3988c5", "Failed": "#abd0eb"}
    hatches = ["//", "\\"]
    plt.rcParams.update({"font.size": font_size_base, "font.family": "sans-serif"})

    fig, ax = plt.subplots(figsize=(10, 5.76576))
    bar_width = 0.09504
    ind = np.array([0, 0.18, 0.18 + 0.21 * 1.2, 0.18 + 0.21 * 1.2 + 0.21 * 1.2])

    z3_succeed = ax.bar(ind[0], z3_solved, bar_width, color=colors["Solved"])
    z3_failed_bar = ax.bar(ind[0], z3_failed, bar_width, bottom=z3_solved, color=colors["Failed"])
    add_labels(ax, z3_succeed, np.array([0]), font_size=font_size_base - 2, color="white")
    add_labels(ax, z3_failed_bar, np.array([z3_solved]), font_size=font_size_base - 2, color="black")

    compass_indices = ind[1:]
    pos1 = compass_indices - bar_width / 2
    s1_s = ax.bar(
        pos1,
        data_on_z3_failed["Solved"],
        bar_width,
        color=colors["Solved"],
        hatch=hatches[0],
        edgecolor="#999999",
        linewidth=0.5,
    )
    s1_f = ax.bar(
        pos1,
        data_on_z3_failed["Failed"],
        bar_width,
        bottom=data_on_z3_failed["Solved"],
        color=colors["Failed"],
        hatch=hatches[0],
        edgecolor="#999999",
        linewidth=0.5,
    )
    add_labels(ax, s1_s, np.zeros_like(data_on_z3_failed["Solved"], dtype=float), font_size=font_size_base - 2, color="white")
    add_labels(ax, s1_f, data_on_z3_failed["Solved"].astype(float), font_size=font_size_base - 2, color="black")

    pos2 = compass_indices + bar_width / 2
    s2_s = ax.bar(
        pos2,
        data_on_z3_solved["Solved"],
        bar_width,
        color=colors["Solved"],
        hatch=hatches[1],
        edgecolor="#999999",
        linewidth=0.5,
    )
    s2_f = ax.bar(
        pos2,
        data_on_z3_solved["Failed"],
        bar_width,
        bottom=data_on_z3_solved["Solved"],
        color=colors["Failed"],
        hatch=hatches[1],
        edgecolor="#999999",
        linewidth=0.5,
    )
    add_labels(ax, s2_s, np.zeros_like(data_on_z3_solved["Solved"], dtype=float), font_size=font_size_base - 2, color="white")
    add_labels(ax, s2_f, data_on_z3_solved["Solved"].astype(float), font_size=font_size_base - 2, color="black")

    ax.set_ylabel("Number of Cases", fontsize=font_size_base)
    ax.set_xticks(ind)
    pretty_labels = ["Z3"] + [name for name, _ in variants]
    ax.set_xticklabels(pretty_labels, fontsize=font_size_base - 2)
    ax.tick_params(axis="x", pad=6)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.015)

    legend_elements = [
        Patch(facecolor=colors["Solved"], label="Outcome: Solved"),
        Patch(facecolor=colors["Failed"], label="Outcome: Failed"),
        Patch(facecolor="white", edgecolor="#999999", hatch=hatches[0], label=f"Z3's {z3_failed} Failed Cases"),
        Patch(facecolor="white", edgecolor="#999999", hatch=hatches[1], label=f"Z3's {z3_solved} Solved Cases"),
    ]
    fig.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.06),
        ncol=2,
        borderaxespad=0.15,
        fancybox=True,
        shadow=False,
        fontsize=font_size_base,
        frameon=False,
        columnspacing=0.8,
        handlelength=1.2,
        handletextpad=0.4,
        labelspacing=0.3,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("grey")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE", linestyle="-", linewidth=0.8)
    plt.tight_layout(pad=0.3, rect=[0.0, 0.0, 1.0, 0.94])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), format="pdf", bbox_inches="tight", pad_inches=0.0)


if __name__ == "__main__":
    main()
