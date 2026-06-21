class BM25Retriever:
    def __init__(self, index) -> None:
        self.index = index

    def retrieve(self, query: str, **kwargs):
        return self.index.search(query, kwargs.get("top_k", 10), kwargs.get("metadata_filter"))
