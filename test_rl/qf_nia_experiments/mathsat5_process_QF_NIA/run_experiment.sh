#!/bin/bash
# QF_NIA MathSAT5求解实验一键运行脚本

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "QF_NIA MathSAT5求解实验"
echo "=========================================="
echo ""

# 设置Python路径
export PYTHONPATH="/home/lz/PycharmProjects/Pearl:$PYTHONPATH"

if [ -n "${CONDA_PYTHON:-}" ]; then
    PYTHON_CMD=("$CONDA_PYTHON")
elif [ -n "${CONDA_ENV:-}" ]; then
    PYTHON_BIN=""
    for base in "$HOME/anaconda3" "$HOME/miniconda3" "/home/lz/anaconda3" "/opt/conda"; do
        candidate="$base/envs/$CONDA_ENV/bin/python"
        if [ -x "$candidate" ]; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
    if [ -z "$PYTHON_BIN" ]; then
        echo "找不到conda环境Python: env=$CONDA_ENV。你可以设置 CONDA_PYTHON=/abs/path/to/python 以显式指定解释器。" >&2
        exit 1
    fi
    PYTHON_CMD=("$PYTHON_BIN")
else
    PYTHON_CMD=(python)
fi

echo "Python解释器: ${PYTHON_CMD[*]}"

# 创建必要的目录
mkdir -p features/QF_NIA_llm_embeddings
mkdir -p models
mkdir -p log
mkdir -p supervenn_output

# 步骤1: 生成embeddings（可选，如果已有可跳过）
echo "步骤1: 检查embeddings..."
if [ ! -f "embeding_QF_NIA.json" ] || [ ! -f "QF_NIA_train.json" ] || [ ! -f "QF_NIA_test.json" ]; then
    echo "开始生成/更新embeddings与数据划分..."
    "${PYTHON_CMD[@]}" test_group_get_dis_smt_comp_bert_embeding_single.py 2>&1 | tee log/embedding_generation.log
    echo "Embeddings与数据划分生成完成！"
else
    echo "Embeddings与数据划分已存在，跳过生成步骤"
fi
echo ""

# 步骤2: 训练模型（可选，如果已有可跳过）
echo "步骤2: 检查训练模型..."
if [ ! -f "models/QF_NIA_bert_predictor_mask_best.pth" ] || [ ! -f "models/QF_NIA_bert_predictor_2_mask_best_model.pth" ]; then
    echo "开始训练模型..."
    "${PYTHON_CMD[@]}" train_predictor.py --mode both --epochs 100 --batch_size 32 --lr 0.001 2>&1 | tee log/training.log
    echo "模型训练完成！"
else
    echo "模型已存在，跳过训练步骤"
fi
echo ""

# 步骤3: 运行求解实验
echo "步骤3: 运行求解实验..."
echo "求解器: MathSAT5"
echo "最大文件数: ${MAX_FILES:-all}"
echo ""

if [ -z "${MAX_FILES:-}" ]; then
    "${PYTHON_CMD[@]}" run_predictor.py --timeout 1200 2>&1 | tee log/experiment.log
else
    "${PYTHON_CMD[@]}" run_predictor.py --timeout 1200 --max_files "$MAX_FILES" 2>&1 | tee log/experiment.log
fi

echo "实验完成！"
echo ""

# 步骤4: 分析结果
echo "步骤4: 分析结果..."
RESULT_FILE=$(ls -t info_dict_SMTimer_*.txt 2>/dev/null | head -1 || true)
if [ -n "$RESULT_FILE" ]; then
    echo "分析结果文件: $RESULT_FILE"
    "${PYTHON_CMD[@]}" analyze_solver_time.py --result_file "$RESULT_FILE" --plot 2>&1 | tee log/analysis.log
    echo "结果分析完成！"
else
    echo "未找到结果文件"
fi

echo ""
echo "=========================================="
echo "实验流程全部完成！"
echo "=========================================="
echo ""
echo "生成的文件："
echo "  - Embeddings: embeding_QF_NIA.json"
echo "  - 训练集: QF_NIA_train.json"
echo "  - 测试集: QF_NIA_test.json"
echo "  - 模型: models/"
echo "  - 实验结果: $RESULT_FILE"
echo "  - 分析报告: solver_time_analysis.json"
echo "  - 可视化: supervenn_output/"
echo ""
