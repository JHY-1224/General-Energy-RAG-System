from __future__ import annotations

import hashlib
import re

from app.core.models import EnergyEntity, RagChunk

from .energy_schema import normalize_domain, normalize_entity_name


DOMAIN_ENTITIES: dict[str, dict[str, list[str]]] = {
    "wind_oam": {
        "Variable": ["AccX", "AccY", "WindSpeed", "GridPower", "GeneratorSpeed", "Pitch1Position", "Pitch2Position", "Pitch3Position"],
        "FaultType": ["过速", "塔架共振", "加速度故障", "变桨异常", "偏航异常", "传感器异常", "机舱横向振动"],
        "Component": ["风机", "塔架", "机舱", "叶轮", "变桨系统", "偏航系统"],
        "Feature": ["0-5Hz 频谱能量异常", "0-5Hz", "频谱能量", "主频峰值", "RMS"],
    },
    "load_forecast": {
        "Feature": ["lag_1", "lag_4", "lag_96", "rolling_mean_96", "hour", "day_of_week", "is_weekend"],
        "Model": ["LightGBM", "XGBoost", "RandomForest", "LSTM", "TCN"],
        "Metric": ["MAE", "RMSE", "MAPE", "峰值误差"],
        "Scenario": ["负荷预测", "日周期建模"],
    },
    "storage_ems": {
        "System": ["EMS", "BMS", "PCS", "储能系统"],
        "Variable": ["SOC", "SOH"],
        "Scenario": ["削峰填谷", "储能削峰填谷", "需量管理", "告警归因", "储能运行管理"],
        "Strategy": ["充放电策略", "储能充放电策略"],
    },
}

CANONICAL_NAMES = {
    "削峰填谷": "储能削峰填谷",
    "充放电策略": "储能充放电策略",
    "0-5Hz": "0-5Hz 频谱能量异常",
}


def entity_id(domain: str, entity_type: str, name: str) -> str:
    key = f"{domain}:{entity_type}:{normalize_entity_name(name).lower()}"
    return f"ent_{hashlib.sha1(key.encode('utf-8')).hexdigest()[:12]}"


class EntityExtractor:
    def extract(self, chunk: RagChunk) -> list[EnergyEntity]:
        domain = normalize_domain(str(chunk.metadata.get("domain", "")))
        content = f"{chunk.content} {' '.join(map(str, chunk.metadata.get('variables', [])))}"
        entities: dict[str, EnergyEntity] = {}
        for entity_type, names in DOMAIN_ENTITIES.get(domain, {}).items():
            for name in names:
                pattern = re.escape(name)
                flags = re.IGNORECASE if re.search(r"[A-Za-z]", name) else 0
                if re.search(pattern, content, flags):
                    normalized = normalize_entity_name(CANONICAL_NAMES.get(name, name))
                    item = EnergyEntity(
                        entity_id=entity_id(domain, entity_type, normalized),
                        name=normalized,
                        entity_type=entity_type,
                        domain=domain,
                        source_chunk_ids=[chunk.chunk_id],
                        metadata={"source": chunk.metadata.get("source", ""), "doc_id": chunk.doc_id},
                    )
                    entities[item.entity_id] = item
        return list(entities.values())
