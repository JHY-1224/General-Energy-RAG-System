from pathlib import Path
from typing import Any


class MetadataEnricher:
    def enrich(self, source: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        data = dict(metadata or {})
        data.setdefault("source", Path(source).name)
        data.setdefault("domain", "电气工程基础")
        data.setdefault("task", "知识问答")
        data.setdefault("doc_type", "技术资料")
        data.setdefault("chunk_type", "普通文本")
        data.setdefault("section", "未分节")
        data.setdefault("page", None)
        return data
