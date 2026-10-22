"""
Giai đoạn 3: Xây dựng Chỉ mục & Lưu trữ vật lý
Mục tiêu: Tạo BM25 index và Dense Vector index (CAGRA/FAISS)

Backend ưu tiên:
  1. cuVS CAGRA (GPU) – nếu có cuVS cài sẵn
  2. FAISS GPU        – nếu có faiss-gpu
  3. FAISS CPU        – fallback an toàn (không cần GPU)
"""

import sys
import io
import pickle
import numpy as np
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ─── Phát hiện backend ───────────────────────────────────────────────────────
BACKEND = "cpu"  # default

try:
    import cupy as cp
    from cuvs.neighbors import cagra
    BACKEND = "cuvs"
    print("[backend] cuVS CAGRA (GPU) - OK")
except ImportError as e:
    print(f"[backend] cuVS khong import duoc: {e}")
except Exception as e:
    print(f"[backend] cuVS loi khac: {e}")

if BACKEND == "cpu":
    try:
        import faiss
        if faiss.get_num_gpus() > 0:
            BACKEND = "faiss_gpu"
            print("[backend] FAISS GPU - OK")
        else:
            BACKEND = "faiss_cpu"
            print("[backend] FAISS CPU - OK")
    except ImportError as e:
        print(f"[backend] FAISS khong import duoc: {e}")
        print("[backend] Khong co vector index. Chi build BM25 + embeddings.")

# ─── Helpers ─────────────────────────────────────────────────────────────────

def build_faiss_index(embeddings: np.ndarray, use_gpu: bool = False):
    """Xây dựng FAISS IndexFlatIP (inner product)."""
    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    if use_gpu:
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)
    index.add(embeddings)
    return index


def save_faiss_index(index, path: str, use_gpu: bool = False):
    """Lưu FAISS index ra file."""
    import faiss
    if use_gpu:
        index = faiss.index_gpu_to_cpu(index)
    faiss.write_index(index, path)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("Giai đoạn 3: Xây dựng Chỉ mục")
    print("=" * 55)

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # ── Bước 1: Tải dữ liệu đã tiền xử lý ────────────────
    print("\nBước 1: Tải dữ liệu đã tiền xử lý")
    corpus_path = artifacts_dir / "corpus.pkl"
    if not corpus_path.exists():
        print(f"❌ Không tìm thấy {corpus_path}. Chạy giai đoạn 1-2 trước!")
        sys.exit(1)

    with open(corpus_path, "rb") as f:
        data = pickle.load(f)

    corpus = data['corpus']
    tokenized_corpus = data['tokenized_corpus']
    print(f"✓ Đã tải {len(corpus)} văn bản")

    # ── Bước 2: BM25 Index (CPU) ───────────────────────────
    print("\nBước 2: Xây dựng BM25 Index (CPU)")
    from rank_bm25 import BM25Okapi
    bm25_model = BM25Okapi(tokenized_corpus)

    bm25_path = artifacts_dir / "bm25_model.pkl"
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_model, f)
    print(f"✓ Đã lưu BM25 index vào {bm25_path}")

    # ── Bước 3: Embeddings ────────────────────────────────
    print("\nBước 3: Tạo Dense Embeddings")
    print("  3.1: Tải mô hình Sentence Transformer")

    from sentence_transformers import SentenceTransformer

    # Chọn device: cuda nếu có GPU, ngược lại cpu
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        device = "cpu"

    print(f"  Device: {device}")
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    print("  ✓ Đã tải mô hình all-MiniLM-L6-v2")

    print("  3.2: Mã hóa văn bản thành embeddings")
    texts = [item['text'] for item in corpus]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=64,
    )
    embeddings = embeddings.astype(np.float32)
    print(f"  ✓ Embeddings: shape={embeddings.shape}, dtype={embeddings.dtype}")

    emb_path = artifacts_dir / "embeddings.npy"
    np.save(emb_path, embeddings)
    print(f"  ✓ Đã lưu embeddings vào {emb_path}")

    # ── Bước 4: Vector Index ──────────────────────────────
    if BACKEND == "cuvs":
        print("\nBước 4: Xây dựng CAGRA Index (cuVS GPU)")
        embeddings_gpu = cp.asarray(embeddings)

        index_params = cagra.IndexParams(
            metric="inner_product",
            build_algo="nn_descent"
        )
        index = cagra.build(index_params, embeddings_gpu)
        print("  ✓ Đã xây dựng CAGRA index")

        cagra_path = str(artifacts_dir / "cagra_index.bin")
        cagra.save(cagra_path, index)
        print(f"  ✓ Đã lưu CAGRA index vào {cagra_path}")

    elif BACKEND in ("faiss_gpu", "faiss_cpu"):
        use_gpu = (BACKEND == "faiss_gpu")
        label = "FAISS GPU" if use_gpu else "FAISS CPU"
        print(f"\nBước 4: Xây dựng {label} Index")

        index = build_faiss_index(embeddings, use_gpu=use_gpu)
        print(f"  ✓ Đã xây dựng {label} index ({index.ntotal} vectors)")

        faiss_path = str(artifacts_dir / "faiss_index.bin")
        save_faiss_index(index, faiss_path, use_gpu=use_gpu)
        print(f"  ✓ Đã lưu {label} index vào {faiss_path}")

    else:
        print("\n⚠️  Bỏ qua Bước 4: Không có vector index backend.")
        print("   Cài thêm: pip install faiss-cpu")
        print("   Hoặc dùng conda với cuVS cho GPU search.")

    # ── Tổng kết ──────────────────────────────────────────
    print("\n" + "=" * 55)
    print("✓ Hoàn thành Giai đoạn 3!")
    print("=" * 55)
    print("\nCác file trong artifacts/:")
    for f in sorted(artifacts_dir.glob("*")):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name:<30} {size_mb:6.2f} MB")


if __name__ == "__main__":
    main()
