from app.embeddings.embedding_factory import tokenize


class Reranker:
    def rerank(self, query: str, hits: list, top_k: int) -> list:
        query_terms = set(tokenize(query))
        for hit in hits:
            content_terms = set(tokenize(hit.content))
            overlap = len(query_terms & content_terms) / max(1, len(query_terms))
            hit.rerank_score = round(hit.score * 0.65 + overlap * 0.35, 6)
        ranked = sorted(hits, key=lambda item: item.rerank_score or 0.0, reverse=True)[:top_k]
        for rank, hit in enumerate(ranked, start=1):
            hit.final_rank = rank
        return ranked
