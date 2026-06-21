class ParentChildRetriever:
    def __init__(self, base_retriever, parent_index) -> None:
        self.base_retriever = base_retriever
        self.parent_index = parent_index

    def retrieve(self, query: str, **kwargs):
        return self.parent_index.recover(self.base_retriever.retrieve(query, **kwargs))
