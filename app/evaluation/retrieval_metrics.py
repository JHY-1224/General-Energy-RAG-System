from __future__ import annotations

import math


def hit_at_k(retrieved: list[str], gold: list[str], k: int) -> float:
    return float(bool(set(retrieved[:k]) & set(gold))) if gold else 0.0


def recall_at_k(retrieved: list[str], gold: list[str], k: int) -> float:
    return len(set(retrieved[:k]) & set(gold)) / len(set(gold)) if gold else 0.0


def reciprocal_rank(retrieved: list[str], gold: list[str]) -> float:
    gold_set = set(gold)
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in gold_set:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: list[str], gold: list[str], k: int, relevance: dict[str, float] | None = None) -> float:
    relevance = relevance or {doc_id: 1.0 for doc_id in gold}
    dcg = sum((2 ** relevance.get(doc_id, 0.0) - 1) / math.log2(rank + 1) for rank, doc_id in enumerate(retrieved[:k], start=1))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum((2**score - 1) / math.log2(rank + 1) for rank, score in enumerate(ideal, start=1))
    return dcg / idcg if idcg else 0.0


def calculate_retrieval_metrics(retrieved: list[str], gold: list[str], relevance: dict[str, float] | None = None) -> dict[str, float]:
    retrieved = list(dict.fromkeys(retrieved))
    return {
        "hit_at_1": hit_at_k(retrieved, gold, 1),
        "hit_at_5": hit_at_k(retrieved, gold, 5),
        "recall_at_5": recall_at_k(retrieved, gold, 5),
        "recall_at_10": recall_at_k(retrieved, gold, 10),
        "mrr": reciprocal_rank(retrieved, gold),
        "ndcg_at_5": ndcg_at_k(retrieved, gold, 5, relevance),
    }
