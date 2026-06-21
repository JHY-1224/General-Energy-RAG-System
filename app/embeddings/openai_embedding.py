from .embedding_factory import HashEmbedding


class OpenAIEmbedding(HashEmbedding):
    """Offline fallback; replace embed() with OpenAI SDK when configured."""
