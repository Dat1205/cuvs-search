# 🐛 Troubleshooting Guide

Tổng hợp các lỗi thường gặp và cách khắc phục.

---

## 📋 Mục lục

1. [Lỗi cài đặt môi trường](#1-lỗi-cài-đặt-môi-trường)
2. [Lỗi GPU / CUDA](#2-lỗi-gpu--cuda)
3. [Lỗi khi chạy code](#3-lỗi-khi-chạy-code)
4. [Lỗi về bộ nhớ](#4-lỗi-về-bộ-nhớ)
5. [Lỗi encoding / Unicode](#5-lỗi-encoding--unicode)
6. [Lỗi performance](#6-lỗi-performance)

---

## 1. Lỗi cài đặt môi trường

### ❌ Error: `ModuleNotFoundError: No module named 'cupy'`

**Nguyên nhân:** CuPy chưa được cài hoặc môi trường không active.

**Giải pháp:**
```bash
# Kiểm tra môi trường hiện tại
conda info --envs

# Kích hoạt môi trường
conda activate hybrid_search

# Cài lại CuPy nếu cần
conda install -c conda-forge cupy cuda-version=12.0 -y
```

**Verify:**
```bash
python -c "import cupy as cp; print(cp.__version__)"
```

---

### ❌ Error: `ImportError: libcuvs.so: cannot open shared object file`

**Nguyên nhân:** cuVS không được cài đúng hoặc thiếu dependencies.

**Giải pháp 1: Cài lại cuVS**
```bash
conda activate hybrid_search
conda install -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 libcuvs cuda-version=12.0 --override-channels -y
```

**Giải pháp 2: Kiểm tra LD_LIBRARY_PATH**
```bash
echo $LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
```

**Giải pháp 3: Tạo lại môi trường từ đầu**
```bash
conda deactivate
conda env remove -n hybrid_search
bash setup_env.sh
```

---

### ❌ Error: Terms of Service / Anaconda channels blocked

**Lỗi đầy đủ:**
```
CondaError: Anaconda.org authentication required by your organization
```

**Nguyên nhân:** Conda cố tải từ anaconda.com (bị chặn).

**Giải pháp:** Dùng `--override-channels` để bỏ qua:
```bash
conda create -n hybrid_search python=3.10 \
    -c rapidsai -c nvidia -c conda-forge \
    cuvs=24.10 cupy cuda-version=12.0 \
    --override-channels -y
```

---

### ❌ Error: `Solving environment: failed with initial frozen solve`

**Nguyên nhân:** Conflict dependencies.

**Giải pháp 1: Cài từng bước**
```bash
# Bước 1: Tạo base environment
conda create -n hybrid_search python=3.10 -y

# Bước 2: Kích hoạt
conda activate hybrid_search

# Bước 3: Cài cuVS + CuPy
conda install -c rapidsai -c nvidia -c conda-forge \
    cuvs=24.10 cupy cuda-version=12.0 -y

# Bước 4: Cài Python packages
pip install sentence-transformers rank-bm25 datasets
```

**Giải pháp 2: Dùng mamba (nhanh hơn conda)**
```bash
conda install mamba -n base -c conda-forge
mamba create -n hybrid_search -c rapidsai -c nvidia -c conda-forge \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y
```

---

## 2. Lỗi GPU / CUDA

### ❌ Error: `nvidia-smi: command not found`

**Nguyên nhân:** NVIDIA driver chưa cài hoặc không hoạt động trong WSL2.

**Giải pháp:**
1. **Trên Windows:** Cài driver NVIDIA mới nhất
   - Tải từ: https://www.nvidia.com/Download/index.aspx
   - Chọn GPU model → Download → Install
   
2. **Khởi động lại máy**

3. **Kiểm tra trong WSL2:**
   ```bash
   wsl
   nvidia-smi
   ```

**Nếu vẫn lỗi:** Cập nhật WSL kernel:
```powershell
# Trên PowerShell (Windows)
wsl --update
wsl --shutdown
wsl
```

---

### ❌ Error: `CUDA not available` hoặc `cp.cuda.is_available() = False`

**Nguyên nhân:** CuPy không nhận diện được CUDA.

**Giải pháp 1: Kiểm tra CUDA version mismatch**
```bash
# Kiểm tra CUDA version của driver
nvidia-smi  # Xem dòng "CUDA Version: 12.x"

# Kiểm tra CuPy được build cho CUDA version nào
python -c "import cupy; print(cupy.cuda.runtime.runtimeGetVersion())"

# Nếu mismatch, cài lại CuPy cho đúng version
conda install -c conda-forge cupy cuda-version=12.0 -y  # Thay 12.0 bằng version đúng
```

**Giải pháp 2: Verify GPU accessible từ Python**
```python
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout)
```

**Giải pháp 3: Reinstall CuPy từ scratch**
```bash
pip uninstall cupy-cuda12x -y  # Thay 12x bằng version của bạn
conda install -c conda-forge cupy cuda-version=12.0 -y
```

---

### ❌ Error: `CUDA out of memory`

**Lỗi đầy đủ:**
```
cupy.cuda.memory.OutOfMemoryError: Out of memory allocating X bytes
```

**Nguyên nhân:** GPU RAM không đủ.

**Giải pháp 1: Giảm batch_size trong encoding**

Sửa trong `src/2_build_index.py`:
```python
# Trước (line ~45)
embeddings = model.encode(texts, batch_size=64, ...)

# Sau
embeddings = model.encode(texts, batch_size=32, ...)  # Hoặc 16
```

**Giải pháp 2: Giảm số lượng samples**

Sửa trong `src/1_data_prep.py`:
```python
# Trước
dataset = load_dataset("ag_news", split="train[:5000]")

# Sau
dataset = load_dataset("ag_news", split="train[:2000]")  # Giảm xuống 2000
```

**Giải pháp 3: Clear GPU cache**
```python
import cupy as cp
cp.get_default_memory_pool().free_all_blocks()
```

**Giải pháp 4: Monitor GPU memory**
```bash
# Chạy trong terminal thứ 2
watch -n 1 nvidia-smi
```

---

### ❌ Error: `cupy.cuda.compiler.CompileException`

**Nguyên nhân:** CuPy không tìm thấy NVCC (CUDA compiler).

**Giải pháp:** Cài lại CuPy với precompiled binaries:
```bash
pip uninstall cupy -y
conda install -c conda-forge cupy cuda-version=12.0 -y
```

> **Lưu ý:** KHÔNG cần cài CUDA Toolkit riêng trong WSL2. Driver Windows đã đủ.

---

## 3. Lỗi khi chạy code

### ❌ Error: `FileNotFoundError: [Errno 2] No such file or directory: 'artifacts/corpus.pkl'`

**Nguyên nhân:** Chưa chạy bước data prep hoặc chạy sai thư mục.

**Giải pháp:**
```bash
# Kiểm tra thư mục hiện tại
pwd

# Chạy lại data prep
python src/1_data_prep.py

# Kiểm tra file đã tạo
ls -lh artifacts/
```

**Thứ tự chạy đúng:**
```bash
python src/1_data_prep.py      # Tạo corpus.pkl
python src/2_build_index.py    # Tạo indexes (cần corpus.pkl)
python src/3_search_engine.py  # Search (cần indexes)
python src/4_benchmark.py      # Benchmark (cần indexes)
```

---

### ❌ Error: `pickle.UnpicklingError: invalid load key`

**Nguyên nhân:** File artifacts bị corrupt.

**Giải pháp:**
```bash
# Xóa artifacts cũ
rm -rf artifacts/*.pkl artifacts/*.bin artifacts/*.npy

# Rebuild từ đầu
python src/1_data_prep.py
python src/2_build_index.py
```

---

### ❌ Error: `KeyError: 'text'` khi load dataset

**Nguyên nhân:** Dataset format khác hoặc tải sai.

**Giải pháp:**

Sửa trong `src/1_data_prep.py`:
```python
# Thử với namespace đầy đủ
try:
    dataset = load_dataset("fancyzhx/ag_news", split="train[:5000]")
except:
    # Fallback
    dataset = load_dataset("ag_news", split="train[:5000]", trust_remote_code=True)
```

**Hoặc kiểm tra fields:**
```python
dataset = load_dataset("ag_news", split="train[:100]")
print(dataset[0])  # In ra xem có field nào
```

---

## 4. Lỗi về bộ nhớ

### ❌ Error: `MemoryError` (RAM)

**Nguyên nhân:** Hết RAM khi encode.

**Giải pháp 1: Process theo batch nhỏ hơn**

Sửa `src/2_build_index.py`:
```python
# Encode theo batch
batch_size = 1000
all_embeddings = []

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    embeddings = model.encode(batch, normalize_embeddings=True)
    all_embeddings.append(embeddings)
    
embeddings = np.vstack(all_embeddings)
```

**Giải pháp 2: Tăng WSL2 memory limit**

Tạo file `.wslconfig` trong `C:\Users\<YourName>\`:
```ini
[wsl2]
memory=8GB
processors=4
```

Restart WSL:
```powershell
wsl --shutdown
wsl
```

---

### ❌ Error: `OSError: [Errno 28] No space left on device`

**Nguyên nhân:** Hết dung lượng ổ đĩa.

**Giải pháp 1: Xóa conda cache**
```bash
conda clean --all -y
```

**Giải pháp 2: Xóa pip cache**
```bash
pip cache purge
```

**Giải pháp 3: Kiểm tra dung lượng**
```bash
df -h
du -sh ~/miniconda3/envs/*
```

---

## 5. Lỗi encoding / Unicode

### ❌ Error: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Nguyên nhân:** Windows console không hỗ trợ UTF-8.

**Giải pháp:** Đã xử lý trong code với:
```python
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

**Nếu vẫn lỗi:** Chạy trong WSL2 (Linux terminal) thay vì cmd/PowerShell.

---

### ❌ Tiếng Việt hiển thị lỗi trong output

**Giải pháp:**
```bash
# Set locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Thêm vào ~/.bashrc để persist
echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=en_US.UTF-8' >> ~/.bashrc
```

---

## 6. Lỗi performance

### ❌ Search rất chậm (> 100ms)

**Nguyên nhân 1: GPU chưa warm-up**

**Giải pháp:** Chạy vài query đầu để warm-up:
```python
for _ in range(5):
    engine.hybrid_search("test query", 10)
```

**Nguyên nhân 2: BM25 quá chậm (corpus lớn)**

**Giải pháp:** Cache BM25 results:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def keyword_search_cached(self, query: str, top_k: int):
    return self.keyword_search(query, top_k)
```

**Nguyên nhân 3: Encode query quá chậm**

**Giải pháp:** Giữ model trên GPU (đã implement):
```python
# model.to('cuda') đã gọi trong __init__
self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
```

---

### ❌ CAGRA search không nhanh hơn CPU

**Nguyên nhân:** Dataset quá nhỏ (< 10K), overhead GPU > speedup.

**Giải pháp:**
- Với dataset nhỏ: Dùng brute-force search thay CAGRA
- Với dataset lớn (>100K): CAGRA mới thật sự nhanh hơn

**Test với brute-force:**
```python
from cuvs.neighbors import brute_force

index = brute_force.build(embeddings_gpu)
distances, neighbors = brute_force.search(params, index, query_gpu, k)
```

---

## 7. Lỗi khác

### ❌ Error: `RuntimeError: cuBLAS error`

**Giải pháp:**
```bash
# Restart Python kernel
# Hoặc clear GPU cache
python -c "import cupy; cupy.get_default_memory_pool().free_all_blocks()"
```

---

### ❌ VSCode không nhận conda environment

**Giải pháp:**
1. Nhấn `F1` → `Python: Select Interpreter`
2. Nếu không thấy, chọn **Enter interpreter path...**
3. Dán: `~/miniconda3/envs/hybrid_search/bin/python`

---

### ❌ Git commit có lỗi line endings (CRLF vs LF)

**Giải pháp:**
```bash
# Cấu hình Git trong WSL2
git config --global core.autocrlf input
git config --global core.eol lf
```

---

## 📞 Liên hệ hỗ trợ

Nếu gặp lỗi không có trong danh sách:

1. **Check logs chi tiết:**
   ```bash
   python src/2_build_index.py 2>&1 | tee build.log
   ```

2. **Mô tả đầy đủ:**
   - Lỗi gì? (full traceback)
   - Đang chạy file nào?
   - Environment info:
     ```bash
     python --version
     nvidia-smi
     conda list cupy cuvs
     ```

3. **Tạo issue** trên GitHub repo (nếu có).

---

**Cập nhật:** 2026-10-22
