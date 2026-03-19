# RQ3 QF\_NIA: 6711/2540 vs 6811/2440 差异（100个实例）分析存档

## 目的

本文件用于存档并解释如下现象：

- 旧的统计（“Direct Solving”）为：`sat=6711, unsat=792, unknown=2540`
- 重新基于 baseline 缓存 `NIA.json` 统计得到：`sat=6811, unsat=792, unknown=2440`

即：**100 个 `unknown` 实际应为 `sat`（或等价地：100 个 `sat` 被旧口径误计为 `unknown`）**。

同时，本文档也再次严格验证：**任何 `time > 1200s` 的记录都必须被视为 `unknown`（并将时间 cap 到 1200）**。

---

## 数据范围与关键文件

### 数据范围

- **测试集 key**：`test_rl/predictor/smt_comp_NIA/QF_NIA_test.json`
- **key 数量**：10,043

### 关键文件

- **baseline 直接求解缓存**：`test_rl/test_solve/NIA/NIA.json`
- **旧口径/阈值流程输出（含 succeed/failed/cached_direct_solve 等状态）**：
  - `test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json`
- **COMPASS（\tool）缓存**：
  - `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`

---

## 关键结论（直接回答“为什么差 100”）

### 结论 1：`6811/2440` 才是基于 baseline 文件 `NIA.json` 的正确 direct-solving 统计

对 `QF_NIA_test.json` 的 10,043 个 key，使用 `NIA.json` 的 `[status, time]` 直接统计，并应用规则：

- 若 `time > 1200s`：将该条结果视为 `unknown`，并令时间为 1200

得到：

- `sat=6811`
- `unsat=792`
- `unknown=2440`

### 结论 2：旧的 `6711/2540` 来自 *另一个数据源*：`QF_NIA_advanced_solver_results_all_4_threshold.json`

当用 `QF_NIA_advanced_solver_results_all_4_threshold.json` 里的 `v[0]` 作为 status 做“direct”统计时，会得到：

- `sat=6711`
- `unsat=792`
- `unknown=2540`

这与 `NIA.json` 的 direct-solving 统计不同。

### 结论 3（根因）：`threshold` 文件里有 **100 条**记录的 `v[0]` 字段未正确记录 SAT

逐 key 对比发现：

- 恰好 **100** 个 key 满足：
  - `baseline(NIA.json)` 解析后为 `sat`
  - 但 `threshold_file(v[0])` 为 `unknown`

并且这 100 个 key 在 threshold 文件中的 `v[7]`（method/status 字段）分布为：

- `succeed`: 81
- `failed`: 19

即：这 100 个实例并不是“求解逻辑变化导致 unknown 变 sat”，而是 **threshold 文件自身的结果字段（v[0]）缺失/为空导致误计数**。

---

## timeout 规则严格验证（CAP=1200s）

### baseline（NIA.json）中 `time > 1200` 的条目

统计结果：

- `raw time > 1200` 的条目数：**2382**
- 它们的 status 全部已经是 `unknown`
- **不存在**任何 `sat/unsat` 且 `time > 1200` 的情况

因此：在 baseline 数据源上，“`time > 1200 => unknown`”规则已经自然满足，不会把 `sat/unsat` 错算成已解。

同时 baseline 的 `unknown=2440` 里：

- `time > 1200`: 2382
- `time <= 1200`: 58

即：unknown 不完全等价于 timeout（仍可能存在 solver 很快返回 unknown）。

### threshold 文件（QF_NIA_advanced_solver_results_all_4_threshold.json）中 `time > 1200`

统计结果：

- `time > 1200` 的条目数：**2382**（全部落在 `unknown`）
- `sat/unsat` 中 `time > 1200`：0

并且 threshold 的 `unknown=2540` 里：

- `time > 1200`: 2382
- `time <= 1200`: 158

对比 baseline 的 `unknown time<=1200`（58）可知：

- threshold 文件的 `unknown time<=1200` 比 baseline 多了 **100**
- 这 **100** 正是上文定位的“baseline=SAT，但 threshold 的 v[0] 为空/unknown”那一批

