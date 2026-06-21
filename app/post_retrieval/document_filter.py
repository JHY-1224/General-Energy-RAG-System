class DocumentFilter:
    def filter(self, hits: list, minimum_score: float = 0.0) -> list:
        return [hit for hit in hits if (hit.rerank_score if hit.rerank_score is not None else hit.score) >= minimum_score]
