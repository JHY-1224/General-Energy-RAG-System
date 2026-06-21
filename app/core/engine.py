from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from app.chains.rag_chain import RagChain
from app.config.loader import DEFAULT_CONFIG
from app.core.models import IngestRequest, QueryRequest, QueryTrace, RagChunk
from app.embeddings import EmbeddingFactory
from app.indexes import BM25Index, HybridIndex, ParentChildIndex, VectorIndex
from app.indexes.summary_index import SummaryIndex
from app.loaders import get_loader
from app.post_retrieval import ContextCompressor, Deduplicator, DocumentFilter, ParentContextRecover, Reranker
from app.pre_retrieval import MetadataRouter, QueryExpander, QueryRewriter
from app.pre_retrieval.hyde_generator import HydeGenerator
from app.preprocessors import DocumentCleaner, MetadataEnricher, TableExtractor
from app.retrievers.rag_fusion_retriever import RagFusionRetriever
from app.retrievers.hybrid_retriever import HybridRetriever
from app.splitters import get_splitter
from app.vectorstores import VectorStoreFactory


class ConfigurableRagEngine:
    def __init__(self) -> None:
        self.chunks: list[RagChunk] = []
        self.traces: dict[str, QueryTrace] = {}
        self.embedding_name = "bge-large-zh"
        self.vectorstore_name = "chroma"
        self.embedding = EmbeddingFactory.create(self.embedding_name)
        self.vector_store = VectorStoreFactory.create(self.vectorstore_name)
        self.vector_index = VectorIndex(self.embedding, self.vector_store)
        self.bm25_index = BM25Index()
        self.hybrid_index = HybridIndex(self.vector_index, self.bm25_index)
        self.parent_index = ParentChildIndex()
        self.summary_vector_index = None
        self.trace_dir = Path("data/traces")

    def configure(self, embedding: str, vectorstore: str) -> None:
        if embedding == self.embedding_name and vectorstore == self.vectorstore_name:
            return
        self.embedding_name = embedding
        self.vectorstore_name = vectorstore
        self.embedding = EmbeddingFactory.create(embedding)
        self.vector_store = VectorStoreFactory.create(vectorstore)
        self.vector_index = VectorIndex(self.embedding, self.vector_store)
        self.hybrid_index = HybridIndex(self.vector_index, self.bm25_index)
        self.rebuild_indexes()

    def rebuild_indexes(self) -> None:
        self.vector_store = VectorStoreFactory.create(self.vectorstore_name)
        self.vector_index = VectorIndex(self.embedding, self.vector_store)
        self.vector_index.build(self.chunks)
        self.bm25_index.build(self.chunks)
        self.hybrid_index = HybridIndex(self.vector_index, self.bm25_index)
        summary_store = VectorStoreFactory.create(self.vectorstore_name)
        self.summary_vector_index = VectorIndex(self.embedding, summary_store)
        self.summary_vector_index.build(SummaryIndex().build(self.chunks))

    def add_chunks(self, chunks: list[RagChunk]) -> None:
        existing = {chunk.chunk_id: chunk for chunk in self.chunks}
        existing.update({chunk.chunk_id: chunk for chunk in chunks})
        self.chunks = list(existing.values())
        self.rebuild_indexes()

    def remove_document(self, document_id: str) -> int:
        """Remove one document and rebuild every active index."""
        before = len(self.chunks)
        self.chunks = [chunk for chunk in self.chunks if chunk.doc_id != document_id]
        removed = before - len(self.chunks)
        if removed:
            self.rebuild_indexes()
        return removed

    def ingest(self, request: IngestRequest) -> dict:
        path = Path(request.path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Document not found: {path}")
        loader = get_loader(path)
        cleaner = DocumentCleaner()
        enricher = MetadataEnricher()
        table_extractor = TableExtractor()
        splitter = get_splitter(request.splitter, request.chunk_size, request.chunk_overlap)
        generated: list[RagChunk] = []
        for loaded_index, document in enumerate(loader.load(path), start=1):
            doc_id = f"doc_{path.stem}_{uuid4().hex[:8]}_{loaded_index}"
            metadata = enricher.enrich(document.source, {**document.metadata, **request.metadata, "domain": request.domain, "doc_type": request.doc_type})
            cleaned = cleaner.clean(document.content)
            body, tables = table_extractor.extract(cleaned, metadata.get("section", "未分节"))
            text_chunks = splitter.split(doc_id, body, metadata)
            for chunk in text_chunks:
                if chunk.parent_content:
                    chunk.metadata["parent_content"] = chunk.parent_content
            generated.extend(text_chunks)
            for table in tables:
                generated.append(RagChunk(doc_id=doc_id, chunk_id=table.table_id, content=table.content, metadata={**metadata, "category": "Table", "chunk_type": "表格", "table_id": table.table_id, "table_section": table.section}))
        self.add_chunks(generated)
        return {"path": str(path), "chunk_count": len(generated), "chunk_ids": [chunk.chunk_id for chunk in generated]}

    def _retrieve(self, query: str, request: QueryRequest, metadata_filter: dict) -> list:
        options = request.options
        common = {"top_k": options.top_k, "metadata_filter": metadata_filter}
        mode = options.retrieval_mode
        if mode == "vector":
            return self.vector_index.search(query, options.top_k, metadata_filter)
        if mode == "bm25":
            return self.bm25_index.search(query, options.top_k, metadata_filter)
        if mode == "summary" and self.summary_vector_index:
            return self.summary_vector_index.search(query, options.top_k, metadata_filter)
        if mode in {"rag_fusion", "parent_child_hybrid"} or options.rag_fusion:
            retriever = HybridRetriever(self.hybrid_index)
            queries = QueryExpander().expand(query)
            return RagFusionRetriever(retriever).retrieve(queries, **common, vector_weight=options.vector_weight, bm25_weight=options.bm25_weight)
        hits = self.hybrid_index.search(query, options.top_k, options.vector_weight, options.bm25_weight, metadata_filter)
        if mode == "parent_child":
            return self.parent_index.recover(hits)
        return hits

    def query(self, request: QueryRequest) -> QueryTrace:
        total_started = perf_counter()
        self.configure(request.options.embedding, request.options.vectorstore)
        trace = QueryTrace(
            original_query=request.question,
            rewritten_query=request.question,
            retrieval_mode=request.options.retrieval_mode,
            options=request.options.model_dump(),
        )

        pre_started = perf_counter()
        query = QueryRewriter().rewrite(request.question, request.conversation_context) if request.options.query_rewrite else request.question
        expanded = QueryExpander().expand(query) if request.options.query_expansion or request.options.multi_query else [query]
        if request.options.hyde:
            expanded.append(HydeGenerator().generate(query))
        metadata_filter = MetadataRouter().route(query, request.options.metadata_filter) if request.options.metadata_router or request.options.query_transformation else request.options.metadata_filter
        trace.rewritten_query = query
        trace.expanded_queries = expanded
        trace.metadata_filter = metadata_filter
        trace.latency_ms["pre_retrieval"] = round((perf_counter() - pre_started) * 1000, 3)

        retrieval_started = perf_counter()
        embedding_started = perf_counter()
        self.embedding.embed(expanded[-1])
        trace.latency_ms["query_embedding"] = round((perf_counter() - embedding_started) * 1000, 3)
        if request.options.multi_query or request.options.rag_fusion:
            rankings = [self._retrieve(candidate, request, metadata_filter) for candidate in expanded]
            from app.post_retrieval.rrf_fusion import RrfFusion

            hits = RrfFusion().fuse(rankings, request.options.top_k)
        else:
            hits = self._retrieve(expanded[-1], request, metadata_filter)
        for rank, hit in enumerate(hits, start=1):
            hit.original_rank = rank
        trace.latency_ms["retrieval"] = round((perf_counter() - retrieval_started) * 1000, 3)
        trace.retrieved_docs = [hit.model_copy(deep=True) for hit in hits]

        post_started = perf_counter()
        if request.options.deduplicate:
            hits = Deduplicator().deduplicate(hits)
        if request.options.document_filter:
            hits = DocumentFilter().filter(hits)
        if request.options.parent_recovery:
            hits = ParentContextRecover().recover(hits)
        rerank_started = perf_counter()
        if request.options.rerank:
            hits = Reranker().rerank(query, hits, request.options.final_top_k)
        else:
            hits = hits[: request.options.final_top_k]
            for rank, hit in enumerate(hits, start=1):
                hit.final_rank = rank
        trace.latency_ms["rerank"] = round((perf_counter() - rerank_started) * 1000, 3)
        trace.reranked_docs = [hit.model_copy(deep=True) for hit in hits]

        compression_started = perf_counter()
        contexts = [ContextCompressor().compress(query, hit.content, mode=request.options.compression_mode) if request.options.compression else hit.content for hit in hits]
        trace.compressed_context = contexts
        trace.latency_ms["compression"] = round((perf_counter() - compression_started) * 1000, 3)
        trace.latency_ms["post_retrieval"] = round((perf_counter() - post_started) * 1000, 3)

        generation_started = perf_counter()
        trace.answer = RagChain().generate(request.question, contexts, [hit.chunk_id for hit in hits])
        trace.latency_ms["generation"] = round((perf_counter() - generation_started) * 1000, 3)
        trace.latency_ms["total"] = round((perf_counter() - total_started) * 1000, 3)
        trace.token_usage = {"input_tokens": sum(len(item) for item in contexts) // 2, "output_tokens": len(trace.answer) // 2}
        trace.cost = {"embedding": 0.0, "generation": 0.0, "total": 0.0}
        self.save_trace(trace)
        return trace

    def save_trace(self, trace: QueryTrace) -> None:
        self.traces[trace.trace_id] = trace
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        (self.trace_dir / f"{trace.trace_id}.json").write_text(json.dumps(trace.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    def get_trace(self, trace_id: str) -> QueryTrace | None:
        return self.traces.get(trace_id)

    def stats(self) -> dict:
        return {"chunks": len(self.chunks), "documents": len({chunk.doc_id for chunk in self.chunks}), "embedding": self.embedding_name, "embedding_dimension": self.embedding.dimension, "vectorstore": self.vectorstore_name, "traces": len(self.traces), "default_config": DEFAULT_CONFIG}
