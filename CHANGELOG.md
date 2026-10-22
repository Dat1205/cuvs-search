# Nhật ký Thay đổi (Changelog)

## [2026-10-22 20:10] - 🎉 Dự án Hoàn thành 100%

### ✅ Giai đoạn 5: Benchmark & Testing
- **Qualitative testing:** 9 query types (keyword, semantic, mixed)
- **Latency benchmark:** 100 queries với statistical analysis
- **GPU profiling:** CUDA Events cho timing chính xác
- **Throughput:** 110 queries/second

### 📊 Performance Results
| Metric | GPU CAGRA | Hybrid RRF |
|--------|-----------|------------|
| Average | **1.64 ms** | 9.09 ms |
| P95 | 2.15 ms | 14.29 ms |
| P99 | 2.37 ms | 15.31 ms |

### 🎯 NFR Verification
- **Target:** GPU search < 10ms
- **Achieved:** 1.64ms ⚡
- **Status:** **PASS** (6x better!)

### 🏆 Project Complete
- All 5 phases completed
- cuVS CAGRA requirement met ✅
- Performance targets exceeded ✅
- Production ready ✅

---

## [2026-10-22 20:02] - Giai đoạn 4 Hoàn thành

### ✅ Đã thêm
- **HybridSearchEngine class** với đầy đủ chức năng
- `keyword_search()` - BM25 keyword search
- `semantic_search()` - cuVS CAGRA vector search
- `hybrid_search()` - RRF fusion algorithm
- Query preprocessing & tokenization
- Result formatting với metadata

### 🎯 Demo Results
Đã test thành công với 3 loại query:
1. **"stock market crash"** → Business articles
2. **"football championship"** → Sports articles  
3. **"new technology innovation"** → Sci/Tech articles

### 🔧 RRF Implementation
- **Formula:** `RRF_Score(d) = Σ 1/(k + rank(d))`
- **k parameter:** 60 (default, configurable)
- **Strategy:** Lấy top_k×2 từ mỗi nhánh
- **Fusion quality:** Kết quả từ cả 2 sources có điểm cao nhất ✅

### 📊 Performance
- Load time: ~2 seconds (all indexes)
- Query latency: <100ms (includes encoding + search + fusion)
- GPU memory: Efficient, <2GB

---

## [2026-10-22 19:53] - Giai đoạn 3 Hoàn thành với cuVS CAGRA

### ✅ Đã thêm
- **cuVS CAGRA GPU Index** (8.55MB) - NVIDIA RAPIDS
- Môi trường WSL2 với conda: cuVS 24.10 + CuPy + CUDA 12.0
- Dense Embeddings với GPU acceleration (all-MiniLM-L6-v2)
- File `artifacts/cagra_index.bin` - Graph-based ANN index

### 🚀 Hiệu năng GPU
- **Encoding embeddings:** 3s trên RTX 5060 (vs 20s CPU)
- **CAGRA build:** 2-3s
- **Search latency:** <5ms (đạt yêu cầu NFR)
- **GPU:** NVIDIA GeForce RTX 5060 Laptop (8GB VRAM)

### 🔧 Kỹ thuật
- Algorithm: NN-Descent graph construction
- Metric: Inner Product (normalized embeddings)
- Backend: cuVS CAGRA (bắt buộc theo yêu cầu)
- Environment: WSL2 Ubuntu + Miniconda

### 📝 Thay đổi
- Thay thế FAISS CPU bằng cuVS CAGRA GPU
- File size tăng: 7.32MB (FAISS) → 8.55MB (CAGRA)
- Performance cải thiện: 10-50ms → <5ms

---

## [2026-10-22 19:37] - Giai đoạn 3 Thử nghiệm FAISS (Đã thay thế)

### ✅ Đã thêm
- Dense Embeddings với all-MiniLM-L6-v2 (5,000 × 384 dim)
- FAISS CPU Index (IndexFlatIP) cho semantic search
- File `artifacts/embeddings.npy` (7.32MB)
- File `artifacts/faiss_index.bin` (7.32MB)

### 🔧 Cải tiến
- Script `2_build_index.py` tự động fallback 3-tier:
  1. cuVS CAGRA (GPU) → không có
  2. FAISS GPU → không có
  3. FAISS CPU → ✅ Sử dụng
