# 📚 API Reference

Tài liệu tham khảo API đầy đủ cho module `HybridSearchEngine`.

---

## Module: `search_engine_module`

### Class: `HybridSearchEngine`

Class chính để thực hiện tìm kiếm lai kết hợp BM25 và CAGRA với thuật toán RRF.

#### Constructor

```python
HybridSearchEngine(artifacts_dir: str = "artifacts")
```

**Tham số:**
- `artifacts_dir` (str, optional): Đường dẫn đến thư mục chứa các file index. Mặc định: `"artifacts"`

**Raises:**
- `FileNotFoundError`: Nếu thư mục artifacts hoặc các file index không tồn tại
- `ImportError`: Nếu cuVS không có sẵn (fallback sang CPU mode)

**Example:**
```python
from src.search_engine_module import HybridSearchEngine

# Khởi tạo với thư mục mặc định
engine = HybridSearchEngine()

# Hoặc chỉ định thư mục khác
engine = HybridSearchEngine("path/to/artifacts")
```

---

### Methods

#### `preprocess_query`

```python
preprocess_query(query: str) -> List[str]
```

Tiền xử lý query theo cách giống corpus (lowercase + tokenize).

**Tham số:**
- `query` (str): Câu truy vấn cần xử lý

**Returns:**
- `List[str]`: Danh sách tokens

**Example:**
```python
tokens = engine.preprocess_query("Stock Market Crash!")
print(tokens)  # ['stock', 'market', 'crash']
```

**Internal use:** Được gọi tự động bởi `keyword_search()`.

---

#### `keyword_search`

```python
keyword_search(query: str, top_k: int = 10) -> Dict[int, int]
```

Tìm kiếm dựa trên từ khóa sử dụng BM25.

**Tham số:**
- `query` (str): Câu truy vấn
- `top_k` (int, optional): Số kết quả trả về. Mặc định: 10

**Returns:**
- `Dict[int, int]`: Dictionary `{doc_id: rank}` với rank bắt đầu từ 1
  - Chỉ trả về documents có BM25 score > 0

**Example:**
```python
results = engine.keyword_search("Iraq war", top_k=5)
print(results)  # {123: 1, 456: 2, 789: 3, ...}

# Lấy document ID có rank cao nhất
top_doc_id = min(results, key=results.get)
```

**Performance:**
- Thời gian: ~5-10ms trên CPU cho 5,000 documents
- Tốt cho: Exact keyword matching, proper nouns, acronyms

---

#### `semantic_search`

```python
semantic_search(query: str, top_k: int = 10) -> Dict[int, int]
```

Tìm kiếm dựa trên ngữ nghĩa sử dụng CAGRA vector search trên GPU.

**Tham số:**
- `query` (str): Câu truy vấn
- `top_k` (int, optional): Số kết quả trả về. Mặc định: 10

**Returns:**
- `Dict[int, int]`: Dictionary `{doc_id: rank}` với rank bắt đầu từ 1

**Example:**
```python
results = engine.semantic_search("financial crisis", top_k=5)
print(results)  # {42: 1, 156: 2, 893: 3, ...}
```

**Performance:**
- Thời gian: ~1.6ms trên GPU (RTX 5060)
- Tốt cho: Semantic similarity, paraphrases, conceptual queries

**Note:** 
- Nếu cuVS không có sẵn, sẽ fallback về CPU brute-force search (~50ms)
- Query được encode và normalize trước khi search

---

#### `hybrid_search`

```python
hybrid_search(
    query: str, 
    top_k: int = 10, 
    rrf_k: int = 60
) -> List[Dict[str, Any]]
```

Tìm kiếm lai kết hợp keyword và semantic search với RRF fusion.

**Tham số:**
- `query` (str): Câu truy vấn
- `top_k` (int, optional): Số kết quả trả về. Mặc định: 10
- `rrf_k` (int, optional): Tham số k trong công thức RRF. Mặc định: 60

**Returns:**
- `List[Dict]`: Danh sách documents được sắp xếp theo RRF score giảm dần

**Format của mỗi document:**
```python
{
    'id': int,              # Document ID
    'text': str,            # Nội dung văn bản
    'label': int,           # Category label (0-3)
    'rrf_score': float,     # RRF fusion score
    'in_keyword': bool,     # Có trong kết quả keyword không
    'in_semantic': bool     # Có trong kết quả semantic không
}
```

**Example:**
```python
results = engine.hybrid_search("Apple stock price", top_k=5, rrf_k=60)

for i, doc in enumerate(results, 1):
    print(f"{i}. [RRF: {doc['rrf_score']:.4f}]")
    print(f"   Text: {doc['text'][:100]}...")
    print(f"   Sources: KW={doc['in_keyword']}, SEM={doc['in_semantic']}")
    print()
```

