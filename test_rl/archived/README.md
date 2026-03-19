# test_rl 归档文件说明

本目录包含从 `test_rl` 根目录归档的文件，这些文件不再活跃使用但保留用于历史参考。

---

## 目录结构

### `deprecated_scripts/`
已废弃的实验脚本，包含早期版本的环境和测试脚本。

| 类型 | 文件数 | 说明 |
|------|--------|------|
| 旧版 RL 环境 | 3 | `env_gai_3.py`, `env_gai_4.py`, `env_gai_4_v2.py` |
| gai_5 系列 | 4 | `test_group_gai_5_normal_*` (SMTimer, QF_BV, QF_LRA) |
| gai_6 中间版本 | 8 | `test_group_gai_6_*_docker_*` 等实验中间版本 |
| 测试脚本 | 5 | `bert_embedder_test.py`, `embedding_test*.py`, `simple_test.py` |
| 其他 | 1 | `test_group_get_dis.py` |

**说明**: 这些脚本是实验过程中的中间版本，最终版本已整合到 `test_cvc5/` 和 `test_QF_NIA/` 目录中。

### `old_models/`
旧版预测器模型文件。

| 文件 | 大小 | 说明 |
|------|------|------|
| `bert_predictor.pth` | 388KB | 基础 BERT 预测器 |
| `bert_predictor_mask.pth` | 388KB | SAT/UNSAT 预测器 |
| `bert_predictor_mask_best.pth` | 388KB | SAT/UNSAT 最佳模型 |
| `bert_predictor_mask_final.pth` | 388KB | SAT/UNSAT 最终模型 |
| `bert_predictor_2.pth` | 422KB | 8-way 时间预测器 |
| `bert_predictor_2_mask.pth` | 422KB | 8-way 时间预测器 (mask) |
| `bert_predictor_2_mask_best_model.pth` | 0KB | 空文件 |
| `BootstrappedDQN-LSTM-return.pt` | 1.2KB | DQN-LSTM 检查点 |
| `agent_save_1111.pkl` | 0KB | 空文件 |
| `predictor.pkl` | 0KB | 空文件 |

**说明**: 当前使用的模型位于 `test_QF_NIA/*/models/` 和 `test_overfit/models_smtimer_llm/`。

### `temp_files/`
临时数据文件。

| 文件 | 说明 |
|------|------|
| `result_dict.txt` | 结果字典 |
| `result_dict_2.txt` | 结果字典 (版本2) |
| `result_dict_no_increment_QF_LIA_924.txt` | QF_LIA 非增量结果 |
| `result_dict_no_increment_QF_LRA_924.txt` | QF_LRA 非增量结果 |
| `result_dict_time.txt` | 时间结果字典 |
| `result_dict_time_pre_order.txt` | 预排序时间结果 |
| `pre_result.txt` | 预处理结果 |
| `pre_result_after.txt` | 后处理结果 |
| `file_time.txt`, `file_time_3.21.txt` | 文件时间记录 |
| `info_bit_dict.txt` | 位信息字典 |
| `example.txt` | 示例文件 |
| `constraints.smt2` | SMT2 约束示例 |

### `experiment_data/`
实验数据文件。

| 文件 | 说明 |
|------|------|
| `features.npy` | 特征数组 (NumPy) |
| `labels.npy` | 标签数组 (NumPy) |
| `time.npy` | 时间数组 (NumPy) |
| `smt.json` | SMT 约束数据 |
| `smt4.18.json` | SMT 约束数据 (4.18版本) |
| `timeout_keys.json` | 超时键记录 |

### `logs/`
实验日志文件（约 417MB）。

包含 325 个日志文件，来自：
- `test_cvc5/solver_script*.log` - CVC5 求解器日志
- `test_QF_NIA/*/log/` - QF_NIA 实验日志
- `predictor/smt_comp_NIA/log/` - 预测器训练日志

**注意**: 部分日志文件超过 50MB，已通过 `.gitignore` 排除上传。

### `old_info_dicts/`
旧版 `info_dict` 文件（约 157MB）。

包含 78 个实验数据文件，命名格式：
- `info_dict_gai_3_*.txt` - gai_3 系列实验
- `info_dict_gai_4_*.txt` - gai_4 系列实验
- `info_dict_gai_5_*.txt` - gai_5 系列实验
- `info_dict_gai_6_normal_*.txt` - gai_6 系列实验
- `info_dict_normal_*.txt` - 普通实验
- `info_dict_random.txt` - 随机实验

### `unused_benchmarks/`
未在论文中使用的基准测试数据。

| 目录 | 大小 | 说明 |
|------|------|------|
| `QF_LIA/` | 380MB | 线性整数算术基准 |
| `QF_IDL/` | 3.3MB | 整数差分逻辑基准 |
| `QF_BV/` | 388KB | 位向量基准 |

### `large_models/`
超过 50MB 的模型文件（仅本地保留）。

| 文件 | 大小 | 说明 |
|------|------|------|
| `QF_NIA_bert_predictor_mask_best_llm.pth` | 103MB | QF_NIA 预测器 |
| `QF_NIA_bert_predictor_mask_best.pth` | 103MB | QF_NIA 预测器 |
| `QF_NIA_bert_predictor_mask_final_llm.pth` | 103MB | QF_NIA 预测器 |
| `SMTimer_bert_predictor_mask_best.pth` | 103MB | SMTimer 预测器 |

---

## 当前活跃文件

`test_rl` 根目录下保留的活跃文件：

| 文件 | 说明 |
|------|------|
| `bert_predictor_2_mask.py` | 8-way 时间预测器模块 |
| `bert_predictor_mask.py` | SAT/UNSAT 预测器模块 |
| `embedding.py` | CodeBERT 嵌入模块 |
| `env_gai_6_llm_add_ce_predictor_docker.py` | 主 RL 环境 |
| `env_gai_6_llm_add_ce_predictor_docker_llm_embed.py` | LLM 嵌入版本 |
| `env_gai_6_llm_add_ce_predictor_docker_no_predict.py` | 无预测器版本 |
| `env_gai_6_llm_add_ce_predictor_local.py` | 本地运行版本 |
| `env_gai_6_llm_add_ce_predictor_save_local.py` | 本地保存版本 |
| `__init__.py` | 包初始化文件 |

---

## 归档时间

- **归档日期**: 2026-03-19
- **操作者**: 项目维护者