- Encoding embeddings thành công trên CPU (~20s)
- Inner product metric tương đương Cosine với normalized vectors

### 📊 Kết quả
- **BM25 Index:** 1.84 MB
- **Embeddings:** 7.32 MB (5,000 vectors × 384 float32)
- **FAISS Index:** 7.32 MB (brute-force exact search)
- **Tổng artifacts:** 19.31 MB

---

## [2026-10-22 16:25] - Giai đoạn 3 Bắt đầu

### ✅ Đã thêm
- BM25 Index được build thành công trên CPU
- File `artifacts/bm25_model.pkl` (1.9MB) chứa BM25Okapi model
- Keyword search đã sẵn sàng sử dụng

### ⚠️ Hạn chế
- **CAGRA Index chưa build:** Yêu cầu môi trường Linux/WSL2 + cuVS + NVIDIA GPU
- Hiện tại chỉ có BM25 keyword search, chưa có semantic search
- Để build đầy đủ cần chuyển sang WSL2 và cài đặt:
  ```bash
  conda install -c rapidsai -c conda-forge -c nvidia cuvs=24.10 cupy cuda-version=12.0
  ```

### 📝 Đã cập nhật
- `src/2_build_index.py` - Thêm xử lý encoding UTF-8
- `STATUS.md` - Cập nhật trạng thái giai đoạn 3
- `README.md` - Cập nhật bảng tiến độ

### 🎯 Kế hoạch tiếp theo
**Lựa chọn 1:** Hoàn thành CAGRA index trên WSL2 + GPU
**Lựa chọn 2:** Tiếp tục giai đoạn 4 với BM25-only mode (không cần GPU)

---

## [2026-10-22 15:58] - Giai đoạn 2 Hoàn thành

### ✅ Đã thêm
- Thu thập 5,000 mẫu từ AG News dataset (fancyzhx/ag_news)
- Tiền xử lý văn bản: lowercase, loại bỏ dấu câu, tokenization
- File `artifacts/corpus.pkl` (2.9MB) chứa corpus và tokenized_corpus
- Thống kê: 41.0 tokens trung bình/văn bản

### 🔧 Đã sửa
- **Lỗi encoding UTF-8:** Thêm wrapper cho sys.stdout/stderr để hỗ trợ ký tự tiếng Việt trên Windows console
  ```python
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```

- **Lỗi HfUriError:** Dataset đã chuyển namespace từ `ag_news` sang `fancyzhx/ag_news`
  ```python
  dataset = load_dataset("fancyzhx/ag_news", split="train[:5000]")
  ```

### 📝 Đã cập nhật
- `src/1_data_prep.py` - Thêm xử lý encoding và fallback cho dataset
- `STATUS.md` - Cập nhật trạng thái giai đoạn 2 hoàn thành
- `README.md` - Thêm bảng tiến độ và kết quả đạt được

---

## [2026-10-22] - Giai đoạn 1 Hoàn thành

### ✅ Đã thêm
- Cấu trúc thư mục dự án: `artifacts/`, `src/`
- File cấu hình: `requirements.txt`, `setup_env.sh`, `.gitignore`
- Mã nguồn đầy đủ cho 4 giai đoạn:
  - `1_data_prep.py` - Thu thập dữ liệu
  - `2_build_index.py` - Xây dựng index
  - `3_search_engine.py` - Search engine với RRF
  - `4_benchmark.py` - Kiểm thử và benchmark
- Tài liệu: `README.md`, `STATUS.md`

---

## Tiếp theo

### Giai đoạn 3: Xây dựng Chỉ mục (BM25 + CAGRA)
**Yêu cầu:**
- Môi trường Linux/WSL2
- NVIDIA GPU với CUDA 12.0
- Môi trường conda với cuVS 24.10

**Công việc:**
- Build BM25 index từ tokenized corpus
- Generate embeddings với Sentence Transformers (all-MiniLM-L6-v2)
- Build CAGRA index trên GPU
- Lưu các index vào `artifacts/`

**Ước tính:** 10-15 phút (phụ thuộc GPU)
