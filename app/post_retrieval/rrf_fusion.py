class RrfFusion:
    def __init__(self, k: int = 60) -> None:
        self.k = k

    def fuse(self, rankings: list[list], top_k: int) -> list:
        scores: dict[str, float] = {}
        hits = {}
        for ranking in rankings:
            for rank, hit in enumerate(ranking, start=1):
                scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (self.k + rank)
                hits[hit.chunk_id] = hit
        ordered = sorted(hits.values(), key=lambda item: scores[item.chunk_id], reverse=True)[:top_k]
        for rank, hit in enumerate(ordered, start=1):
            hit.score = scores[hit.chunk_id]
            hit.final_rank = rank
        return ordered
