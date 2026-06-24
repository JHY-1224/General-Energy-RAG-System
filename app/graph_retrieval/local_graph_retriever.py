from __future__ import annotations

from .graph_context_builder import GraphContextBuilder
from .graph_store import GraphStore


class LocalGraphRetriever:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def retrieve(self, query: str, domain: str | None = None, max_hops: int = 2, top_k_entities: int = 10, top_k_relations: int = 10) -> dict:
        matched = self.store.search_entities(query, domain, top_k_entities)
        entities = {item.entity_id: item for item in matched}
        relations = {}
        reasoning_paths: list[str] = []
        for entity in matched:
            neighborhood = self.store.get_neighbors(entity.entity_id, max_hops)
            entities.update({item.entity_id: item for item in neighborhood["entities"]})
            relations.update({item.relation_id: item for item in neighborhood["relations"]})
            reasoning_paths.extend(neighborhood["reasoning_paths"])
        selected_relations = list(relations.values())[:top_k_relations]
        chunk_ids = list(dict.fromkeys(chunk for item in list(entities.values()) + selected_relations for chunk in item.source_chunk_ids))
        entity_items = list(entities.values())[: max(top_k_entities, len(matched))]
        context = GraphContextBuilder().build(self.store, entity_items, selected_relations, reasoning_paths, chunk_ids)
        return {
            "entities": entity_items,
            "relations": selected_relations,
            "reasoning_path": list(dict.fromkeys(reasoning_paths)),
            "related_chunk_ids": chunk_ids,
            "graph_context": context,
        }
