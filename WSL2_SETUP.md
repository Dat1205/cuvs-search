# ✅ Hướng dẫn WSL2 & cuVS - ĐÃ HOÀN THÀNH

## Trạng thái: Môi trường đã được thiết lập thành công

**Ngày hoàn thành:** 2026-10-22  
**Backend:** cuVS CAGRA (NVIDIA RAPIDS)  
**GPU:** NVIDIA GeForce RTX 5060 Laptop (8GB VRAM)

---

## ✅ Đã hoàn thành

### 1. WSL2 Ubuntu
- ✅ WSL2 đã được cài đặt và chạy
- ✅ NVIDIA GPU driver hoạt động trong WSL2
- ✅ CUDA 12.0 support

### 2. Conda Environment
- ✅ Miniconda đã được cài đặt tại `~/miniconda3`
- ✅ Environment `hybrid_search` đã tạo với:
  - Python 3.10
  - cuVS 24.10
  - CuPy with CUDA 12.0
  - NumPy, SciPy

### 3. Python Libraries
- ✅ sentence-transformers
- ✅ rank-bm25
- ✅ datasets

### 4. Artifacts
- ✅ BM25 Index (1.9MB)
- ✅ Dense Embeddings (7.4MB)
- ✅ **cuVS CAGRA Index (8.6MB)** ⚡

---

## 🚀 Sử dụng môi trường

### Kích hoạt môi trường trong WSL2:
```bash
# Vào WSL2
wsl

# Kích hoạt conda environment
source ~/miniconda3/bin/activate
conda activate hybrid_search

# Di chuyển đến project
cd /mnt/d/New/hybrid_search_project

# Chạy script
python src/2_build_index.py
python src/3_search_engine.py
python src/4_benchmark.py
```

### Kiểm tra GPU:
```bash
nvidia-smi
python -c "import cupy as cp; print('CUDA:', cp.cuda.is_available())"
```

---

## 📝 Lệnh đã sử dụng

```bash
# 1. Cài Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3

# 2. Tạo environment base
conda create -n hybrid_search python=3.10 cupy cuvs=24.10 \
  cuda-version=12.0 --no-deps -c rapidsai -c nvidia -c conda-forge --override-channels -y

# 3. Cài dependencies
conda install -n hybrid_search -c conda-forge numpy scipy -y
conda install -n hybrid_search -c rapidsai -c nvidia -c conda-forge \
  libcuvs cuvs cupy cuda-version=12.0 --override-channels -y

# 4. Cài Python packages
~/miniconda3/envs/hybrid_search/bin/pip install \
  sentence-transformers rank-bm25 datasets
```

---

## 🔧 Troubleshooting (Đã giải quyết)

### ✅ Đã sửa: Lỗi Terms of Service
**Giải pháp:** Dùng `--override-channels` để bỏ qua anaconda.com repos

### ✅ Đã sửa: Network timeout khi tải packages
**Giải pháp:** Cài từng bước thay vì tất cả cùng lúc

### ✅ Đã sửa: pip not found
**Giải pháp:** Dùng đường dẫn đầy đủ `~/miniconda3/envs/hybrid_search/bin/pip`

---

**Kết quả:** Môi trường production-ready với cuVS CAGRA GPU search!
