from fastapi import APIRouter

from app.api.dependencies import engine


router = APIRouter(prefix="/api/v2/config", tags=["RAG v2 Config"])


@router.get("/options")
def config_options():
    return {
        "embeddings": ["huggingface-local", "bge-large-zh", "qwen-embedding", "openai", "dashscope"],
        "vectorstores": ["chroma", "faiss", "qdrant", "pgvector", "milvus"],
        "retrieval_modes": ["vector", "bm25", "hybrid", "parent_child", "summary", "rag_fusion"],
        "pre_retrieval": ["query_rewrite", "query_expansion", "query_transformation", "metadata_router", "multi_query", "hyde"],
        "post_retrieval": ["rerank", "compression", "deduplicate", "document_filter", "parent_recovery", "rag_fusion"],
        "stats": engine.stats(),
    }
