# 📖 Hướng dẫn Code - Chi tiết từng file

## Tổng quan

Dự án gồm 4 file Python chính, mỗi file tương ứng 1 giai đoạn:

```
src/
├── 1_data_prep.py       → Giai đoạn 2: Thu thập dữ liệu
├── 2_build_index.py     → Giai đoạn 3: Xây dựng indexes
├── 3_search_engine.py   → Giai đoạn 4: Search engine
└── 4_benchmark.py       → Giai đoạn 5: Testing
```

---

## 📄 File 1: `1_data_prep.py`

### Mục đích
Thu thập 5,000 văn bản từ AG News dataset và tiền xử lý cho BM25.

### Các function chính:

#### `preprocess_text(text: str) -> List[str]`
```python
def preprocess_text(text):
    """
    Tiền xử lý văn bản cho keyword search
    - Chuyển chữ thường
    - Loại bỏ dấu câu
    - Tách thành danh sách tokens
    """
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    return tokens
```

**Input:** "Stock Market Crash!"  
**Output:** ['stock', 'market', 'crash']

**Lý do:** BM25 cần tokens riêng lẻ để tính TF-IDF.

#### `main()`
```python
def main():
    # 1. Tải dataset
    dataset = load_dataset("fancyzhx/ag_news", split="train[:5000]")
    
    # 2. Xử lý từng văn bản
    for item in dataset:
        text = item['text']
        label = item['label']
        
        # Lưu gốc
        corpus.append({'id': i, 'text': text, 'label': label})
        
        # Tokenize
        tokens = preprocess_text(text)
        tokenized_corpus.append(tokens)
    
    # 3. Lưu ra file
    with open("artifacts/corpus.pkl", "wb") as f:
        pickle.dump({'corpus': corpus, 'tokenized_corpus': tokenized_corpus}, f)
```

### Output
- `artifacts/corpus.pkl` (2.9MB)
  - `corpus`: List[Dict] - Văn bản gốc + metadata
  - `tokenized_corpus`: List[List[str]] - Tokens cho BM25

---

## 📄 File 2: `2_build_index.py`

### Mục đích
Xây dựng BM25 index (CPU) và CAGRA index (GPU).

### Backend Detection
```python
BACKEND = "cpu"  # default

try:
    import cupy as cp
    from cuvs.neighbors import cagra
    BACKEND = "cuvs"
except ImportError:
    try:
        import faiss
        BACKEND = "faiss_cpu" if faiss.get_num_gpus() == 0 else "faiss_gpu"
    except:
        pass
```

**Logic:** Tự động chọn backend tốt nhất có sẵn.

### BM25 Index
```python
from rank_bm25 import BM25Okapi

# Build index
bm25_model = BM25Okapi(tokenized_corpus)

# Save
with open("artifacts/bm25_model.pkl", "wb") as f:
    pickle.dump(bm25_model, f)
```

**BM25Okapi:** Variant tốt nhất của BM25, tính điểm dựa trên:
- TF (Term Frequency)
- IDF (Inverse Document Frequency)
- Document length normalization

### CAGRA Index (cuVS)
```python
# 1. Load model
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

# 2. Encode
embeddings = model.encode(
    texts,
    normalize_embeddings=True,  # L2 normalize
    show_progress_bar=True,
    convert_to_numpy=True,
    batch_size=64
)

# 3. Chuyển sang GPU
embeddings_gpu = cp.asarray(embeddings, dtype=cp.float32)

# 4. Build CAGRA
index_params = cagra.IndexParams(
    metric="inner_product",        # Cosine similarity với normalized vectors
    build_algo="nn_descent"        # NN-Descent graph construction
)
index = cagra.build(index_params, embeddings_gpu)

# 5. Save
cagra.save("artifacts/cagra_index.bin", index)
```

**CAGRA:** GPU-accelerated Approximate Nearest Neighbor (ANN)
- **Graph-based:** Xây dựng đồ thị kết nối các vectors
- **NN-Descent:** Thuật toán build nhanh, chính xác cao
- **Inner Product:** Với normalized vectors = Cosine Similarity

### Output
- `artifacts/bm25_model.pkl` (1.9MB)
- `artifacts/embeddings.npy` (7.4MB)
- `artifacts/cagra_index.bin` (8.6MB)

---

## 📄 File 3: `3_search_engine.py`

### Mục đích
Class HybridSearchEngine kết hợp BM25 và CAGRA với RRF.

### Class Structure
```python
class HybridSearchEngine:
    def __init__(self, artifacts_dir="artifacts")
    def preprocess_query(self, query: str) -> List[str]
    def keyword_search(self, query: str, top_k: int = 10) -> Dict[int, int]
    def semantic_search(self, query: str, top_k: int = 10) -> Dict[int, int]
    def hybrid_search(self, query: str, top_k: int = 10, rrf_k: int = 60) -> List[Dict]
    def print_results(self, results: List[Dict], query: str)
```

