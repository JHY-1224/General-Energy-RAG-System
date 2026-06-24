from __future__ import annotations

from app.core.models import EnergyEntity, EnergyRelation

from .graph_store import GraphStore


class GraphContextBuilder:
    def build(
        self,
        store: GraphStore,
        entities: list[EnergyEntity],
        relations: list[EnergyRelation],
        reasoning_paths: list[str],
        source_chunk_ids: list[str],
    ) -> str:
        relation_lines = []
        for index, relation in enumerate(relations, start=1):
            source = store.get_entity(relation.source_entity)
            target = store.get_entity(relation.target_entity)
            if source and target:
                relation_lines.append(f"{index}. {source.name} --{relation.relation_type}--> {target.name}")
        entity_summary = "、".join(f"{item.name}({item.entity_type})" for item in entities)
        lines = ["【图增强关系上下文】", *(relation_lines or ["未发现显式关系"]), "", "【关联实体】", entity_summary or "无"]
        lines.extend(["", "【关联知识片段】", f"source_chunk_ids: {', '.join(source_chunk_ids) or '无'}"])
        if reasoning_paths:
            lines.extend(["", "【业务链路解释】", *reasoning_paths])
        return "\n".join(lines)
