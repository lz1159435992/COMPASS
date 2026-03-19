# RQ1/RQ2/RQ3 数据整体核算汇总（20260309）

本文件对 `paper/eval.tex` 中 RQ1/RQ2/RQ3 的所有核心表/图数据进行“脚本—数据源—复算产物”的一致性核查，标注一致/不一致项，并给出下一步建议（**不改论文**）。

---

## 0. 论文中需要核对的关键表/图（eval.tex）

- **RQ1**
  - Table `tab:multi-solver-comparison`（SMTimer，多求解器对比）
  - Table `tab:smtcomp-arith-overall`（SMT-COMP/QF_NIA，多求解器对比）
  - Table `tab:intersection-analysis`（两数据集 intersection breakdown）

- **RQ2**
  - Table `tab:llm-comparison`（LLM 对比）
  - Figure `fig:llm-effectiveness`（LLM effectiveness，`pics/RQ1-effectiveness.pdf`）
  - Table `tab:RQ3-ablation`（组件消融，Total=337）
  - Figure `fig:RQ3-performance`（性能曲线，`pics/RQ3-performance.pdf`）

- **RQ3**
  - Table `tab:parallel-execution`（QF_NIA 10,043，Direct vs Parallel Portfolio）

---

## 1) RQ2 核算结论（New_RQ2_Component_Analysis）

- **复算产物**：
  - `New_RQ2_Component_Analysis/20260309_202958/filtered/RQ2_recomputed_filtered_minvars5.md`
  - fig4/fig5 一键验证：`New_RQ2_Component_Analysis/20260309_202958/verify_rq2_fig4_fig5_20260309.py`

- **与论文一致项**：
  - `tab:RQ3-ablation`（Total=337）逐项一致（Solved/Rate/AvgTime）。
  - `fig:RQ3-performance` 的输入 universe（`time_dict_*_106.txt`，n=337）与论文一致。

- **与论文不一致项（需要后续确认数据批次）**：
  - `tab:llm-comparison` 中 **L3.3/R1 两行**：
    - 复算（min_vars=5）得到：L3.3=86/25.5/403.5，R1=65/19.3/577.5
    - 论文为：L3.3=89/26.4/231，R1=87/25.8/248
  - 结论：论文的 L3.3/R1 很可能使用了**另一批次 info_dict**（不是当前脚本默认的 `0107` 那两份）。

---

## 2) RQ3 核算结论（New_RQ3_Routing_Analysis）

- **复算产物**：
  - `New_RQ3_Routing_Analysis/20260309_225937/RQ3_复算汇总_20260309.md`
  - 原始 stdout：`New_RQ3_Routing_Analysis/20260309_225937/RQ3_parallel_portfolio_stdout.md`

- **与论文一致项**：
  - `tab:parallel-execution`（QF_NIA 10,043）复算可对齐论文（按 1 位小数/整数）。

- **额外补充核查（你要求的 SMTimer + SMT-COMP/QF_NIA 三求解器，除 parti 外）**：
  - 复核文档：
    - `New_RQ3_Routing_Analysis/20260309_225937/RQ3_SMTimer_SMTComp_QF_NIA_三求解器补充复核_20260309.md`
  - 结论：Z3/CVC5/MathSAT 在 SMTimer（full baseline key set）与 SMT-COMP/QF_NIA（test_keys=10043）两种设置下，均与 `parallel_portfolio_summary.md` 记录一致（差异仅四舍五入）。

---

## 3) RQ1 核算结论（New_RQ1_Effectiveness_Analysis）

### 3.1 已做的动作
- 我对 `New_RQ1_Effectiveness_Analysis/20260309_153333/recompute_rq1_tables_to_md_20260309.py` 做了口径修正，使其支持 `--paper-smtimer-universe`：
  - SMTimer universe：baseline status∈{sat,unknown}、drop unsat、baseline_time>300、严格 |V|>min_vars（依赖 `New_RQ2_Component_Analysis/var_count.txt`）
  - baseline solved：只算 `sat`

- 复算输出：
  - `New_RQ1_Effectiveness_Analysis/20260309_153333/RQ1_recomputed_summary_paper_universe_minvars5_20260309.md`
  - `New_RQ1_Effectiveness_Analysis/20260309_153333/RQ1_recomputed_summary_solver_cached_subsets_minvars5_20260310_mathsat1913_20260309.md`

### 3.2 与论文一致项
- **SMT-COMP/QF_NIA**（`tab:smtcomp-arith-overall` 与 `tab:intersection-analysis` 的 SMT-COMP 部分）
  - 复算与论文对齐（Z3/CVC5/MathSAT5/AriParti 四行）。

- **SMTimer/Z3 行**：
  - 复算得到 Total=337, solved=72→94，与论文 RQ1 表中 Z3 行的 Total/solved 对齐。

