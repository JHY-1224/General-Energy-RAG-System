from .chroma_store import ChromaStore


class PgVectorStore(ChromaStore):
    """Local fallback for the future pgvector adapter."""