**Output:**
```
1. [RRF: 0.0327]
   Text: Apple Inc. shares rose 5% after announcing record quarterly earnings...
   Sources: KW=True, SEM=True

2. [RRF: 0.0298]
   Text: Technology stocks surge as investors bet on growth...
   Sources: KW=False, SEM=True
...
```

**RRF Formula:**
```
RRF_Score(d) = Σ [ 1 / (k + rank_method(d)) ]
               method ∈ {keyword, semantic}
```

**Performance:**
- Thời gian: ~9ms average (GPU)
- Tốt cho: Balanced search, handling diverse query types

**Tuning `rrf_k`:**
- `k = 60`: Mặc định, cân bằng tốt
- `k < 60`: Ưu tiên documents ở top ranks
- `k > 60`: Làm phẳng sự khác biệt giữa ranks

---

#### `print_results`

```python
print_results(results: List[Dict], query: str) -> None
```

In kết quả tìm kiếm ra console với format đẹp.

**Tham số:**
- `results` (List[Dict]): Danh sách kết quả từ `hybrid_search()`
- `query` (str): Query gốc (để hiển thị)

**Example:**
```python
results = engine.hybrid_search("machine learning", top_k=3)
engine.print_results(results, "machine learning")
```

**Output:**
```
🔍 Query: "machine learning"
📊 Tìm thấy 3 kết quả

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Kết quả #1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 RRF Score: 0.0325
🏷️  Category: Sci/Tech
📝 Text:
    Machine learning algorithms are transforming...
📊 Sources: ✅ Keyword | ✅ Semantic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
```

---

## Attributes

### Public Attributes

#### `corpus`
```python
corpus: List[Dict[str, Any]]
```
Danh sách toàn bộ documents trong index.

**Format:**
```python
[
    {'id': 0, 'text': '...', 'label': 2},
    {'id': 1, 'text': '...', 'label': 0},
    ...
]
```

**Example:**
```python
# Lấy document theo ID
doc = engine.corpus[123]
print(doc['text'])

# Đếm documents theo category
from collections import Counter
labels = [doc['label'] for doc in engine.corpus]
print(Counter(labels))  # {0: 1250, 1: 1250, 2: 1250, 3: 1250}
```

---

#### `bm25_model`
```python
bm25_model: BM25Okapi
```
Mô hình BM25 đã build sẵn.

**Example:**
```python
# Tính BM25 scores cho query
tokens = engine.preprocess_query("apple")
scores = engine.bm25_model.get_scores(tokens)
print(f"Max score: {scores.max()}")
```

---

#### `cagra_index`
```python
cagra_index: cagra.Index (nếu cuVS available)
```
CAGRA index trên GPU.

**Note:** Chỉ có sẵn khi cuVS được import thành công.

---

#### `sentence_model`
```python
sentence_model: SentenceTransformer
```
Model embedding để encode queries.

**Example:**
```python
# Encode custom text
embedding = engine.sentence_model.encode("custom text")
print(embedding.shape)  # (384,)
```

---

## Constants

### `CUVS_AVAILABLE`
```python
CUVS_AVAILABLE: bool
```
Flag cho biết cuVS có sẵn hay không.

**Example:**
```python
from src.search_engine_module import CUVS_AVAILABLE

if CUVS_AVAILABLE:
    print("Using GPU-accelerated search")
else:
    print("Fallback to CPU search")
```

---

### `BACKEND`
```python
BACKEND: str
```
Backend đang sử dụng: `"cuvs"`, `"faiss_gpu"`, `"faiss_cpu"`, hoặc `"cpu"`.

**Example:**
```python
from src.search_engine_module import BACKEND
print(f"Search backend: {BACKEND}")
```

---

## Label Mapping

AG News dataset có 4 categories:

```python
LABEL_NAMES = {
    0: "World",       # Tin tức thế giới
    1: "Sports",      # Thể thao
    2: "Business",    # Kinh doanh
    3: "Sci/Tech"     # Khoa học/Công nghệ
}
```

**Example:**
```python
for doc in results:
    label_name = LABEL_NAMES[doc['label']]
    print(f"{label_name}: {doc['text'][:50]}...")
```

---

## Usage Patterns

### Pattern 1: Simple Search

```python
from src.search_engine_module import HybridSearchEngine

engine = HybridSearchEngine()
results = engine.hybrid_search("your query", top_k=10)

for doc in results:
    print(doc['text'])
```

---

### Pattern 2: Compare Search Methods

