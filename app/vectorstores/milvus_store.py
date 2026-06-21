from .chroma_store import ChromaStore


class MilvusStore(ChromaStore):
    """Local fallback for the future Milvus adapter."""
