from __future__ import annotations

import hashlib

from app.core.models import EnergyEntity, EnergyRelation, RagChunk


RELATION_RULES = [
    ("AccY", "机舱横向振动", "INDICATES", "wind_oam"),
    ("机舱横向振动", "塔架共振", "RELATED_TO", "wind_oam"),
    ("塔架共振", "0-5Hz 频谱能量异常", "EVIDENCED_BY", "wind_oam"),
    ("lag_96", "日周期建模", "USED_FOR", "load_forecast"),
    ("lag_96", "负荷预测", "INPUT_FEATURE_OF", "load_forecast"),
    ("负荷预测", "储能削峰填谷", "SUPPORTS", "cross_domain"),
    ("SOC", "储能充放电策略", "CONSTRAINED_BY", "storage_ems"),
    ("PCS", "储能系统", "PART_OF", "storage_ems"),
    ("EMS", "储能运行管理", "APPLIED_IN", "storage_ems"),
    ("BMS", "EMS", "SUPPORTS", "storage_ems"),
    ("PCS", "EMS", "SUPPORTS", "storage_ems"),
]


def relation_id(source_id: str, target_id: str, relation_type: str) -> str:
    key = f"{source_id}:{relation_type}:{target_id}"
    return f"rel_{hashlib.sha1(key.encode('utf-8')).hexdigest()[:12]}"


class RelationExtractor:
    def extract(self, chunk: RagChunk, entities: list[EnergyEntity]) -> list[EnergyRelation]:
        by_name = {entity.name.lower(): entity for entity in entities}
        relations: dict[str, EnergyRelation] = {}
        for source_name, target_name, relation_type, rule_domain in RELATION_RULES:
            source = by_name.get(source_name.lower())
            target = by_name.get(target_name.lower())
            if not source or not target:
                continue
            item = EnergyRelation(
                relation_id=relation_id(source.entity_id, target.entity_id, relation_type),
                source_entity=source.entity_id,
                target_entity=target.entity_id,
                relation_type=relation_type,
                domain=source.domain if rule_domain == "cross_domain" else rule_domain,
                description=f"{source.name} {relation_type} {target.name}",
                source_chunk_ids=[chunk.chunk_id],
                confidence=0.95,
            )
            relations[item.relation_id] = item

        if len(entities) > 1:
            ordered = sorted(entities, key=lambda item: (item.entity_type, item.name))
            for source, target in zip(ordered, ordered[1:]):
                item = EnergyRelation(
                    relation_id=relation_id(source.entity_id, target.entity_id, "RELATED_TO"),
                    source_entity=source.entity_id,
                    target_entity=target.entity_id,
                    relation_type="RELATED_TO",
                    domain=source.domain,
                    description=f"{source.name} 与 {target.name} 出现在同一知识片段",
                    source_chunk_ids=[chunk.chunk_id],
                    confidence=0.65,
                    metadata={"rule": "chunk_cooccurrence"},
                )
                relations.setdefault(item.relation_id, item)
        return list(relations.values())
