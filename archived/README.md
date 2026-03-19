# 归档文件说明 (Archived Files)

本目录包含从项目根目录和 `test_rl` 目录归档的文件。这些文件不再活跃使用，但保留用于历史参考。

---

## 目录结构

### `archived/build_artifacts/`
构建产物和包管理文件。

| 目录/文件 | 大小 | 说明 |
|-----------|------|------|
| `build/` | 1.8MB | Python 构建产物（wheel 等） |
| `Pearl.egg-info/` | - | Setuptools 包元数据 |
| `__pycache__/` | - | Python 字节码缓存 |

### `archived/analysis_outputs/`
实验分析输出和中间结果。

| 目录 | 大小 | 说明 |
|------|------|------|
| `features/` | - | 特征提取中间文件 |
| `log/` | - | 运行日志 |
| `log_overfit/` | - | 过拟合实验日志 |
| `models/` | - | 中间模型文件 |
| `supervenn_output/` | - | Supervenn 图表输出 |
| `New_RQ1_Effectiveness_Analysis/` | - | RQ1 有效性分析 |
| `New_RQ2_Component_Analysis/` | - | RQ2 组件分析 |
| `New_RQ3_Routing_Analysis/` | - | RQ3 路由分析 |
| `RQ4_Analysis_Framework/` | 141MB | RQ4 分析框架 |

### `archived/development_files/`
开发过程文件和测试环境。

| 目录 | 大小 | 说明 |
|------|------|------|
| `backup_models/` | - | 模型备份 |
| `llm_no_rl/` | - | 无 RL 的 LLM 实验 |
| `ollama_model_file/` | - | Ollama 模型配置 |
| `pdf_conversion/` | - | PDF 转换工具 |
| `test_time/` | - | 时间测试 |
| `torch_rl_test/` | - | PyTorch RL 测试 |
| `test/` | - | Pearl 原始测试 |
| `venv/` | 6.2GB | Python 虚拟环境（大文件，仅本地） |
| `scripts/` | - | 开发脚本 |
| `tutorials/` | - | 教程文件 |

### `archived/internal_docs/`
内部文档和迁移记录。

| 文件/目录 | 说明 |
|-----------|------|
| `PATH_MIGRATION_GUIDE.md` | 路径迁移指南（内部记录） |
| `EXPERIMENT_DATA_ANALYSIS.md` | 实验数据分析记录 |
| `TEST_RL_CLEANUP_ANALYSIS.md` | test_rl 清理分析记录 |
| `dev_docs/` | 开发文档目录 |

### `archived/root_temp_files/`
从项目根目录归档的临时文件和旧版本数据。

| 文件 | 大小 | 说明 |
|------|------|------|
| `NIA.json` | 120MB | SMT-COMP QF_NIA 基准数据（大文件，仅本地保留） |
| `2024-10-22-conv.json` | - | 早期实验结果 |
| `QF_NIA_advanced_solver_results_all.json` | - | QF_NIA 高级求解器结果 |
| `QF_NIA_advanced_solver_results_all.json.backup_corrupted` | - | 损坏的备份文件 |
| `technical_verification_report.json` | - | 技术验证报告 |
| `empirical_study_content.tex` | - | 实证研究内容（LaTeX） |
| `improved_rq5_content.tex` | - | 改进的 RQ5 内容（LaTeX） |
| `setup_bvparti_remote.sh` | - | BVParti 远程安装脚本 |
| `bvparti_environment.yml` | - | BVParti Conda 环境配置 |

### `archived/large_models/`
超过 50MB 的模型文件，仅本地保留，不上传远程仓库。

