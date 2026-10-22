"""
Giai đoạn 2: Thu thập và Tiền xử lý dữ liệu
Mục tiêu: Tải 5,000 mẫu từ AG News, làm sạch và chuẩn bị cho BM25
"""

import sys
import io
import pickle
import re
from pathlib import Path
from datasets import load_dataset

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


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


def main():
    print("=" * 50)
    print("Bước 1: Tải dữ liệu AG News")
    print("=" * 50)

    # Tải 5,000 mẫu từ AG News
    # Thử với namespace đầy đủ
    try:
        dataset = load_dataset("fancyzhx/ag_news", split="train[:5000]")
    except:
        # Fallback to legacy name
        dataset = load_dataset("ag_news", split="train[:5000]", trust_remote_code=True)

    print(f"✓ Đã tải {len(dataset)} mẫu từ AG News")

    # Trích xuất text và label
    corpus = []
    tokenized_corpus = []

    print("\nBước 2: Tiền xử lý văn bản")
    for i, item in enumerate(dataset):
        text = item['text']
        label = item['label']

        # Lưu văn bản gốc và label
        corpus.append({
            'id': i,
            'text': text,
            'label': label
        })

        # Tokenize cho BM25
        tokens = preprocess_text(text)
        tokenized_corpus.append(tokens)

        if (i + 1) % 1000 == 0:
            print(f"  Đã xử lý {i + 1}/{len(dataset)} văn bản")

    print(f"✓ Hoàn thành tiền xử lý {len(corpus)} văn bản")

    # Tạo thư mục artifacts nếu chưa có
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # Lưu dữ liệu
    print("\nBước 3: Lưu dữ liệu đã xử lý")
    with open(artifacts_dir / "corpus.pkl", "wb") as f:
        pickle.dump({
            'corpus': corpus,
            'tokenized_corpus': tokenized_corpus
        }, f)

    print(f"✓ Đã lưu vào {artifacts_dir / 'corpus.pkl'}")
    print(f"\nThống kê:")
    print(f"  - Tổng số văn bản: {len(corpus)}")
    print(f"  - Số token trung bình: {sum(len(t) for t in tokenized_corpus) / len(tokenized_corpus):.1f}")
    print("\n✓ Hoàn thành Giai đoạn 2!")


if __name__ == "__main__":
    main()
