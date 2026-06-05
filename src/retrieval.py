"""
retrieval.py — Local semantic-style search using TF-IDF + cosine similarity.

Uses scikit-learn (fully offline, no model downloads required).
For production, swap in SentenceTransformers once HuggingFace is accessible.

Usage:
    engine = RetrievalEngine(docs)      # docs: {filename: text}
    results = engine.search("payments due in January", top_k=5)
"""
from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RetrievalEngine:
    """TF-IDF based retrieval — fast, fully offline, no GPU needed."""

    def __init__(self, docs: dict[str, str]):
        self.filenames: list[str] = list(docs.keys())
        self.texts: list[str] = list(docs.values())

        print(f"[Retrieval] Building TF-IDF index over {len(self.texts)} documents …")
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),   # unigrams + bigrams for better coverage
            min_df=1,
            sublinear_tf=True,    # log-normalise term frequencies
            stop_words="english",
        )
        self.matrix = self.vectorizer.fit_transform(self.texts)
        print(f"[Retrieval] Index ready. Vocabulary size: {len(self.vectorizer.vocabulary_)}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Return top-k documents ranked by cosine similarity to *query*."""
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).flatten()
        ranked = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in ranked:
            results.append({
                "filename": self.filenames[idx],
                "score": round(float(scores[idx]), 4),
                "snippet": self.texts[idx][:200].replace("\n", " "),
            })
        return results
