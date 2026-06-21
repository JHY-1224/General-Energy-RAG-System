from .embedding_factory import HashEmbedding


class DashScopeEmbedding(HashEmbedding):
    """Offline fallback; replace embed() with DashScope SDK when configured."""
