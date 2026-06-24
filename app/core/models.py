from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RagChunk(BaseModel):
    doc_id: str
    chunk_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_id: str | None = None
    parent_content: str | None = None


class QueryOptions(BaseModel):
    embedding: str = "bge-large-zh"
    vectorstore: str = "chroma"
    retrieval_mode: str = "hybrid"
    top_k: int = 10
    final_top_k: int = 5
    vector_weight: float = 0.7
    bm25_weight: float = 0.3
    query_rewrite: bool = True
    query_expansion: bool = True
    query_transformation: bool = True
    metadata_router: bool = True
    multi_query: bool = False
    hyde: bool = False
    rerank: bool = True
    reranker_model: str = "score-fallback"
    compression: bool = True
    compression_mode: str = "auto"
    deduplicate: bool = True
    document_filter: bool = True
    parent_recovery: bool = True
    rag_fusion: bool = False
    metadata_filter: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str
    options: QueryOptions = Field(default_factory=QueryOptions)
    conversation_context: str = ""


class RetrievalHit(BaseModel):
    doc_id: str
    chunk_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float
    vector_score: float = 0.0
    bm25_score: float = 0.0
    rerank_score: float | None = None
    original_rank: int | None = None
    final_rank: int | None = None


class QueryTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trace_{uuid4().hex[:12]}")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    original_query: str
    rewritten_query: str
    expanded_queries: list[str] = Field(default_factory=list)
    metadata_filter: dict[str, Any] = Field(default_factory=dict)
    retrieval_mode: str
    options: dict[str, Any] = Field(default_factory=dict)
    retrieved_docs: list[RetrievalHit] = Field(default_factory=list)
    reranked_docs: list[RetrievalHit] = Field(default_factory=list)
    compressed_context: list[str] = Field(default_factory=list)
    answer: str = ""
    latency_ms: dict[str, float] = Field(default_factory=dict)
    token_usage: dict[str, int] = Field(default_factory=dict)
    cost: dict[str, float] = Field(default_factory=dict)


class EvalCase(BaseModel):
    query_id: str
    query: str
    category: str
    gold_doc_ids: list[str] = Field(default_factory=list)
    ground_truth: str | None = None
    relevance: dict[str, float] = Field(default_factory=dict)


class EvalRunRequest(BaseModel):
    eval_set: str = "data/eval_sets/energy_rag_eval.jsonl"
    experiment_name: str = "default_energy_rag"
    options: QueryOptions = Field(default_factory=QueryOptions)


class IngestRequest(BaseModel):
    path: str
    domain: str = "电气工程基础"
    doc_type: str = "技术资料"
    splitter: str = "recursive"
    chunk_size: int = 700
    chunk_overlap: int = 120
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnergyEntity(BaseModel):
    entity_id: str
    name: str
    entity_type: str
    domain: str
    description: str = ""
    source_chunk_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnergyRelation(BaseModel):
    relation_id: str
    source_entity: str
    target_entity: str
    relation_type: str
    domain: str
    description: str = ""
    source_chunk_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphRetrievalOptions(BaseModel):
    mode: str = "hybrid_graph"
    domain: str | None = None
    max_hops: int = 2
    top_k_entities: int = 10
    top_k_relations: int = 10
    include_chunk_context: bool = True
    include_graph_context: bool = True


class GraphRetrievalRequest(BaseModel):
    question: str
    options: GraphRetrievalOptions = Field(default_factory=GraphRetrievalOptions)


class GraphRetrievalResponse(BaseModel):
    question: str
    mode: str
    entities: list[EnergyEntity] = Field(default_factory=list)
    relations: list[EnergyRelation] = Field(default_factory=list)
    related_chunk_ids: list[str] = Field(default_factory=list)
    graph_context: str = ""
    chunk_context: str = ""
    final_context: str = ""
    reasoning_path: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
