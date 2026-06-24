from __future__ import annotations

from .global_graph_retriever import GlobalGraphRetriever
from .graph_context_builder import GraphContextBuilder
from .graph_store import GraphStore
from .local_graph_retriever import LocalGraphRetriever


class GraphHybridRetriever:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def retrieve(self, query: str, mode: str = "hybrid_graph", domain: str | None = None, max_hops: int = 2, top_k_entities: int = 10, top_k_relations: int = 10) -> dict:
        if mode == "local_graph":
            return LocalGraphRetriever(self.store).retrieve(query, domain, max_hops, top_k_entities, top_k_relations)
        if mode == "global_graph":
            return GlobalGraphRetriever(self.store).retrieve(query, domain, max_hops, top_k_entities, top_k_relations)
        if mode == "naive":
            entities = self.store.search_entities(query, domain, top_k_entities)
            chunk_ids = list(dict.fromkeys(chunk for item in entities for chunk in item.source_chunk_ids))
            context = GraphContextBuilder().build(self.store, entities, [], [], chunk_ids)
            return {"entities": entities, "relations": [], "reasoning_path": [], "related_chunk_ids": chunk_ids, "graph_context": context}

        local = LocalGraphRetriever(self.store).retrieve(query, domain, max_hops, top_k_entities, top_k_relations)
        global_result = GlobalGraphRetriever(self.store).retrieve(query, domain, max_hops, top_k_entities, top_k_relations)
        entities = {item.entity_id: item for item in local["entities"] + global_result["entities"]}
        relations = {item.relation_id: item for item in local["relations"] + global_result["relations"]}
        entity_items = list(entities.values())[:top_k_entities]
        relation_items = sorted(relations.values(), key=lambda item: -item.confidence)[:top_k_relations]
        paths = list(dict.fromkeys(local["reasoning_path"] + global_result["reasoning_path"]))
        chunk_ids = list(dict.fromkeys(local["related_chunk_ids"] + global_result["related_chunk_ids"]))
        context = GraphContextBuilder().build(self.store, entity_items, relation_items, paths, chunk_ids)
        return {"entities": entity_items, "relations": relation_items, "reasoning_path": paths, "related_chunk_ids": chunk_ids, "graph_context": context}
