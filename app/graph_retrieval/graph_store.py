from __future__ import annotations

import json
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

from app.core.models import EnergyEntity, EnergyRelation

from .energy_schema import normalize_domain, normalize_entity_name, validate_entity_type, validate_relation_type


class GraphStore:
    def __init__(self, path: str | Path = "data/graph/energy_graph.json") -> None:
        self.path = Path(path)
        self.entities: dict[str, EnergyEntity] = {}
        self.relations: dict[str, EnergyRelation] = {}
        self.last_updated: str | None = None

    def add_entity(self, entity: EnergyEntity) -> EnergyEntity:
        if not validate_entity_type(entity.entity_type):
            raise ValueError(f"Unsupported entity type: {entity.entity_type}")
        existing = self.entities.get(entity.entity_id)
        if existing:
            merged = existing.model_copy(deep=True)
            merged.source_chunk_ids = list(dict.fromkeys(existing.source_chunk_ids + entity.source_chunk_ids))
            merged.metadata = {**existing.metadata, **entity.metadata}
            if entity.description and not merged.description:
                merged.description = entity.description
            self.entities[entity.entity_id] = merged
        else:
            self.entities[entity.entity_id] = entity.model_copy(deep=True)
        return self.entities[entity.entity_id]

    def add_relation(self, relation: EnergyRelation) -> EnergyRelation:
        if not validate_relation_type(relation.relation_type):
            raise ValueError(f"Unsupported relation type: {relation.relation_type}")
        if relation.source_entity not in self.entities or relation.target_entity not in self.entities:
            raise ValueError("Relation endpoints must exist before adding a relation")
        existing = self.relations.get(relation.relation_id)
        if existing:
            merged = existing.model_copy(deep=True)
            merged.source_chunk_ids = list(dict.fromkeys(existing.source_chunk_ids + relation.source_chunk_ids))
            merged.confidence = max(existing.confidence, relation.confidence)
            merged.metadata = {**existing.metadata, **relation.metadata}
            self.relations[relation.relation_id] = merged
        else:
            self.relations[relation.relation_id] = relation.model_copy(deep=True)
        return self.relations[relation.relation_id]

    def get_entity(self, entity_id: str) -> EnergyEntity | None:
        return self.entities.get(entity_id)

    def search_entities(
        self,
        query: str,
        domain: str | None = None,
        top_k: int = 10,
        entity_type: str | None = None,
    ) -> list[EnergyEntity]:
        normalized_query = normalize_entity_name(query).lower()
        query_terms = {term for term in normalized_query.replace("/", " ").split() if term}
        normalized_domain = normalize_domain(domain) if domain else None
        scored: list[tuple[float, EnergyEntity]] = []
        for entity in self.entities.values():
            if normalized_domain and entity.domain != normalized_domain:
                continue
            if entity_type and entity.entity_type != entity_type:
                continue
            name = entity.name.lower()
            score = 0.0
            if name and name in normalized_query:
                score += 5.0
            if normalized_query and normalized_query in name:
                score += 3.0
            score += sum(1.0 for term in query_terms if term in name or term in entity.description.lower())
            if not normalized_query:
                score = 1.0
            if score > 0:
                scored.append((score, entity))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [entity.model_copy(deep=True) for _, entity in scored[: max(1, top_k)]]

    def get_relations(
        self,
        entity_id: str | None = None,
        domain: str | None = None,
        relation_type: str | None = None,
    ) -> list[EnergyRelation]:
        normalized_domain = normalize_domain(domain) if domain else None
        items = []
        for relation in self.relations.values():
            if entity_id and entity_id not in {relation.source_entity, relation.target_entity}:
                continue
            if normalized_domain and relation.domain not in {normalized_domain, "cross_domain"}:
                continue
            if relation_type and relation.relation_type != relation_type:
                continue
            items.append(relation.model_copy(deep=True))
        return sorted(items, key=lambda item: (-item.confidence, item.relation_id))

    def get_neighbors(self, entity_id: str, max_hops: int = 1) -> dict:
        visited = {entity_id}
        frontier = {entity_id}
        relation_ids: set[str] = set()
        reasoning_paths: list[str] = []
        for hop in range(1, max(1, max_hops) + 1):
            next_frontier: set[str] = set()
            for current in frontier:
                for relation in self.get_relations(entity_id=current):
                    relation_ids.add(relation.relation_id)
                    neighbor = relation.target_entity if relation.source_entity == current else relation.source_entity
                    if neighbor not in visited:
                        next_frontier.add(neighbor)
                        source = self.entities.get(relation.source_entity)
                        target = self.entities.get(relation.target_entity)
                        if source and target:
                            reasoning_paths.append(f"hop {hop}: {source.name} --{relation.relation_type}--> {target.name}")
            visited.update(next_frontier)
            frontier = next_frontier
            if not frontier:
                break
        return {
            "entities": [self.entities[item].model_copy(deep=True) for item in visited if item in self.entities],
            "relations": [self.relations[item].model_copy(deep=True) for item in relation_ids if item in self.relations],
            "reasoning_paths": reasoning_paths,
        }

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        self.last_updated = datetime.now().isoformat(timespec="seconds")
        payload = {
            "version": 1,
            "last_updated": self.last_updated,
            "entities": [item.model_dump() for item in self.entities.values()],
            "relations": [item.model_dump() for item in self.relations.values()],
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.path = target
        return target

    @classmethod
    def load(cls, path: str | Path = "data/graph/energy_graph.json") -> "GraphStore":
        store = cls(path)
        target = Path(path)
        if not target.is_file():
            return store
        payload = json.loads(target.read_text(encoding="utf-8"))
        for item in payload.get("entities", []):
            store.add_entity(EnergyEntity.model_validate(item))
        for item in payload.get("relations", []):
            store.add_relation(EnergyRelation.model_validate(item))
        store.last_updated = payload.get("last_updated")
        return store

    def status(self) -> dict:
        domains = sorted({entity.domain for entity in self.entities.values()})
        entity_types = Counter(entity.entity_type for entity in self.entities.values())
        relation_types = Counter(relation.relation_type for relation in self.relations.values())
        return {
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "graph_path": self.path.as_posix(),
            "last_updated": self.last_updated,
            "supported_domains": domains,
            "average_relation_hops": self._average_relation_hops(),
            "entity_type_distribution": dict(entity_types.most_common()),
            "relation_type_distribution": dict(relation_types.most_common()),
        }

    def _average_relation_hops(self) -> float:
        if len(self.entities) < 2 or not self.relations:
            return 0.0
        adjacency: dict[str, set[str]] = {entity_id: set() for entity_id in self.entities}
        for relation in self.relations.values():
            adjacency[relation.source_entity].add(relation.target_entity)
            adjacency[relation.target_entity].add(relation.source_entity)
        distances: list[int] = []
        entity_ids = list(self.entities)
        for index, start in enumerate(entity_ids):
            discovered = {start: 0}
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for neighbor in adjacency[current]:
                    if neighbor not in discovered:
                        discovered[neighbor] = discovered[current] + 1
                        queue.append(neighbor)
            distances.extend(discovered[target] for target in entity_ids[index + 1 :] if target in discovered)
        return round(sum(distances) / len(distances), 2) if distances else 0.0
