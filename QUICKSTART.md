# 🚀 Quick Start Guide

Hướng dẫn chạy dự án từ đầu đến cuối trong 15 phút.

## Điều kiện tiên quyết

- ✅ Đã cài đặt WSL2 trên Windows
- ✅ Đã cài đặt Miniconda trong WSL2
- ✅ Có NVIDIA GPU với CUDA support

> Nếu chưa có, xem [INSTALL.md](INSTALL.md) để cài đặt từ đầu.

---

## Bước 1: Clone hoặc mở dự án (1 phút)

```bash
# Vào WSL2
wsl

# Di chuyển đến thư mục dự án
cd /mnt/d/New/hybrid_search_project

# Hoặc nếu clone từ Git
# git clone <repo-url>
# cd hybrid_search_project
```

---

## Bước 2: Tạo môi trường conda (5 phút)

```bash
# Sử dụng script tự động (khuyên dùng)
bash setup_env.sh

# Hoặc chạy thủ công
conda create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y

# Kích hoạt môi trường
conda activate hybrid_search
```

---

## Bước 3: Cài đặt dependencies (2 phút)

```bash
pip install -r requirements.txt
```

File `requirements.txt` chứa:
```
sentence-transformers
rank-bm25
datasets
```

---

## Bước 4: Chạy pipeline (5-7 phút)

### 4.1. Thu thập dữ liệu (1 phút)

```bash
python src/1_data_prep.py
```

**Output:**
```
✓ Đã tải 5000 mẫu từ AG News
✓ Hoàn thành tiền xử lý 5000 văn bản
✓ Đã lưu vào artifacts/corpus.pkl
```

**File tạo ra:** `artifacts/corpus.pkl` (2.9MB)

### 4.2. Xây dựng indexes (2-3 phút)

```bash
python src/2_build_index.py
```

**Output:**
```
✓ Đã build BM25 Index (1.84MB)
✓ Đã encode 5000 văn bản → 384-dim vectors (7.32MB)
✓ Đã build cuVS CAGRA Index (8.55MB)
```

**Files tạo ra:**
- `artifacts/bm25_model.pkl` (1.9MB)
- `artifacts/embeddings.npy` (7.4MB)
- `artifacts/cagra_index.bin` (8.6MB)

> **Lưu ý:** Bước này tải model `all-MiniLM-L6-v2` (~80MB) lần đầu.

### 4.3. Test tìm kiếm (< 1 phút)

```bash
python src/3_search_engine.py
```

**Output:** Kết quả tìm kiếm mẫu cho các query test.

### 4.4. Benchmark hiệu năng (1-2 phút)

```bash
python src/4_benchmark.py
```

**Output:**
```
🎯 GPU Search: 1.64ms average (PASS ✅)
🔍 Hybrid Search: 9.09ms average
📊 Throughput: 110 queries/second
```

---

## Bước 5: Sử dụng trong code

```python
from src.search_engine_module import HybridSearchEngine

# Khởi tạo
engine = HybridSearchEngine("artifacts")

# Tìm kiếm
results = engine.hybrid_search("stock market crash", top_k=5)

# In kết quả
for i, doc in enumerate(results, 1):
    print(f"{i}. [Score: {doc['rrf_score']:.4f}] {doc['text'][:100]}...")
```

---

## Kiểm tra cài đặt

### Test GPU

```bash
# Kiểm tra CUDA
nvidia-smi

# Kiểm tra CuPy
python -c "import cupy as cp; print('CUDA available:', cp.cuda.is_available())"
```

**Output mong đợi:**
```
CUDA available: True
```

### Test cuVS

```python
python -c "from cuvs.neighbors import cagra; print('cuVS OK')"
```

---

## Cấu trúc thư mục sau khi chạy

```
hybrid_search_project/
├── artifacts/                    ← Được tạo sau bước 4.1
│   ├── corpus.pkl               ← Bước 4.1
│   ├── bm25_model.pkl           ← Bước 4.2
│   ├── embeddings.npy           ← Bước 4.2
│   └── cagra_index.bin          ← Bước 4.2
├── src/
│   ├── 1_data_prep.py
│   ├── 2_build_index.py
│   ├── 3_search_engine.py
│   ├── 4_benchmark.py
│   └── search_engine_module.py
├── requirements.txt
├── setup_env.sh
└── README.md
```

---

## Các lệnh thường dùng

```bash
# Kích hoạt môi trường
conda activate hybrid_search

# Kiểm tra GPU
nvidia-smi

# Xem kích thước artifacts
du -sh artifacts/*

# Rebuild index (nếu thay đổi dữ liệu)
rm -rf artifacts/*.bin artifacts/*.pkl
python src/1_data_prep.py
python src/2_build_index.py

# Deactivate môi trường
conda deactivate
```

---

## Troubleshooting nhanh

### ❌ Lỗi: `ModuleNotFoundError: No module named 'cupy'`
**Giải pháp:**
```bash
conda activate hybrid_search
conda install -c conda-forge cupy cuda-version=12.0 -y
```

### ❌ Lỗi: `CUDA out of memory`
**Giải pháp:** Giảm batch_size trong `src/2_build_index.py`:
```python
embeddings = model.encode(texts, batch_size=32)  # Thay vì 64
```

### ❌ Lỗi: `UnicodeEncodeError`
**Giải pháp:** Đã xử lý trong code, đảm bảo chạy trong WSL2.

> **Chi tiết:** Xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Next Steps

- 📖 Đọc [CODE_GUIDE.md](CODE_GUIDE.md) để hiểu code
- 🔧 Đọc [INSTALL.md](INSTALL.md) để cài đặt chi tiết
- 🐛 Đọc [TROUBLESHOOTING.md](TROUBLESHOOTING.md) nếu gặp lỗi
- 📊 Xem [PROJECT_FINAL.md](PROJECT_FINAL.md) để biết kết quả

---

**Thời gian hoàn thành:** ~15 phút  
**Tình trạng:** Production Ready ✅
