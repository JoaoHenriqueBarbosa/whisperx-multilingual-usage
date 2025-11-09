#!/bin/bash

# Script para executar pipeline de transcrição

# Ativar ambiente virtual
source venv/bin/activate

# Configurar LD_LIBRARY_PATH para CUDA/cuDNN
export LD_LIBRARY_PATH="$(pwd)/venv/lib/python3.12/site-packages/nvidia/cudnn/lib:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cublas/lib:$(pwd)/venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"

# Executar pipeline
python main.py "$@" 2>&1 | grep -v "Model was trained with" | grep -v "Lightning automatically upgraded" | grep -v "Bad things might happen"
