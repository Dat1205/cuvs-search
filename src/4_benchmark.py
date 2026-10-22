"""
Giai đoạn 5: Kiểm thử, Đánh giá & Đo lường Hiệu năng
Mục tiêu: Đánh giá chất lượng và đo latency của hệ thống
"""

import sys
import io
import time
import numpy as np
from pathlib import Path
from typing import List

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import HybridSearchEngine
sys.path.insert(0, str(Path(__file__).parent))
from search_engine_module import HybridSearchEngine

try:
    import cupy as cp
    CUVS_AVAILABLE = True
except ImportError:
    CUVS_AVAILABLE = False


class Benchmark:
    """Class đo lường hiệu năng của Hybrid Search Engine"""

    def __init__(self, engine: HybridSearchEngine):
        self.engine = engine

    def qualitative_test(self):
        """Kiểm thử chất lượng với các loại truy vấn khác nhau"""
        print("=" * 80)
        print("KIỂM THỬ CHẤT LƯỢNG")
        print("=" * 80)

        test_queries = {
            "Truy vấn khớp từ khóa đặc thù": [
                "Iraq war",
                "Microsoft Windows",
                "Olympics Athens"
            ],
            "Truy vấn diễn giải ngữ nghĩa": [
                "financial crisis and economy",
                "sports competition results",
                "computer and internet technology"
            ],
            "Truy vấn hỗn hợp": [
                "Apple company stock price",
                "election results politics",
                "scientific research breakthrough"
            ]
        }

        for category, queries in test_queries.items():
            print(f"\n{'=' * 80}")
            print(f"📊 {category}")
            print("=" * 80)

            for query in queries:
                print(f"\nQuery: '{query}'")
                print("-" * 80)

                # Keyword search
                kw_results = self.engine.keyword_search(query, top_k=3)
                print(f"Keyword Search: {len(kw_results)} kết quả")

                # Semantic search
                sem_results = self.engine.semantic_search(query, top_k=3)
                print(f"Semantic Search: {len(sem_results)} kết quả")

                # Hybrid search
                hybrid_results = self.engine.hybrid_search(query, top_k=5)
                print(f"\nTop 3 Hybrid Results:")
                for i, result in enumerate(hybrid_results[:3], 1):
                    sources = f"{'K' if result['in_keyword'] else '-'}{'S' if result['in_semantic'] else '-'}"
                    text_preview = result['text'][:100] + "..."
                    print(f"  [{i}] {sources} | Score: {result['rrf_score']:.4f}")
                    print(f"      {text_preview}")

                print()

    def latency_benchmark(self, num_queries: int = 100, warmup: int = 5):
        """
        Đo độ trễ (latency) của hệ thống

        Args:
            num_queries: Số lượng truy vấn để đo
            warmup: Số truy vấn warm-up GPU
        """
        print("\n" + "=" * 80)
        print("ĐO LƯỜNG LATENCY")
        print("=" * 80)

        # Các truy vấn test
        test_queries = [
            "stock market crash",
            "football championship",
            "new technology",
            "political election",
            "scientific research",
            "business merger",
            "international trade",
            "climate change",
            "medical breakthrough",
            "entertainment news"
        ]

        # Warm-up
        print(f"\n🔥 Warm-up GPU ({warmup} truy vấn)...")
        for i in range(warmup):
            query = test_queries[i % len(test_queries)]
            _ = self.engine.hybrid_search(query, top_k=10)
        print("✓ Warm-up hoàn tất")

        # Benchmark keyword search
        print(f"\n📊 Đo latency Keyword Search ({num_queries} truy vấn)...")
        kw_times = []
        for i in range(num_queries):
            query = test_queries[i % len(test_queries)]

            start = time.perf_counter()
            _ = self.engine.keyword_search(query, top_k=10)
            end = time.perf_counter()

            kw_times.append((end - start) * 1000)  # Convert to ms

        self._print_stats("Keyword Search", kw_times)

        # Benchmark semantic search (nếu có GPU)
        if CUVS_AVAILABLE and self.engine.cagra_index is not None:
            print(f"\n📊 Đo latency Semantic Search ({num_queries} truy vấn)...")
            sem_times = []
            sem_times_gpu = []

            for i in range(num_queries):
                query = test_queries[i % len(test_queries)]

                # Đo tổng thời gian (CPU timer)
                start = time.perf_counter()

                # Đo thời gian GPU chính xác
                start_event = cp.cuda.Event()
                end_event = cp.cuda.Event()

                # Encode query
                query_embedding = self.engine.sentence_model.encode(
                    query,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
                query_embedding_gpu = cp.asarray(query_embedding.reshape(1, -1), dtype=cp.float32)

                # Time GPU search
                start_event.record()
                from cuvs.neighbors import cagra
                search_params = cagra.SearchParams()
                distances, neighbors = cagra.search(
                    search_params,
                    self.engine.cagra_index,
                    query_embedding_gpu,
                    10
                )
                end_event.record()
                end_event.synchronize()

                end = time.perf_counter()

                gpu_time = cp.cuda.get_elapsed_time(start_event, end_event)
                total_time = (end - start) * 1000

                sem_times.append(total_time)
                sem_times_gpu.append(gpu_time)

            self._print_stats("Semantic Search (Total)", sem_times)
            self._print_stats("Semantic Search (GPU only)", sem_times_gpu)

        # Benchmark hybrid search
        print(f"\n📊 Đo latency Hybrid Search ({num_queries} truy vấn)...")
        hybrid_times = []
        for i in range(num_queries):
            query = test_queries[i % len(test_queries)]

            start = time.perf_counter()
            _ = self.engine.hybrid_search(query, top_k=10)
            end = time.perf_counter()

            hybrid_times.append((end - start) * 1000)

        self._print_stats("Hybrid Search", hybrid_times)

        # Summary
        print("\n" + "=" * 80)
        print("📈 TỔNG KẾT")
        print("=" * 80)
        if CUVS_AVAILABLE and self.engine.cagra_index is not None:
            print(f"Semantic Search GPU time: {np.mean(sem_times_gpu):.2f} ms (avg)")
            print(f"✓ Yêu cầu: < 10 ms → {'PASS' if np.mean(sem_times_gpu) < 10 else 'FAIL'}")
        print(f"\nHybrid Search total time: {np.mean(hybrid_times):.2f} ms (avg)")
        print(f"Throughput: {1000 / np.mean(hybrid_times):.1f} queries/second")

    def _print_stats(self, name: str, times: List[float]):
        """In thống kê thời gian"""
        times_array = np.array(times)
        print(f"\n{name}:")
        print(f"  Average:  {np.mean(times_array):.2f} ms")
        print(f"  Median:   {np.median(times_array):.2f} ms")
        print(f"  Min:      {np.min(times_array):.2f} ms")
        print(f"  Max:      {np.max(times_array):.2f} ms")
        print(f"  P50:      {np.percentile(times_array, 50):.2f} ms")
        print(f"  P95:      {np.percentile(times_array, 95):.2f} ms")
        print(f"  P99:      {np.percentile(times_array, 99):.2f} ms")


def main():
    """Chạy benchmark đầy đủ"""
    print("\n🚀 Khởi động Hybrid Search Benchmark")
    print("=" * 80)

    # Khởi tạo engine
    engine = HybridSearchEngine()

    # Chạy benchmark
    benchmark = Benchmark(engine)

    # Test chất lượng
    benchmark.qualitative_test()

    # Test hiệu năng
    benchmark.latency_benchmark(num_queries=100, warmup=5)

    print("\n✓ Benchmark hoàn tất!")


if __name__ == "__main__":
    main()
