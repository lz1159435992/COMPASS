#!/bin/bash
# BVParti预测器远程服务器设置脚本

echo "=== BVParti预测器环境设置 ==="

# 1. 激活conda环境
echo "激活langchain环境..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate langchain

# 2. 安装缺失的包
echo "安装Python依赖..."
pip install z3-solver loguru transformers openai ollama pearl-agent

# 3. 设置环境变量
export PYTHONPATH="/home/<USER>/PycharmProjects/Pearl:$PYTHONPATH"
export CUDA_VISIBLE_DEVICES=0

# 4. 检查GPU
echo "检查GPU状态..."
nvidia-smi

# 5. 运行兼容性检查
echo "运行兼容性检查..."
cd /home/<USER>/PycharmProjects/Pearl
python test_rl/test_cvc5/bvparti_process/remote_server_compatibility_check.py

echo "设置完成！"
echo "现在可以运行: python test_rl/test_cvc5/bvparti_process/run_bvparti_predictor.py --help"