---

## COMPASS cache 的 `time>1200` 处理验证（补充）

对 `QF_NIA_test` 与 COMPASS cache 交集（2019 个 key）检查：

- 当 portfolio 使用 `--compass_time_field total`（默认）：
  - succeed 总数 467，其中 **1 个 succeed 的 total time > 1200**，将被视为 `unknown`
- 当使用 `--compass_time_field solve`：
  - succeed 的 solve time 均 `<=1200`

本项目的论文表格与仿真使用的是 `total` 口径（更符合“并行执行的 wall-clock 总耗时”定义）。

---

## 复现命令与关键输出（用于审计）

### 1) 差异定位（baseline vs threshold）与 timeout 校验

执行脚本（一次性输出：数据规模、baseline timeout、差异 100 的来源、COMPASS timeout 等）：

```bash
python - <<'PY'
import json
import math
import ast
from collections import Counter

CAP = 1200.0

def is_number(x):
    return isinstance(x, (int, float)) and not (
        isinstance(x, float) and (math.isnan(x) or math.isinf(x))
    )

def normalize_status(st):
    st = str(st).lower() if st is not None else "unknown"
    return st if st in ("sat", "unsat") else "unknown"

def parse_baseline(entry):
    if not isinstance(entry, list) or len(entry) < 2:
        return "unknown", float(CAP)
    st = normalize_status(entry[0])
    t = entry[1]
    if not is_number(t):
        return "unknown", float(CAP)
    t = float(t)
    if t > CAP:
        return "unknown", float(CAP)
    return st, t

def parse_threshold(entry):
    if not isinstance(entry, list) or len(entry) < 2:
        return "unknown", None
    st = normalize_status(entry[0] if entry[0] else "unknown")
    t = entry[1] if is_number(entry[1]) else None
    return st, t

def load_compass(path):
    with open(path, "r") as f:
        txt = f.read()
    try:
        return json.loads(txt)
    except Exception:
        return ast.literal_eval(txt)

def parse_compass(entry, time_field="total"):
    if not isinstance(entry, list) or len(entry) < 5:
        return None
    flag = str(entry[4]).lower() if entry[4] is not None else "failed"
    if time_field == "solve" and flag == "succeed" and len(entry) > 5:
        t = entry[5]
    else:
        t = entry[3] if len(entry) > 3 else None
    if not is_number(t):
        t = float(CAP)
    else:
        t = float(t)
    if t > CAP:
        return "unknown", float(CAP), flag
    st = "sat" if flag == "succeed" else "unknown"
    return st, t, flag

with open("test_rl/predictor/smt_comp_NIA/QF_NIA_test.json", "r") as f:
    keys = list(json.load(f).keys())

with open("test_rl/test_solve/NIA/NIA.json", "r") as f:
    baseline = json.load(f)

with open("test_rl/test_cvc5/predict_z3_process/QF_NIA_advanced_solver_results_all_4_threshold.json", "r") as f:
    threshold = json.load(f)

compass = load_compass("test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt")

print("=" * 80)
print("Sanity: dataset sizes")
print("=" * 80)
print("QF_NIA_test keys:", len(keys))
print("baseline NIA.json keys:", len(baseline))
print("threshold file keys:", len(threshold))
print("COMPASS cache keys:", len(compass))

print("\n" + "=" * 80)
print("(A) Baseline raw vs. timeout>1200")
print("=" * 80)
raw_norm_counts = Counter()
raw_time_gt = 0
raw_time_gt_norm = Counter()
for k in keys:
    v = baseline.get(k)
    st = normalize_status(v[0] if isinstance(v, list) and v else None)
    raw_norm_counts[st] += 1
    if isinstance(v, list) and len(v) > 1 and is_number(v[1]) and float(v[1]) > CAP:
        raw_time_gt += 1
        raw_time_gt_norm[st] += 1
print("Baseline normalized counts (ignoring time):", dict(raw_norm_counts))
print("Baseline records with raw time>1200:", raw_time_gt, "breakdown:", dict(raw_time_gt_norm))

parsed_counts = Counter()
for k in keys:
    st, _ = parse_baseline(baseline.get(k))
    parsed_counts[st] += 1
print("Baseline counts AFTER applying rule time>1200 => unknown:", dict(parsed_counts))

print("\n" + "=" * 80)
print("(B) Where do the old 6711/2540 counts come from?")
print("=" * 80)
th_counts = Counter()
status_diff = 0
sat_in_baseline_but_unknown_in_threshold = 0
sat_in_baseline_but_unknown_methods = Counter()
for k in keys:
    st_th, _ = parse_threshold(threshold.get(k))
    st_b, _ = parse_baseline(baseline.get(k))
    th_counts[st_th] += 1
    if st_th != st_b:
        status_diff += 1
    if st_b == "sat" and st_th == "unknown":
        sat_in_baseline_but_unknown_in_threshold += 1
        v = threshold.get(k)
        method = v[7] if isinstance(v, list) and len(v) > 7 else None
        sat_in_baseline_but_unknown_methods[str(method)] += 1
print("Threshold file counts using v[0] (old-style direct metric):", dict(th_counts))
print("Count(threshold_status != baseline_status_after_timeout):", status_diff)
print("Count(baseline SAT but threshold UNKNOWN):", sat_in_baseline_but_unknown_in_threshold)
print("Breakdown of those cases by threshold v[7] (method/status):")
for m, c in sat_in_baseline_but_unknown_methods.most_common():
    print(f"  {m}: {c}")

print("\n" + "=" * 80)
print("(C) COMPASS cache: timeout>1200 handling check")
print("=" * 80)
keys_intersection = [k for k in keys if k in compass]
print("Intersection keys (test ∩ compass_cache):", len(keys_intersection))
for tf in ("total", "solve"):
    parsed_c_counts = Counter()
    raw_t_gt = 0
    gt_flags = Counter()
    succeed_total = 0
    succeed_t_gt = 0
    for k in keys_intersection:
        entry = compass.get(k)
        if not isinstance(entry, list) or len(entry) < 5:
            continue
        flag = str(entry[4]).lower() if entry[4] is not None else "failed"
        if flag == "succeed":
            succeed_total += 1
        if tf == "solve" and flag == "succeed" and len(entry) > 5:
            raw_t = entry[5]
        else:
            raw_t = entry[3] if len(entry) > 3 else None
        if is_number(raw_t) and float(raw_t) > CAP:
            raw_t_gt += 1
            gt_flags[flag] += 1
            if flag == "succeed":
                succeed_t_gt += 1
        parsed = parse_compass(entry, time_field=tf)
        if parsed is None:
            continue
        st, _, _ = parsed
        parsed_c_counts[st] += 1
    print(f"\nCompass time_field={tf}:")
    print("  parsed status counts:", dict(parsed_c_counts))
    print("  raw chosen time>1200:", raw_t_gt, "breakdown by flag:", dict(gt_flags))
    print("  succeed total:", succeed_total, "succeed with raw time>1200:", succeed_t_gt)
PY
```

该脚本在本仓库上的关键输出摘要（已在本次核验中实际得到）：

```text
QF_NIA_test keys: 10043
baseline counts: sat=6811 unsat=792 unknown=2440
threshold(v[0]) counts: sat=6711 unsat=792 unknown=2540
Count(baseline SAT but threshold UNKNOWN): 100
  succeed: 81
  failed: 19
Baseline raw time>1200: 2382 (all already unknown)
```

---

## 总结

- **100 个差异的根因**：旧口径使用的 `QF_NIA_advanced_solver_results_all_4_threshold.json` 中，**100 个 key 的结果字段 `v[0]` 未正确记录 SAT**（在 `v[7]` 中体现为 `succeed`/`failed`），导致被误统计为 `unknown`。
- **timeout 规则确认**：
  - baseline/threshold 中不存在 `sat/unsat` 且 `time>1200` 的情况；
  - `time>1200` 的条目全部处于 `unknown`，符合 “`time>1200 => unknown`” 的定义。
