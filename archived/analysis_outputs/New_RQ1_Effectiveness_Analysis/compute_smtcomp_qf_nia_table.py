#!/usr/bin/env python3
import argparse
import ast
from pathlib import Path

TIMEOUT = 1200.0


def compute(info_dict_path: str, compass_time_idx: int, flag_idx: int = 7):
    info = ast.literal_eval(Path(info_dict_path).read_text())

    n = len(info)
    base_sat = 0
    compass_sat = 0
    base_time_sum = 0.0
    compass_time_sum = 0.0

    changed_base_to_unknown = 0
    changed_compass_to_failed = 0

    for _, v in info.items():
        base_st = v[0]
        base_t = float(v[1])
        compass_t = float(v[compass_time_idx])
        compass_flag = v[flag_idx]

        if base_t > TIMEOUT:
            base_t = TIMEOUT
            if base_st != 'unknown':
                base_st = 'unknown'
                changed_base_to_unknown += 1

        if compass_t > TIMEOUT:
            compass_t = TIMEOUT
            if compass_flag != 'failed':
                compass_flag = 'failed'
                changed_compass_to_failed += 1

        if base_st == 'sat':
            base_sat += 1
        if compass_flag in {'succeed', 'success'}:
            compass_sat += 1

        base_time_sum += base_t
        compass_time_sum += compass_t

    base_rate = 100.0 * base_sat / n if n else float('nan')
    compass_rate = 100.0 * compass_sat / n if n else float('nan')

    base_avg = base_time_sum / n if n else float('nan')
    compass_avg = compass_time_sum / n if n else float('nan')

    return {
        'Total': n,
        'Solved_Baseline_sat': base_sat,
        'Solved_Compass_sat': compass_sat,
        'SuccessRate_Baseline_pct': base_rate,
        'SuccessRate_Compass_pct': compass_rate,
        'AvgTime_Baseline_s': base_avg,
        'AvgTime_Compass_s': compass_avg,
        'ChangedBaseToUnknown_dueToCap': changed_base_to_unknown,
        'ChangedCompassToFailed_dueToCap': changed_compass_to_failed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--info', required=True, help='Path to info_dict_*.txt (python dict literal)')
    ap.add_argument('--compass-time-idx', type=int, required=True, help='0-based index for +COMPASS time in the per-key list')
    ap.add_argument('--flag-idx', type=int, default=7, help='0-based index for succeed/failed flag in the per-key list (default: 7)')
    args = ap.parse_args()

    stats = compute(args.info, args.compass_time_idx, args.flag_idx)

    # Print a concise, table-ready line
    print('Total', stats['Total'])
    print('Solved (Baseline sat)', stats['Solved_Baseline_sat'])
    print('Solved (+COMPASS sat)', stats['Solved_Compass_sat'])
    print('Success Rate % (Baseline)', round(stats['SuccessRate_Baseline_pct'], 1))
    print('Success Rate % (+COMPASS)', round(stats['SuccessRate_Compass_pct'], 1))
    print('Avg. Time (s) (Baseline)', round(stats['AvgTime_Baseline_s'], 1))
    print('Avg. Time (s) (+COMPASS)', round(stats['AvgTime_Compass_s'], 1))
    print('Cap adjustments: base->unknown', stats['ChangedBaseToUnknown_dueToCap'], 'compass->failed', stats['ChangedCompassToFailed_dueToCap'])


if __name__ == '__main__':
    main()
