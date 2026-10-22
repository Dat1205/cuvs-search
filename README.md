# Hệ thống Tìm Kiếm Lai (Hybrid Search System)

Hệ thống tìm kiếm kết hợp cuVS (GPU-accelerated vector search) và BM25 (keyword search) sử dụng thuật toán Reciprocal Rank Fusion.

## 📊 Tiến độ triển khai

| Giai đoạn | Trạng thái | Ngày hoàn thành |
|-----------|-----------|-----------------|
| 1. Thiết lập môi trường & Cấu trúc | ✅ Hoàn thành | 2026-10-22 |
| 2. Thu thập & Tiền xử lý dữ liệu | ✅ Hoàn thành | 2026-10-22 |
| 3. Xây dựng Chỉ mục (BM25 + CAGRA) | ✅ Hoàn thành | 2026-10-22 |
| 4. Xây dựng Search Engine (RRF) | ✅ Hoàn thành | 2026-10-22 |
| 5. Kiểm thử & Benchmark | ✅ Hoàn thành | 2026-10-22 |

**🎉 DỰ ÁN HOÀN THÀNH 100%!**

**Đã hoàn thành:**
- ✅ Tải 5,000 mẫu từ AG News dataset
- ✅ Tiền xử lý và tokenize văn bản (41.0 tokens/văn bản)
- ✅ Xây dựng BM25 Index (1.84MB)
- ✅ Tạo Dense Embeddings 384-dim (7.32MB)
- ✅ Xây dựng cuVS CAGRA GPU Index (8.55MB) ⚡
- ✅ HybridSearchEngine với RRF fusion
- ✅ Performance benchmark & testing

**Performance Achieved:**
- GPU search latency: **1.64ms** (target: <10ms) ⚡
- Hybrid search: 9.09ms average
- Throughput: **110 queries/second**
- NFR Status: **PASS** ✅

**Backend:** cuVS CAGRA (NVIDIA RAPIDS)
- GPU: RTX 5060 Laptop (8GB VRAM)
- CUDA: 12.0
- Algorithm: NN-Descent graph-based ANN

**Project Status:** ✅ PRODUCTION READY

> **Chi tiết:** Xem `STATUS.md` để theo dõi tiến độ chi tiết và các vấn đề đã giải quyết.

## 📖 Tài liệu

| Tài liệu | Mô tả | Thời gian đọc |
|----------|-------|---------------|
| [QUICKSTART.md](QUICKSTART.md) | Chạy dự án trong 15 phút | ⏱️ 5 phút |
| [INSTALL.md](INSTALL.md) | Cài đặt đầy đủ từ máy mới | ⏱️ 15 phút |
| [CODE_GUIDE.md](CODE_GUIDE.md) | Giải thích code chi tiết | ⏱️ 30 phút |
| [API_REFERENCE.md](API_REFERENCE.md) | Tài liệu API đầy đủ | ⏱️ 20 phút |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Xử lý lỗi thường gặp | ⏱️ Khi cần |

> **Bắt đầu từ đâu?**
> - 🆕 Máy mới chưa cài đặt gì → [INSTALL.md](INSTALL.md)
> - ⚡ Đã có môi trường → [QUICKSTART.md](QUICKSTART.md)
> - 🔧 Gặp lỗi → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
> - 💻 Muốn hiểu code → [CODE_GUIDE.md](CODE_GUIDE.md)
> - 📚 Tích hợp vào app → [API_REFERENCE.md](API_REFERENCE.md)

## Yêu cầu hệ thống

- Windows 10/11 với WSL2
- NVIDIA GPU với CUDA support
- Python 3.10
- CUDA 12.0 hoặc tương thích
- Miniconda hoặc Anaconda
- Visual Studio Code + Extension WSL

> **Lưu ý:** cuVS (RAPIDS) chỉ hỗ trợ Linux. Trên Windows cần sử dụng WSL2 để chạy project.

## Cài đặt nhanh

```bash
# 1. Cài WSL2 (PowerShell Administrator)
wsl --install

# 2. Trong WSL2, cài Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
~/miniconda3/bin/conda init bash
source ~/.bashrc

# 3. Tạo môi trường (hoặc dùng setup_env.sh)
conda create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y
conda activate hybrid_search

# 4. Cài dependencies
pip install -r requirements.txt
```

> **Chi tiết đầy đủ:** Xem [INSTALL.md](INSTALL.md) để cài đặt từng bước có giải thích

## Cấu trúc dự án

```
hybrid_search_project/
├── artifacts/               # Chứa các file index và dữ liệu đã tiền xử lý
│   ├── corpus.pkl           # Văn bản gốc và labels
│   ├── bm25_model.pkl       # Mô hình BM25 đã build
│   ├── embeddings.npy       # Dense vectors (NumPy)
│   └── cagra_index.bin      # File chỉ mục CAGRA của cuVS
├── src/
│   ├── 1_data_prep.py       # Tải và tiền xử lý AG News
│   ├── 2_build_index.py     # Tạo embedding, build & lưu cuVS + BM25
│   ├── 3_search_engine.py   # Class xử lý truy vấn và thuật toán RRF
│   └── 4_benchmark.py       # Chạy thử nghiệm và đo thời gian
└── requirements.txt
```

## Sử dụng

### Pipeline đầy đủ

```bash
# Bước 1: Tải và tiền xử lý dữ liệu
python src/1_data_prep.py

# Bước 2: Xây dựng BM25 và CAGRA indexes
python src/2_build_index.py

# Bước 3: Test tìm kiếm
python src/3_search_engine.py

# Bước 4: Benchmark performance
python src/4_benchmark.py
```

### Sử dụng trong code

```python
from src.search_engine_module import HybridSearchEngine

# Khởi tạo engine
engine = HybridSearchEngine("artifacts")

# Tìm kiếm
results = engine.hybrid_search("stock market crash", top_k=5)

# In kết quả
for i, doc in enumerate(results, 1):
    print(f"{i}. [Score: {doc['rrf_score']:.4f}]")
    print(f"   {doc['text'][:100]}...")
```

> **Chi tiết API:** Xem [API_REFERENCE.md](API_REFERENCE.md)

## Kiểm tra cài đặt

```bash
# Test GPU
nvidia-smi
python -c "import cupy as cp; print('CUDA:', cp.cuda.is_available())"

# Test cuVS
python -c "from cuvs.neighbors import cagra; print('cuVS OK')"

# Chạy full test
python src/4_benchmark.py
```

## Tham chiếu tài liệu kỹ thuật

- [rq.md](../rq.md) - Tài liệu đặc tả yêu cầu (SRS)
- [trien_khai.md](../trien_khai.md) - Kế hoạch triển khai
- [STATUS.md](STATUS.md) - Theo dõi tiến độ chi tiết
- [PROJECT_FINAL.md](PROJECT_FINAL.md) - Báo cáo kết quả cuối cùng

## Giấy phép & Đóng góp

Dự án sử dụng:
- **cuVS (NVIDIA RAPIDS)** - Apache 2.0 License
- **sentence-transformers** - Apache 2.0 License
- **rank-bm25** - Apache 2.0 License
