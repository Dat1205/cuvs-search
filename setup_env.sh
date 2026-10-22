#!/bin/bash

# Script thiết lập môi trường cho Hybrid Search System
# Yêu cầu: Linux/WSL2, conda/mamba, NVIDIA GPU với CUDA support

set -e

echo "=========================================="
echo "Hybrid Search System - Environment Setup"
echo "=========================================="
echo ""

# Kiểm tra conda
if ! command -v conda &> /dev/null; then
    echo "❌ Lỗi: conda không được cài đặt"
    echo "Vui lòng cài đặt Miniconda hoặc Anaconda trước"
    exit 1
fi

echo "✓ Đã tìm thấy conda"
echo ""

# Kiểm tra CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "✓ Đã phát hiện NVIDIA GPU:"
    nvidia-smi --query-gpu=name --format=csv,noheader
    echo ""
else
    echo "⚠️  Cảnh báo: Không phát hiện nvidia-smi"
    echo "Vui lòng đảm bảo driver NVIDIA đã được cài đặt"
    echo ""
fi

# Tạo môi trường conda
echo "Đang tạo môi trường conda 'hybrid_search'..."
echo "Quá trình này có thể mất vài phút..."
echo ""

conda create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y

echo ""
echo "✓ Môi trường conda đã được tạo thành công"
echo ""

# Hướng dẫn tiếp theo
echo "=========================================="
echo "Các bước tiếp theo:"
echo "=========================================="
echo ""
echo "1. Kích hoạt môi trường:"
echo "   conda activate hybrid_search"
echo ""
echo "2. Cài đặt các thư viện Python:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Chạy script chuẩn bị dữ liệu:"
echo "   python src/1_data_prep.py"
echo ""
echo "=========================================="
