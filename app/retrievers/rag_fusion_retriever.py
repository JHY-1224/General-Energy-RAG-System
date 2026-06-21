from app.post_retrieval.rrf_fusion import RrfFusion


class RagFusionRetriever:
    def __init__(self, base_retriever) -> None:
        self.base_retriever = base_retriever

    def retrieve(self, queries: list[str], **kwargs):
        rankings = [self.base_retriever.retrieve(query, **kwargs) for query in queries]
        return RrfFusion().fuse(rankings, kwargs.get("top_k", 10))
