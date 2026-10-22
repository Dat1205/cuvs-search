"""
Giai đoạn 4: Xây dựng Core Search Engine & RRF
Mục tiêu: Class quản lý tìm kiếm lai với thuật toán Reciprocal Rank Fusion
"""

import pickle
import re
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple

try:
    import cupy as cp
    from cuvs.neighbors import cagra
    CUVS_AVAILABLE = True
except ImportError:
    CUVS_AVAILABLE = False


class HybridSearchEngine:
    """
    Hệ thống tìm kiếm lai kết hợp BM25 và Vector Search với RRF
    """

    def __init__(self, artifacts_dir: str = "artifacts"):
        """
        Khởi tạo search engine và load các index
        """
        self.artifacts_dir = Path(artifacts_dir)
        print("Đang khởi tạo Hybrid Search Engine...")

        # Load corpus
        print("  - Đang load corpus...")
        with open(self.artifacts_dir / "corpus.pkl", "rb") as f:
            data = pickle.load(f)
        self.corpus = data['corpus']
        print(f"    ✓ Đã load {len(self.corpus)} văn bản")

        # Load BM25 model
        print("  - Đang load BM25 index...")
        with open(self.artifacts_dir / "bm25_model.pkl", "rb") as f:
            self.bm25_model = pickle.load(f)
        print("    ✓ Đã load BM25 index")

        # Load CAGRA index và sentence transformer
        self.cagra_index = None
        self.sentence_model = None

        if CUVS_AVAILABLE:
            print("  - Đang load CAGRA index...")
            self.cagra_index = cagra.load(str(self.artifacts_dir / "cagra_index.bin"))
            print("    ✓ Đã load CAGRA index vào GPU")

            print("  - Đang load Sentence Transformer...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
            print("    ✓ Đã load mô hình all-MiniLM-L6-v2")
        else:
            print("    ⚠️  cuVS không khả dụng - chỉ hỗ trợ keyword search")

        print("✓ Khởi tạo hoàn tất!\n")

    def preprocess_query(self, query: str) -> List[str]:
        """Tiền xử lý query giống như corpus"""
        query = query.lower()
        tokens = re.findall(r'\w+', query)
        return tokens

    def keyword_search(self, query: str, top_k: int = 10) -> Dict[int, int]:
        """
        Tìm kiếm bằng BM25

        Returns:
            Dict[doc_id, rank] - Rank bắt đầu từ 1
        """
        tokens = self.preprocess_query(query)
        scores = self.bm25_model.get_scores(tokens)

        # Lấy top_k kết quả có điểm > 0
        scored_docs = [(i, score) for i, score in enumerate(scores) if score > 0]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        scored_docs = scored_docs[:top_k]

        # Trả về {doc_id: rank}
        return {doc_id: rank + 1 for rank, (doc_id, score) in enumerate(scored_docs)}

    def semantic_search(self, query: str, top_k: int = 10) -> Dict[int, int]:
        """
        Tìm kiếm bằng Vector Search (CAGRA)

        Returns:
            Dict[doc_id, rank] - Rank bắt đầu từ 1
        """
        if not CUVS_AVAILABLE or self.cagra_index is None:
            return {}

        # Encode query
        query_embedding = self.sentence_model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        query_embedding_gpu = cp.asarray(query_embedding.reshape(1, -1), dtype=cp.float32)

        # Search
        search_params = cagra.SearchParams()
        distances, neighbors = cagra.search(
            search_params,
            self.cagra_index,
            query_embedding_gpu,
            top_k
        )

        # Convert về CPU
        neighbors = cp.asnumpy(neighbors)[0]

        # Trả về {doc_id: rank}
        return {int(doc_id): rank + 1 for rank, doc_id in enumerate(neighbors)}

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
        # Lấy kết quả từ cả 2 nhánh (lấy nhiều hơn để tăng độ phủ)
        search_k = top_k * 2

        keyword_results = self.keyword_search(query, search_k)
        semantic_results = self.semantic_search(query, search_k)

        # Tính RRF score
        rrf_scores = {}
        all_doc_ids = set(keyword_results.keys()) | set(semantic_results.keys())

        for doc_id in all_doc_ids:
            score = 0.0

            # Điểm từ keyword search
            if doc_id in keyword_results:
                score += 1.0 / (rrf_k + keyword_results[doc_id])

            # Điểm từ semantic search
            if doc_id in semantic_results:
                score += 1.0 / (rrf_k + semantic_results[doc_id])

            rrf_scores[doc_id] = score

        # Sắp xếp theo RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_docs = sorted_docs[:top_k]

        # Ánh xạ với corpus
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

    def print_results(self, results: List[Dict], query: str):
        """In kết quả tìm kiếm đẹp mắt"""
        print(f"\nKết quả tìm kiếm cho: '{query}'")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Score: {result['rrf_score']:.4f} | Label: {result['label']}")
            print(f"    Sources: {'K' if result['in_keyword'] else '-'}{'S' if result['in_semantic'] else '-'} (K=Keyword, S=Semantic)")

            # Rút gọn text nếu quá dài
            text = result['text']
            if len(text) > 150:
                text = text[:150] + "..."
            print(f"    {text}")

        print("\n" + "=" * 80)


def main():
    """Demo tìm kiếm"""
    engine = HybridSearchEngine()

    # Các câu truy vấn mẫu
    queries = [
        "stock market crash",
        "football championship",
        "new technology innovation"
    ]

    for query in queries:
        results = engine.hybrid_search(query, top_k=5)
        engine.print_results(results, query)


if __name__ == "__main__":
    main()
