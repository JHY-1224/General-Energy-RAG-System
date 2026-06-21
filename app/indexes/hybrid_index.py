from app.core.models import RetrievalHit


class HybridIndex:
    def __init__(self, vector_index, bm25_index) -> None:
        self.vector_index = vector_index
        self.bm25_index = bm25_index

    def search(self, query: str, top_k: int, vector_weight: float = 0.7, bm25_weight: float = 0.3, metadata_filter: dict | None = None) -> list[RetrievalHit]:
        vector_hits = self.vector_index.search(query, top_k * 2, metadata_filter)
        bm25_hits = self.bm25_index.search(query, top_k * 2, metadata_filter)
        merged: dict[str, RetrievalHit] = {}
        for hit in vector_hits:
            hit.score = hit.vector_score * vector_weight
            merged[hit.chunk_id] = hit
        for hit in bm25_hits:
            if hit.chunk_id in merged:
                merged[hit.chunk_id].bm25_score = hit.bm25_score
                merged[hit.chunk_id].score += hit.bm25_score * bm25_weight
            else:
                hit.score = hit.bm25_score * bm25_weight
                merged[hit.chunk_id] = hit
        return sorted(merged.values(), key=lambda item: item.score, reverse=True)[:top_k]
