# RQ3 并行 Portfolio（Parallel Portfolio）评估：实现过程与论文表格核验存档

## 目的

本文件用于存档：

1. RQ3 中“并行 portfolio / 并行执行”评估的**精确定义**。
2. 本仓库中用于复现该评估的**实现脚本与关键规则**（尤其是 1200s timeout 处理与“first conclusive result”选择）。
3. 对 `paper/eval.tex` 中 RQ3 表格（Direct Solving / Parallel Portfolio）进行**再次核验**，确认其与实现一致。

---

## 评估定义（论文口径）

对每个约束（constraint），同时运行：

- baseline solver（Z3 direct solving）
- \tool（COMPASS / RL+LLM）

系统接受两者中**第一个“conclusive”** 的结果：

- conclusive = `sat` 或 `unsat`
- `unknown` 不被视为 conclusive

### timeout 规则（CAP=1200s）

- 若某次运行耗时 `> 1200s`：
  - 将其视为 `unknown`
  - 并将耗时 cap 到 `1200s`

### 并行总耗时定义

- 若 baseline 与 \tool 都返回 conclusive：选择耗时更短的那个。
- 若只有一方 conclusive：选择 conclusive 一方。
- 若两者都非 conclusive：最终结果为 `unknown`。
  - 并行耗时取 `max(time_baseline, time_tool)`（在 timeout 情况下通常为 1200）。

---

## 数据源与复现入口

### 测试集 key（10,043）

- `test_rl/predictor/smt_comp_NIA/QF_NIA_test.json`

### baseline 直接求解缓存

- `test_rl/test_solve/NIA/NIA.json`
- 记录结构（最少）：`[status, time, ...]`

### \tool / COMPASS 缓存

- `test_rl/info_dict_gai_6_normal_0503_pre_llm_llama3.1:70b_1200s_QF_NIA.txt`
- 记录结构（最少）：列表且长度 >= 5

---

## 实现脚本（权威实现）

### 1) 并行 portfolio 仿真脚本

- 仓库根目录：`simulate_parallel_portfolio_qf_nia.py`

该脚本直接实现了：

- baseline 解析 + timeout 归类
- COMPASS cache 解析 + timeout 归类
- 并行 portfolio 的“first conclusive result”选择逻辑
- 指标汇总（counts / averages / totals / conversions）
- 生成可直接粘贴到论文表格的 LaTeX 行

### 2) 关键实现点（与代码对应）

#### baseline 解析（`parse_baseline(entry, cap)`）

- 从 entry 中读取：
  - `status = entry[0]`
  - `time = entry[1]`
- status 只保留 `sat/unsat`，其余归为 `unknown`
- 若 `time` 不是数字 或 `time > cap`：
  - 结果归为 `unknown`
  - 时间置为 `cap`

#### COMPASS 解析（`parse_compass(entry, cap, time_field)`）

- 使用 `entry[4]` 作为 `flag`：`succeed/failed` 等
- 时间字段选择：
  - `--compass_time_field total`：使用 `entry[3]`（**总耗时 / wall-clock total time**，包含 LLM + solver 等）
  - `--compass_time_field solve`：若 `flag==succeed`，使用 `entry[5]`（solve time）
- status 规则：
  - `flag == succeed` -> 视为 `sat`
  - 其它 -> `unknown`
- 若选用时间字段 `> cap`：
  - 视为 `unknown`，时间置为 `cap`

> 说明：论文的“并行执行”口径通常应比较 wall-clock，总体上应使用 `total` 而非 `solve`。

#### 并行选择逻辑（`simulate_portfolio(b_st,b_t,c_st,c_t)`）

- 若 baseline 与 COMPASS 都 conclusive：选时间更短者
- 若只有一方 conclusive：选 conclusive 一方
- 否则 `unknown`（耗时取 `max(b_t,c_t)`）

脚本也统计：

- `wins`：portfolio 采用 baseline / compass / both_unknown / no_compass 的次数
- `conversions`：`(baseline_status -> portfolio_status)` 的计数
- `disagreements`：两者均 conclusive 但 SAT/UNSAT 结果不同的情况（用于 sanity check）

---

## 复现命令（生成论文表格数值）

在仓库根目录运行：

```bash
python simulate_parallel_portfolio_qf_nia.py --cap 1200 --compass_time_field total
```

本次核验时该命令输出的关键数值（ALL scope）为：