```python
query = "climate change"

kw_results = engine.keyword_search(query, 5)
sem_results = engine.semantic_search(query, 5)
hybrid_results = engine.hybrid_search(query, 5)

print(f"Keyword only: {list(kw_results.keys())}")
print(f"Semantic only: {list(sem_results.keys())}")
print(f"Hybrid (RRF): {[d['id'] for d in hybrid_results]}")
```

---

### Pattern 3: Batch Processing

```python
queries = [
    "stock market crash",
    "football championship",
    "artificial intelligence"
]

all_results = []
for query in queries:
    results = engine.hybrid_search(query, top_k=3)
    all_results.append((query, results))

# Process results
for query, results in all_results:
    print(f"\nQuery: {query}")
    print(f"Top result: {results[0]['text'][:100]}")
```

---

### Pattern 4: Filter by Category

```python
results = engine.hybrid_search("technology news", top_k=20)

# Chỉ lấy Sci/Tech (label=3)
tech_results = [r for r in results if r['label'] == 3]

print(f"Found {len(tech_results)} tech articles")
```

---

### Pattern 5: Custom RRF Tuning

```python
query = "Apple iPhone"

# Test different k values
for k in [30, 60, 90]:
    results = engine.hybrid_search(query, top_k=5, rrf_k=k)
    print(f"\nk={k}:")
    for r in results[:3]:
        print(f"  {r['id']}: {r['rrf_score']:.4f}")
```

---

## Performance Benchmarks

### Latency (5,000 documents, RTX 5060 GPU)

| Method | Average | Median | P95 | P99 |
|--------|---------|--------|-----|-----|
| BM25 Keyword | 5.2ms | 4.8ms | 7.1ms | 9.3ms |
| CAGRA Semantic | 1.6ms | 1.5ms | 2.1ms | 2.8ms |
| Hybrid (RRF) | 9.1ms | 8.7ms | 12.4ms | 15.2ms |

### Throughput

- **Hybrid search:** ~110 queries/second
- **Semantic only:** ~600 queries/second
- **Keyword only:** ~190 queries/second

### Memory Usage

- **GPU VRAM:** ~250MB (embeddings + index)
- **System RAM:** ~150MB (corpus + BM25)
- **Disk space:** ~20MB (all artifacts)

---

## Error Handling

### Common Exceptions

```python
from src.search_engine_module import HybridSearchEngine

try:
    engine = HybridSearchEngine("nonexistent_dir")
except FileNotFoundError as e:
    print(f"Artifacts not found: {e}")
    print("Run data_prep and build_index first!")

try:
    results = engine.hybrid_search("", top_k=10)
except ValueError as e:
    print(f"Invalid query: {e}")

try:
    results = engine.semantic_search("test", top_k=-5)
except ValueError as e:
    print(f"Invalid top_k: {e}")
```

---

## Advanced Usage

### Custom Search Parameters

```python
from cuvs.neighbors import cagra

# Modify CAGRA search parameters (advanced)
search_params = cagra.SearchParams(
    itopk_size=128,          # Internal topk (default: 64)
    search_width=2,          # Beam width (default: 1)
    max_iterations=100,      # Max graph traversal (default: 0 = auto)
)

# Note: Cần modify source code để expose search_params
```

---

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from src.search_engine_module import HybridSearchEngine

app = FastAPI()
engine = HybridSearchEngine()

@app.get("/search")
async def search(q: str, top_k: int = 10):
    results = engine.hybrid_search(q, top_k)
    return {"query": q, "results": results}
```

### Gradio UI

```python
import gradio as gr
from src.search_engine_module import HybridSearchEngine

engine = HybridSearchEngine()

def search_interface(query, top_k):
    results = engine.hybrid_search(query, top_k)
    output = "\n\n".join([
        f"{i}. {r['text'][:200]}..." 
        for i, r in enumerate(results, 1)
    ])
    return output

demo = gr.Interface(
    fn=search_interface,
    inputs=[
        gr.Textbox(label="Query"),
        gr.Slider(1, 20, value=5, label="Top K")
    ],
    outputs=gr.Textbox(label="Results")
)

demo.launch()
```

---

## Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.10+ | Required |
| cuVS | 24.10+ | GPU search |
| CuPy | 12.0+ | CUDA 12.0 |
| sentence-transformers | Latest | CPU/GPU |
| rank-bm25 | Latest | CPU only |

---

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn chạy nhanh
- [CODE_GUIDE.md](CODE_GUIDE.md) - Giải thích code chi tiết
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Xử lý lỗi
- [PROJECT_FINAL.md](PROJECT_FINAL.md) - Báo cáo kết quả

---

**Updated:** 2026-10-22  
**Maintainer:** Project Team
