#!/usr/bin/env python3
"""
main.py — Local AI Document Intelligence Pipeline

Usage:
    python main.py --docs documents/          # process all PDFs, write output.json
    python main.py --search "payments due"    # semantic search (after first run)
    python main.py --docs documents/ --search "electricity bills"
"""
import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows (avoids cp1252 encoding errors in the terminal)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingest import load_documents
from classifier import classify
from extractor import extract


OUTPUT_FILE = Path("output/output.json")


def process_documents(docs_folder: str) -> dict:
    print(f"\n{'='*60}")
    print(f" Document Intelligence Pipeline")
    print(f"{'='*60}")

    print(f"\n[1/3] Loading PDFs from '{docs_folder}' …")
    docs = load_documents(docs_folder)
    print(f"      Loaded {len(docs)} documents.")

    print("\n[2/3] Classifying & extracting …")
    results: dict = {}
    for fname, text in docs.items():
        doc_class = classify(text)
        fields = extract(doc_class, text)
        results[fname] = {"class": doc_class, **fields}
        status = f"  {fname:<30} -> {doc_class}"
        print(status)

    print("\n[3/3] Writing output.json …")
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"      Saved -> {OUTPUT_FILE}")

    # Summary table
    from collections import Counter
    counts = Counter(v["class"] for v in results.values())
    print("\n── Classification Summary ──────────────────")
    for cls, n in sorted(counts.items()):
        print(f"   {cls:<20} {n:>3} doc(s)")
    print()
    return results


def run_search(docs_folder: str, query: str, top_k: int = 5):
    from retrieval import RetrievalEngine
    docs = load_documents(docs_folder)
    engine = RetrievalEngine(docs)
    print(f"\n🔍 Query: \"{query}\"\n")
    results = engine.search(query, top_k=top_k)
    print(f"{'Rank':<5} {'File':<30} {'Score':<8} Snippet")
    print("─" * 80)
    for rank, r in enumerate(results, 1):
        print(f"{rank:<5} {r['filename']:<30} {r['score']:<8.4f} {r['snippet'][:60]}…")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Local AI Document Classification & Retrieval"
    )
    parser.add_argument(
        "--docs", default="documents",
        help="Folder containing PDF files (default: documents/)"
    )
    parser.add_argument(
        "--search", metavar="QUERY",
        help="Semantic search query"
    )
    parser.add_argument(
        "--top-k", type=int, default=5,
        help="Number of search results to return (default: 5)"
    )
    args = parser.parse_args()

    if args.docs:
        process_documents(args.docs)

    if args.search:
        run_search(args.docs, args.search, top_k=args.top_k)


if __name__ == "__main__":
    main()
