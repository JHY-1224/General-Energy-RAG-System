from __future__ import annotations

from .graph_context_builder import GraphContextBuilder
from .graph_store import GraphStore


class GlobalGraphRetriever:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def retrieve(self, query: str, domain: str | None = None, max_hops: int = 2, top_k_entities: int = 10, top_k_relations: int = 10) -> dict:
        seeds = self.store.search_entities(query, domain, top_k_entities)
        if not seeds:
            seeds = self.store.search_entities("", domain, top_k_entities)
        entities = {item.entity_id: item for item in seeds}
        relations = {}
        paths: list[str] = []
        for seed in seeds:
            neighborhood = self.store.get_neighbors(seed.entity_id, max(2, max_hops))
            entities.update({item.entity_id: item for item in neighborhood["entities"]})
            relations.update({item.relation_id: item for item in neighborhood["relations"]})
            paths.extend(neighborhood["reasoning_paths"])
        selected_entities = list(entities.values())[:top_k_entities]
        selected_relations = sorted(relations.values(), key=lambda item: -item.confidence)[:top_k_relations]
        chunk_ids = list(dict.fromkeys(chunk for item in selected_entities + selected_relations for chunk in item.source_chunk_ids))
        context = GraphContextBuilder().build(self.store, selected_entities, selected_relations, paths, chunk_ids)
        return {
            "entities": selected_entities,
            "relations": selected_relations,
            "reasoning_path": list(dict.fromkeys(paths)),
            "related_chunk_ids": chunk_ids,
            "graph_context": context,
        }