- **SMTimer/CVC5 行**（按 solver 独立缓存子集口径）：
  - 使用 `test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`，在 baseline status∈{sat,unknown}、baseline_time>300 的前提下，对变量过滤采用 **`|V| >= 5`（inclusive）**。
  - 得到 Total=561，Solved(Base)=117，Solved(+tool)=360，与论文一致。
  - AvgT 口径采用 **cap-all 平均**（对每个实例取 `t` 或 `cap`，再对 Total 求均值），得到 AvgT(Base)=1054.8（论文 1055），AvgT(+tool)=44.4（论文 44），差异仅来自四舍五入。

### 3.3 与论文不一致项（当前仍需进一步定位）
在开启 `--paper-smtimer-universe` 后，SMTimer 仍存在与论文不一致：

- 论文 `tab:multi-solver-comparison`：
  - CVC5 Total=561（baseline 117 → +tool 360）
  - MathSAT Total=150（baseline 29 → +tool 100）

- 当前复算（paper-universe, min_vars=5）：
  - CVC5 Total=555（baseline 113 → +tool 357）
  - MathSAT Total=101（baseline 0 → +tool 0）
  - intersection 的 CVC5 行也因此变为 Both=40（论文是 43）

这说明：**论文 RQ1 的 SMTimer（CVC5/MathSAT）行所用 universe/输入文件批次，与我当前使用的这套“统一 SMTimer universe”并不一致**。

更直观地说：
- 对 Z3：论文 SMTimer 的 Total=337 与 RQ2 使用的 universe 完全一致（可复现）。
- 对 CVC5/MathSAT：论文的 Total 更像是“来自各自实验时生成的子集缓存”，而不是从统一 universe 再过滤得出。

补充：你已确认 **SMTimer/MathSAT 的 Total=150 是错误口径**（应以最新实验缓存为准）。

- 最新实验缓存：
  - compass：`New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/mathsat5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat5_0628.txt`
  - baseline：`New_RQ3_Routing_Analysis/mathsat_smtimer_nju_cache_and_baseline/smtimer_710/mathsat5_smtimer_results_rl.json`
- 实际记录的 key 数为 **1913**；在 **Total=1913** 全量 key set 上复算得到：
  - `Solved(Base)=29`，`Solved(+tool)=100`
  - `AvgT(Base)=1193.9s`，`AvgT(+tool)=206.1s`（cap-all 平均）
- 对应复算产物：`New_RQ1_Effectiveness_Analysis/20260309_153333/RQ1_recomputed_summary_solver_cached_subsets_minvars5_20260310_mathsat1913_20260309.md`。

### 3.4 建议的下一步（需要你确认口径）
为了把 RQ1 的 SMTimer（CVC5/MathSAT）也做到 **100% 复现论文表格**，我建议你先确认论文当时的口径属于哪一种：

- **方案 A（统一 universe）**：所有 solver 在 SMTimer 都用同一个 universe（如 RQ2 的 337-key universe 或其扩展），然后每个 solver 在该 universe 上统计；
- **方案 B（各 solver 自己的缓存子集）**：每个 solver 使用各自实验中生成的 key 集合（因此 Total 不同），论文表格直接抄这些缓存统计。

目前论文 `tab:multi-solver-comparison` 的 Total（Z3=337, CVC5=561, MathSAT=150, BVParti=33）看起来更像 **方案 B 的混合**：
- Z3 与 RQ2 universe 对齐
- CVC5/MathSAT/BVParti 可能来自各自 pipeline 的子集缓存

当前你已确认 MathSAT=150 为错误口径，因此后续建议为：

- 若以“最新缓存”作为准据：在核算报告中以 MathSAT=1913 的统计为准记录（不改论文），并在差异列表中明确指出论文 MathSAT 行使用了错误的 Total。

如果你确认要按 **方案 B** 复现，我下一步会去定位：
- CVC5 的 561-key 和 MathSAT 的 150-key 分别是由哪个脚本/哪个过滤条件导出的 key set（是从 `info_dict` 本身、还是另一个 keys 文件/日志），然后让复算脚本对该 key set 直接统计。

---

## 4) 总体结论（截至目前）

- **RQ2**：
  - 组件消融表与性能曲线口径可复现；LLM 对比表的 L3.3/R1 需要确认论文数据文件批次。

- **RQ3**：
  - 论文表格可复现；补充的 SMTimer + SMT-COMP/QF_NIA 三求解器数据计算准确。

- **RQ1**：
  - SMT-COMP/QF_NIA 的表与 intersection 可复现；
  - SMTimer 的 Z3 行可复现；
  - SMTimer 的 CVC5/MathSAT 行目前仍与论文不一致，需要你确认论文口径（统一 universe vs 各 solver 子集缓存）后再做 100% 对齐复现。
