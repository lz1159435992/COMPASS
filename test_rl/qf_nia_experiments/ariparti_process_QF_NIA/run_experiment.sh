#!/bin/bash
# QF_NIA AriParti求解实验一键运行脚本

echo "=========================================="
echo "QF_NIA AriParti求解实验"
echo "=========================================="
echo ""

# 设置Python路径
export PYTHONPATH="/home/<USER>/PycharmProjects/Pearl:$PYTHONPATH"

# 创建必要的目录
mkdir -p features/QF_NIA_llm_embeddings
mkdir -p models
mkdir -p log
mkdir -p supervenn_output

echo "步骤1: 检查embeddings..."
if [ ! -f "embeding_QF_NIA.json" ]; then
    echo "开始生成embeddings..."
    python test_group_get_dis_smt_comp_bert_embeding_single.py 2>&1 | tee log/embedding_generation.log
    echo "Embeddings生成完成！"
else
    echo "Embeddings已存在，跳过生成步骤"
fi
echo ""

echo "步骤2: 检查训练模型..."
if [ ! -f "models/QF_NIA_bert_predictor_mask_best.pth" ] || [ ! -f "models/QF_NIA_bert_predictor_2_mask_best_model.pth" ]; then
    echo "开始训练模型..."
    python train_predictor.py --mode both --epochs 100 --batch_size 32 --lr 0.001 2>&1 | tee log/training.log
    echo "模型训练完成！"
else
    echo "模型已存在，跳过训练步骤"
fi
echo ""

echo "步骤3: 运行求解实验..."
echo "求解器: AriParti"
echo "最大文件数: ${MAX_FILES:-all}"
echo ""

if [ -z "$MAX_FILES" ]; then
    python run_predictor.py --timeout 1200 2>&1 | tee log/experiment.log
else
    python run_predictor.py --timeout 1200 --max_files $MAX_FILES 2>&1 | tee log/experiment.log
fi

echo "实验完成！"
echo ""

echo "步骤4: 分析结果..."
RESULT_FILE=$(ls -t info_dict_SMTimer_*.txt 2>/dev/null | head -1)
if [ -n "$RESULT_FILE" ]; then
    echo "分析结果文件: $RESULT_FILE"
    python analyze_solver_time.py --result_file "$RESULT_FILE" --plot 2>&1 | tee log/analysis.log
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
