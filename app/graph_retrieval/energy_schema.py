from __future__ import annotations

import re
import unicodedata


ENTITY_TYPES = {
    "Variable",
    "FaultType",
    "Component",
    "Feature",
    "Model",
    "Metric",
    "System",
    "Scenario",
    "Strategy",
    "MarketMechanism",
    "ReportModule",
}

RELATION_TYPES = {
    "RELATED_TO",
    "INDICATES",
    "USED_FOR",
    "INPUT_FEATURE_OF",
    "EVALUATED_BY",
    "SUPPORTS",
    "CONSTRAINED_BY",
    "PART_OF",
    "APPLIED_IN",
    "CAUSES",
    "EVIDENCED_BY",
}

SUPPORTED_DOMAINS = ["wind_oam", "load_forecast", "storage_ems"]
FUTURE_DOMAINS = ["pv_forecast", "power_trading"]

DOMAIN_ALIASES = {
    "风电故障诊断": "wind_oam",
    "风电智能运维": "wind_oam",
    "wind_oam": "wind_oam",
    "区域负荷预测": "load_forecast",
    "负荷预测": "load_forecast",
    "load_forecast": "load_forecast",
    "储能EMS": "storage_ems",
    "储能 EMS": "storage_ems",
    "storage_ems": "storage_ems",
}


def normalize_entity_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKC", name or "").strip()
    return re.sub(r"\s+", " ", normalized)


def normalize_domain(domain: str | None) -> str:
    value = normalize_entity_name(domain or "")
    return DOMAIN_ALIASES.get(value, value or "general")


def validate_entity_type(entity_type: str) -> bool:
    return entity_type in ENTITY_TYPES


def validate_relation_type(relation_type: str) -> bool:
    return relation_type in RELATION_TYPES
