from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "embedding": "bge-large-zh",
    "vectorstore": "chroma",
    "indexing": {
        "vector": True,
        "bm25": True,
        "hybrid": True,
        "metadata": True,
        "parent_child": True,
        "summary": False,
    },
    "pre_retrieval": {
        "query_rewrite": True,
        "query_expansion": True,
        "query_transformation": True,
        "metadata_router": True,
        "multi_query": False,
        "hyde": False,
    },
    "retrieval": {
        "mode": "hybrid",
        "top_k": 10,
        "vector_weight": 0.7,
        "bm25_weight": 0.3,
    },
    "post_retrieval": {
        "rerank": True,
        "reranker_model": "score-fallback",
        "compression": True,
        "compression_mode": "auto",
        "deduplicate": True,
        "filter": True,
        "parent_recovery": True,
        "rag_fusion": False,
    },
    "generation": {"final_context_top_k": 5},
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    if not path:
        return deepcopy(DEFAULT_CONFIG)
    config_path = Path(path)
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)
    text = config_path.read_text(encoding="utf-8")
    try:
        import yaml

        loaded = yaml.safe_load(text) or {}
    except ModuleNotFoundError:
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            return deepcopy(DEFAULT_CONFIG)
    return deep_merge(DEFAULT_CONFIG, loaded)