| 文件 | 大小 | 说明 |
|------|------|------|
| `QF_NIA_bert_predictor_mask_best_llm.pth` | 103MB | QF_NIA SAT/UNSAT 预测器（最佳模型） |
| `QF_NIA_bert_predictor_mask_best.pth` | 103MB | QF_NIA SAT/UNSAT 预测器 |
| `QF_NIA_bert_predictor_mask_final_llm.pth` | 103MB | QF_NIA SAT/UNSAT 预测器（最终模型） |
| `SMTimer_bert_predictor_mask_best.pth` | 103MB | SMTimer SAT/UNSAT 预测器 |

### `archived/unused_benchmarks/`
未在论文中使用的基准测试文件。

| 目录 | 大小 | 说明 |
|------|------|------|
| `QF_LIA/` | 380MB | 线性整数算术基准（未纳入论文） |
| `QF_IDL/` | 3.3MB | 整数差分逻辑基准（未纳入论文） |
| `QF_BV/` | 388KB | 位向量基准（未纳入论文） |

### `archived/paper_revision_reports/`
论文修订过程中的分析报告。

包含 23 个 Markdown 文件，记录论文结构调整、实证研究集成、相关工作修订等内容。

### `archived/experiment_analysis_scripts/`
实验分析脚本。

包含 18 个 Python 脚本，用于分析求解时间、并行执行、RQ 结果等。

### `archived/test_scripts/`
测试和验证脚本。

包含 10 个测试脚本，用于验证 QF_NIA 参数、RL-LLM 集成等。

### `archived/rq5_related/`
RQ5 相关文件（论文中未使用）。

包含 RQ3/RQ4/RQ5 分析报告和实验脚本。

### `archived/old_info_dicts/`
旧版本 `info_dict` 文件。

包含 78 个实验数据文件（约 157MB），来自早期实验版本。

---

## `test_rl/archived/` 目录

### `test_rl/archived/deprecated_scripts/`
已废弃的实验脚本。

| 类型 | 文件数 | 说明 |
|------|--------|------|
| 旧版环境 | 3 | `env_gai_3.py`, `env_gai_4.py`, `env_gai_4_v2.py` |
| 旧版实验 | 10+ | `test_group_gai_5_*`, `test_group_gai_6_*` 等中间版本 |
| 测试脚本 | 5 | `bert_embedder_test.py`, `embedding_test*.py` 等 |

### `test_rl/archived/old_models/`
旧版预测器模型文件。

| 文件 | 大小 | 说明 |
|------|------|------|
| `bert_predictor*.pth` | 388KB-422KB | 早期 BERT 预测器模型 |
| `BootstrappedDQN-LSTM-return.pt` | 1.2KB | DQN-LSTM 模型检查点 |

### `test_rl/archived/temp_files/`
临时数据文件。

| 文件 | 说明 |
|------|------|
| `result_dict*.txt` | 结果字典文件 |
| `pre_result*.txt` | 预处理结果 |
| `file_time*.txt` | 文件时间记录 |
| `example.txt`, `constraints.smt2` | 示例文件 |

### `test_rl/archived/experiment_data/`
实验数据文件。

| 文件 | 说明 |
|------|------|
| `features.npy`, `labels.npy`, `time.npy` | NumPy 特征数组 |
| `smt.json`, `smt4.18.json` | SMT 约束数据 |
| `timeout_keys.json` | 超时记录 |

### `test_rl/archived/logs/`
实验日志文件（约 417MB）。

包含 325 个日志文件，来自各求解器实验运行记录。

---

## 大文件处理说明

以下文件超过 GitHub 50MB 限制，已通过 `.gitignore` 排除，仅保留在本地：

- `archived/large_models/*.pth` (>100MB)
- `archived/root_temp_files/NIA.json` (120MB)
- `archived/development_files/venv/` (6.2GB) - Python 虚拟环境
- `test_rl/archived/logs/` 目录下部分日志 (>50MB)

---

## 归档时间

- **首次归档**: 2026-03-19
- **最后更新**: 2026-03-19 (添加构建产物、分析输出、开发文件、内部文档)

---

## 联系信息

如需访问归档文件或有疑问，请联系项目维护者。
