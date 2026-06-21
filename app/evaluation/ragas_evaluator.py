from __future__ import annotations

from app.embeddings.embedding_factory import tokenize


def _overlap(left: str, right: str) -> float:
    left_terms = set(tokenize(left))
    right_terms = set(tokenize(right))
    return len(left_terms & right_terms) / max(1, len(right_terms))


class RagasEvaluator:
    """Offline-compatible metric proxy with the same output contract as RAGAS."""

    def evaluate(self, question: str, answer: str, contexts: list[str], ground_truth: str | None) -> dict[str, float | None]:
        context = " ".join(contexts)
        context_scores = [_overlap(item, question) for item in contexts]
        metrics: dict[str, float | None] = {
            "faithfulness": round(_overlap(context, answer), 4),
            "answer_relevancy": round(_overlap(answer, question), 4),
            "context_precision": round(sum(score > 0 for score in context_scores) / max(1, len(context_scores)), 4),
            "context_recall": round(_overlap(context, ground_truth or question), 4),
            "answer_correctness": round(_overlap(answer, ground_truth), 4) if ground_truth else None,
            "context_entity_recall": round(_overlap(context, question), 4),
        }
        return metrics
