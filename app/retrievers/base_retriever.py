class BaseRetriever:
    def retrieve(self, query: str, **kwargs):
        raise NotImplementedError