### `__init__` - Load indexes
```python
def __init__(self, artifacts_dir: str = "artifacts"):
    # Load corpus
    with open(self.artifacts_dir / "corpus.pkl", "rb") as f:
        data = pickle.load(f)
    self.corpus = data['corpus']
    
    # Load BM25
    with open(self.artifacts_dir / "bm25_model.pkl", "rb") as f:
        self.bm25_model = pickle.load(f)
    
    # Load CAGRA
    if CUVS_AVAILABLE:
        self.cagra_index = cagra.load("artifacts/cagra_index.bin")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
```

**Lý do load lại model:** Để encode query mới.

### `keyword_search` - BM25
```python
def keyword_search(self, query: str, top_k: int = 10) -> Dict[int, int]:
    # Tokenize query giống corpus
    tokens = self.preprocess_query(query)
    
    # Tính điểm BM25
    scores = self.bm25_model.get_scores(tokens)
    
    # Lấy top_k, chỉ lấy score > 0
    scored_docs = [(i, score) for i, score in enumerate(scores) if score > 0]
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    scored_docs = scored_docs[:top_k]
    
    # Trả về {doc_id: rank}
    return {doc_id: rank + 1 for rank, (doc_id, score) in enumerate(scored_docs)}
```

**Return format:** `{doc_id: rank}` (rank từ 1)  
**Lọc score > 0:** Tránh nhiễu khi gộp với semantic results

### `semantic_search` - CAGRA
```python
def semantic_search(self, query: str, top_k: int = 10) -> Dict[int, int]:
    # 1. Encode query
    query_embedding = self.sentence_model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    
    # 2. Chuyển sang GPU
    query_embedding_gpu = cp.asarray(
        query_embedding.reshape(1, -1), 
        dtype=cp.float32
    )
    
    # 3. Search
    search_params = cagra.SearchParams()
    distances, neighbors = cagra.search(
        search_params,
        self.cagra_index,
        query_embedding_gpu,
        top_k
    )
    
    # 4. Convert về CPU
    neighbors = cp.asnumpy(neighbors)[0]
    
    # 5. Trả về {doc_id: rank}
    return {int(doc_id): rank + 1 for rank, doc_id in enumerate(neighbors)}
```

**CAGRA search:** Graph traversal trên GPU, rất nhanh (~1.6ms)

### `hybrid_search` - RRF Fusion
```python
def hybrid_search(self, query: str, top_k: int = 10, rrf_k: int = 60) -> List[Dict]:
    # 1. Lấy kết quả từ cả 2 nhánh
    search_k = top_k * 2  # Lấy nhiều để tăng độ phủ
    
    keyword_results = self.keyword_search(query, search_k)
    semantic_results = self.semantic_search(query, search_k)
    
    # 2. RRF Formula
    rrf_scores = {}
    all_doc_ids = set(keyword_results.keys()) | set(semantic_results.keys())
    
    for doc_id in all_doc_ids:
        score = 0.0
        
        # Điểm từ keyword
        if doc_id in keyword_results:
            score += 1.0 / (rrf_k + keyword_results[doc_id])
        
        # Điểm từ semantic
        if doc_id in semantic_results:
            score += 1.0 / (rrf_k + semantic_results[doc_id])
        
        rrf_scores[doc_id] = score
    
    # 3. Sắp xếp
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_docs = sorted_docs[:top_k]
    
    # 4. Ánh xạ với corpus
    results = []
    for doc_id, rrf_score in sorted_docs:
        doc = self.corpus[doc_id]
        results.append({
            'id': doc_id,
            'text': doc['text'],
            'label': doc['label'],
            'rrf_score': rrf_score,
            'in_keyword': doc_id in keyword_results,
            'in_semantic': doc_id in semantic_results
        })
    
    return results
```

**RRF Formula:**
```
RRF_Score(d) = Σ 1/(k + rank_method(d))
               method ∈ {keyword, semantic}
```

**Tại sao RRF tốt:**
- Không cần normalize scores
- Không cần tune weights
- Tự động cân bằng 2 sources
- Results từ cả 2 sources được ưu tiên

**Tại sao search_k = top_k × 2:**
- Tăng recall trước khi fusion
- Đảm bảo đủ overlap giữa 2 sources

---

## 📄 File 4: `4_benchmark.py`

### Mục đích
Đo latency và test chất lượng.

### Class Structure
```python
class Benchmark:
    def __init__(self, engine: HybridSearchEngine)
    def qualitative_test(self)
    def latency_benchmark(self, num_queries: int = 100, warmup: int = 5)
    def _print_stats(self, name: str, times: List[float])
```

### `qualitative_test` - Test chất lượng
```python
def qualitative_test(self):
    test_queries = {
        "Truy vấn khớp từ khóa đặc thù": [
            "Iraq war",
            "Microsoft Windows"
        ],
        "Truy vấn diễn giải ngữ nghĩa": [
            "financial crisis and economy",
            "sports competition results"
        ],
        "Truy vấn hỗn hợp": [
            "Apple company stock price",
            "election results politics"
        ]
    }
    
    for category, queries in test_queries.items():
        for query in queries:
            # So sánh 3 methods
            kw_results = self.engine.keyword_search(query, 3)
            sem_results = self.engine.semantic_search(query, 3)
            hybrid_results = self.engine.hybrid_search(query, 5)
```

