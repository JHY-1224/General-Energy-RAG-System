from __future__ import annotations


def _rate(actual: set[str], expected: set[str]) -> float:
    return round(len(actual & expected) / len(expected), 4) if expected else 0.0


def calculate_graph_metrics(
    entity_ids: list[str],
    relation_ids: list[str],
    reasoning_path: list[str],
    source_chunk_ids: list[str],
    expected_entity_ids: list[str] | None = None,
    expected_relation_ids: list[str] | None = None,
    expected_chunk_ids: list[str] | None = None,
) -> dict[str, float]:
    expected_entities = set(expected_entity_ids or [])
    expected_relations = set(expected_relation_ids or [])
    expected_chunks = set(expected_chunk_ids or [])
    return {
        "entity_hit_rate": _rate(set(entity_ids), expected_entities),
        "relation_hit_rate": _rate(set(relation_ids), expected_relations),
        "multi_hop_coverage": round(min(1.0, len(reasoning_path) / 2), 4),
        "graph_context_coverage": round(min(1.0, (len(entity_ids) + len(relation_ids)) / 10), 4),
        "graph_source_citation_rate": _rate(set(source_chunk_ids), expected_chunks) if expected_chunks else float(bool(source_chunk_ids)),
    }
