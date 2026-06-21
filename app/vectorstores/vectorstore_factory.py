from .chroma_store import ChromaStore
from .faiss_store import FaissStore
from .milvus_store import MilvusStore
from .pgvector_store import PgVectorStore
from .qdrant_store import QdrantStore


class VectorStoreFactory:
    @classmethod
    def create(cls, name: str = "chroma"):
        normalized = name.lower()
        if normalized == "faiss":
            return FaissStore()
        if normalized == "qdrant":
            return QdrantStore()
        if normalized == "pgvector":
            return PgVectorStore()
        if normalized == "milvus":
            return MilvusStore()
        return ChromaStore()
