#!/bin/bash
# =============================================================================
# vLLM Qwen Model Deployment Script
# =============================================================================
# 用于部署 Qwen2.5 模型的 vLLM 服务脚本
# 支持 GPTQ 量化和多卡张量并行
# =============================================================================

# ========================
# 可配置参数
# ========================

# 模型路径 (必须修改为实际路径)
MODEL_PATH="${MODEL_PATH:-/root/rivermind-data/hf_cache/models--Qwen--Qwen2.5-32B-Instruct-GPTQ-Int4/snapshots/c83e67dfb2664f5039fd4cd99e206799e27dd800}"

# GPU 设备配置 (多卡用逗号分隔，如 "0,1,2,3")
CUDA_DEVICES="${CUDA_DEVICES:-0,1}"

# 量化方式: gptq, gptq_marlin, awq, squeezellm, fp8
QUANTIZATION="${QUANTIZATION:-gptq_marlin}"

# 张量并行数量 (应等于GPU数量)
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-2}"

# 模型最大上下文长度
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"

# 服务配置
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen-agent}"

# ========================
# 启动 vLLM 服务
# ========================

echo "============================================"
echo "Starting vLLM Server"
echo "============================================"
echo "Model Path: ${MODEL_PATH}"
echo "GPU Devices: ${CUDA_DEVICES}"
echo "Quantization: ${QUANTIZATION}"
echo "Tensor Parallel Size: ${TENSOR_PARALLEL_SIZE}"
echo "Max Model Length: ${MAX_MODEL_LEN}"
echo "Host: ${HOST}:${PORT}"
echo "Served Model Name: ${SERVED_MODEL_NAME}"
echo "============================================"

CUDA_VISIBLE_DEVICES=${CUDA_DEVICES} vllm serve "${MODEL_PATH}" \
    --quantization ${QUANTIZATION} \
    --tensor-parallel-size ${TENSOR_PARALLEL_SIZE} \
    --max-model-len ${MAX_MODEL_LEN} \
    --trust-remote-code \
    --served-model-name ${SERVED_MODEL_NAME} \
    --host ${HOST} \
    --port ${PORT}
