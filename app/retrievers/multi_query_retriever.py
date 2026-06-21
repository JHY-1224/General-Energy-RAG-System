class MultiQueryRetriever:
    def __init__(self, base_retriever) -> None:
        self.base_retriever = base_retriever

    def retrieve(self, queries: list[str], **kwargs):
        results = []
        for query in queries:
            results.extend(self.base_retriever.retrieve(query, **kwargs))
        return results