- Baseline counts：`sat=6811, unsat=792, unknown=2440`
- Portfolio counts：`sat=7135, unsat=792, unknown=2116`
- `unknown -> sat` 转换：`324`
- Baseline total_time：`3173055.478`（表格中取整为 `3173055`）
- Portfolio total_time：`2803370.596`（表格中取整为 `2803371`）
- Time saved：`369684.882`（表格/论文文字四舍五入为 `369,685s`）
- Overall avg：`315.947 -> 315.9`，`279.137 -> 279.1`
- Converted cases average time：`215.1196 -> 215.1`

脚本也会打印对应的 LaTeX 行，例如：

- `Parallel Portfolio & 7135 & 792 & 2116 & 32.8 & 279.1 & 2803371 \\\n`

---

## 论文表格核验（paper/eval.tex）

### 结论

`paper/eval.tex` 的 RQ3 表格目前与上述脚本输出**一致**，且文字描述也与仿真结果一致。

### 核验点（逐项对齐）

#### 表格数值一致性

`paper/eval.tex` 中表格（RQ3 部分）当前为：

- Direct Solving：`6811 / 792 / 2440 / 32.9 / 315.9 / 3173055`
- Parallel Portfolio：`7135 / 792 / 2116 / 32.8 / 279.1 / 2803371`

这与 `simulate_parallel_portfolio_qf_nia.py --compass_time_field total` 的输出一致。

#### 文字描述一致性

论文文字写到：

- 转换 `324` 个 unknown->sat
- overall avg 从 `315.9s` 降到 `279.1s`
- total time 节省 `369,685s`（约 `102.7h`）
- 新解决的 324 个案例平均耗时 `215.1s`

这些都可由仿真输出直接推导得到（四舍五入后对齐）。

---

## 附注：为何使用 `total` 作为 COMPASS 时间

并行 portfolio 的“谁先给出 conclusive 结果”本质上与 wall-clock 耗时一致。

- 若仅用 `solve` 时间，可能忽略 LLM/预处理开销，导致对“并行完成时间”的估计偏乐观。
- 因此论文表格与复现实验均采用 `--compass_time_field total`。

---

## 附注：为何 `sat` 数量增加明显，但 `sat_avg` 变化很小

`sat_avg` 的计算只对最终状态为 `sat` 的实例求平均：`sat_avg = sat_sum / sat_count`。
因此 baseline 中最终状态为 `unknown` 的实例（大多是接近 1200s 的 timeout）不会参与 baseline 的 `sat_avg`，`unknown -> sat` 的转换不会直接“替换”原本的 SAT 平均值，而是改变了 SAT 集合的组成。

在 `--compass_time_field total` 的口径下（ALL scope）：

- Baseline：`sat_count=6811`，`sat_sum=224301.326`，`sat_avg=32.932s`
- Portfolio：`sat_count=7135`，`sat_sum=234285.878`，`sat_avg=32.836s`

Portfolio 额外解出 324 个 `unknown -> sat`，这些新增 SAT 的平均耗时约 215.1s，显著高于原本 6811 个较易 SAT 的均值。
单纯从“新增 SAT”出发，这会推高 `sat_avg`。

但 portfolio 同时也会在一部分 baseline 已经是 `sat` 的实例上选择 COMPASS（因为 COMPASS 更快返回 conclusive）。从 wins 统计可见：

- `wins['compass']=444`，其中 `unknown -> sat` 为 324，因此还有 120 个属于 `sat -> sat`，但由 COMPASS 赢得

用 `sat_sum` 的差分可以看到这 120 个 case 的加速效应抵消了新增 SAT 的拉升：

- 新增 SAT 预计带来的 SAT 时间增加约为 `324 * 215.1 ≈ 69,700s`
- 实际 SAT 总耗时只增加 `234285.878 - 224301.326 = 9,984.552s`
- 因此 baseline SAT 被加速节省的时间约为 `69,700 - 9,985 ≈ 59,700s`，平均到 120 个实例约 `~498s/instance`

综合起来，新解出的 SAT 数量占全部 SAT 的比例约 `324/7135 ≈ 4.5%`，同时还有一批原有 SAT 被明显加速，二者共同作用使 `sat_avg` 只发生很小的变化（32.9s 到 32.8s）。
这也是为什么整体收益主要体现在 `overall_avg` 与 `total_time` 的显著下降，因为它们会直接受到大量 `unknown` 超时实例从接近 1200s 降到约 215s 的影响。

---

## 总结

- 并行 portfolio 的定义与脚本实现一致：**接受第一个 conclusive（sat/unsat）结果**，并统一施加 `CAP=1200s`。
- `paper/eval.tex` 当前 RQ3 表格与复现脚本输出一致，可审计复现。
