# JSON文件格式兼容性修改说明

## 问题描述

原始的 `test_group_get_dis_smt_comp_bert_embeding_single.py` 文件只能处理简单格式的JSON文件（如cvc5_smtimer_results_predictor.json），但无法处理复杂格式的JSON文件（如SMTimer_z3_result_predictor.json）。

## 文件结构差异

### 1. 简单格式（cvc5_smtimer_results_predictor.json）
```json
{
  "file_path": [
    "result_status",  // "sat", "unsat", "unknown"
    solve_time,       // 数字
    time_limit,       // 1200
    {}               // 空字典
  ]
}
```

### 2. 复杂格式（SMTimer_z3_result_predictor.json）
```json
{
  "metadata": {
    "execution_info": {...},
    "configuration": {...},
    "statistics": {...},
    "timing": {...}
  },
  "results": {
    "file_path": {
      "result": "sat/unsat/error",
      "solve_time": number,
      "total_time": number,
      "error": null_or_error_message,
      "stdout": output_string,
      "returncode": number,
      "timestamp": timestamp_string
    }
  }
}
```

## 修改内容

### 1. 新增 `get_solve_result_and_time` 函数
```python
def get_solve_result_and_time(solve_dict, key):
    """
    从solve_dict中获取结果和时间，兼容新旧两种格式
    
    Args:
        solve_dict: 求解结果字典
        key: 文件路径键
    
    Returns:
        tuple: (category, time_value)
    """
```

**功能特点：**
- 自动检测JSON格式类型
- 兼容处理两种不同的数据结构
- 将"error"状态映射为"unknown"
- 处理solve_time为-1的错误情况

### 2. 增强 `convert_timeout_to_unknown` 函数
```python
def convert_timeout_to_unknown(solve_dict):
    """
    将solve_dict中每个value的第一个值如果是'timeout'则改为'unknown'
    同时处理新格式的JSON文件结构
    """
```

**新增功能：**
- 检测并处理新格式的JSON结构
- 在results字段中转换timeout状态
- 保持向后兼容性

### 3. 修改 `test_group_get_label_and_time` 函数
- 使用新的 `get_solve_result_and_time` 函数获取数据
- 移除了硬编码的数据访问方式
- 提高了代码的健壮性

## 数据映射规则

### 状态映射
- `"sat"` → `"sat"`
- `"unsat"` → `"unsat"`
- `"error"` → `"unknown"`
- `"timeout"` → `"unknown"`

### 时间处理
- 简单格式：直接使用 `solve_dict[key][1]`
- 复杂格式：使用 `solve_dict["results"][key]["solve_time"]`
- 错误情况（solve_time = -1）：映射为 0

## 测试验证

### 1. 兼容性测试
运行 `test_json_compatibility.py` 验证：
- 旧格式处理正确性
- 新格式处理正确性
- timeout转换功能
- 实际文件处理能力

### 2. 功能演示
运行 `demo_fixed_functionality.py` 展示：
- 完整的数据处理流程
- 标签生成过程
- 时间分类逻辑

## 使用方法

修改后的代码可以无缝处理两种格式的JSON文件：

```python
# 对于旧格式文件
run_complete_process(
    info_dict_path='/path/to/info_dict.txt',
    solve_dict_path='/path/to/cvc5_smtimer_results.json'
)

# 对于新格式文件
run_complete_process(
    info_dict_path='/path/to/info_dict.txt',
    solve_dict_path='/path/to/SMTimer_z3_result.json'
)
```

## 向后兼容性

- 所有现有的代码调用方式保持不变
- 旧格式的JSON文件处理逻辑完全保留
- 新增的功能不会影响现有功能

## 文件清单

1. **主要修改文件：**
   - `test_group_get_dis_smt_comp_bert_embeding_single.py`

2. **测试文件：**
   - `test_json_compatibility.py` - 兼容性测试
   - `demo_fixed_functionality.py` - 功能演示

3. **文档文件：**
   - `README_MODIFICATIONS.md` - 本说明文档

## 总结

通过这些修改，`bvparti_process` 目录下的代码现在可以：
1. 自动识别JSON文件格式
2. 正确处理两种不同的数据结构
3. 保持完全的向后兼容性
4. 提供更好的错误处理和状态映射

修改后的代码已经通过测试验证，可以正常处理两种格式的JSON文件，解决了原始问题。
