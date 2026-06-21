class SummaryRetriever:
    def __init__(self, vector_retriever) -> None:
        self.vector_retriever = vector_retriever

    def retrieve(self, query: str, **kwargs):
        return self.vector_retriever.retrieve(query, **kwargs)