**Mục đích:** Xác định method nào tốt cho query type nào.

### `latency_benchmark` - Đo thời gian
```python
def latency_benchmark(self, num_queries: int = 100, warmup: int = 5):
    # 1. Warm-up GPU
    for i in range(warmup):
        _ = self.engine.hybrid_search(test_queries[i % len(test_queries)], 10)
    
    # 2. Benchmark từng component
    for i in range(num_queries):
        # Keyword
        start = time.perf_counter()
        _ = self.engine.keyword_search(query, 10)
        end = time.perf_counter()
        kw_times.append((end - start) * 1000)
        
        # Semantic (với CUDA Events)
        start_event = cp.cuda.Event()
        end_event = cp.cuda.Event()
        
        start_event.record()
        # ... CAGRA search ...
        end_event.record()
        end_event.synchronize()
        
        gpu_time = cp.cuda.get_elapsed_time(start_event, end_event)
```

**CUDA Events:** Đo chính xác thời gian GPU, loại bỏ overhead CPU.

**Metrics:**
- **Average:** Trung bình
- **Median:** Giá trị giữa
- **P95:** 95% queries nhanh hơn
- **P99:** 99% queries nhanh hơn

---

## 🔧 Kỹ thuật quan trọng

### 1. Normalized Embeddings
```python
embeddings = model.encode(texts, normalize_embeddings=True)
```
**Lý do:** Với L2-normalized vectors:
- `inner_product(A, B) = cosine_similarity(A, B)`
- Tính nhanh hơn cosine (không cần chia)
- CAGRA yêu cầu normalized cho metric="inner_product"

### 2. CuPy Arrays
```python
embeddings_gpu = cp.asarray(embeddings, dtype=cp.float32)
```
**Lý do:** cuVS yêu cầu GPU arrays, không phải NumPy.

### 3. Error Handling
```python
try:
    import cupy as cp
    CUVS_AVAILABLE = True
except ImportError:
    CUVS_AVAILABLE = False
    # Fallback to CPU
```
**Lý do:** Code chạy được cả khi không có GPU.

### 4. UTF-8 Encoding (Windows)
```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
**Lý do:** Windows console mặc định cp1252, không hiển thị tiếng Việt.

---

## 📊 Data Flow

```
Query: "stock market crash"
         │
         ├─────────────────┬─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   Preprocess          Encode           (Original)
    ["stock",         [0.23, -0.15,       
     "market",         0.41, ...]         
     "crash"]         (384-dim)           
         │                 │                 │
         ▼                 ▼                 ▼
    BM25 Search      CAGRA Search      (Metadata)
    {45: 1,          {12: 1,
     78: 2,           45: 2,
     12: 3}           89: 3}
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                           ▼
                      RRF Fusion
                  {45: 0.0325,  ← Both sources!
                   12: 0.0311,  ← Both sources!
                   78: 0.0164}  ← Keyword only
                           │
                           ▼
                    Top-K Results
                  [Doc 45, Doc 12, Doc 78]
                           │
                           ▼
                   Map to Corpus
              [{'text': '...', 'label': 2, ...}]
```

---

## 🎓 Best Practices trong code

### 1. Type Hints
```python
def keyword_search(self, query: str, top_k: int = 10) -> Dict[int, int]:
```

### 2. Docstrings
```python
def hybrid_search(self, query: str, top_k: int = 10, rrf_k: int = 60) -> List[Dict]:
    """
    Tìm kiếm lai sử dụng Reciprocal Rank Fusion (RRF)
    
    Args:
        query: Câu truy vấn
        top_k: Số kết quả trả về
        rrf_k: Tham số k trong công thức RRF (mặc định 60)
    
    Returns:
        List các văn bản kèm thông tin
    """
```

### 3. Single Responsibility
Mỗi method làm 1 việc duy nhất, dễ test và maintain.

### 4. Configurable Parameters
```python
rrf_k: int = 60  # Có thể tune
```

### 5. Progress Bars
```python
model.encode(texts, show_progress_bar=True)
```

---

## 🐛 Common Issues

### Issue 1: cuVS import fails
**Nguyên nhân:** Chạy trên Windows native  
**Giải pháp:** Dùng WSL2

### Issue 2: CUDA out of memory
**Nguyên nhân:** Batch size quá lớn  
**Giải pháp:** Giảm `batch_size` trong encode

### Issue 3: UnicodeEncodeError
**Nguyên nhân:** Windows console  
**Giải pháp:** UTF-8 wrapper đã có trong code

---

**File này:** Giải thích chi tiết code  
**File tiếp theo:** [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn chạy nhanh
