class HybridRetriever:
    def __init__(self, index) -> None:
        self.index = index

    def retrieve(self, query: str, **kwargs):
        return self.index.search(query, kwargs.get("top_k", 10), kwargs.get("vector_weight", 0.7), kwargs.get("bm25_weight", 0.3), kwargs.get("metadata_filter"))
