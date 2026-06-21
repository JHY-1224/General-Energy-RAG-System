from __future__ import annotations

from typing import Any

from app.core.models import RagChunk

from .base_splitter import BaseSplitter


class RecursiveSplitter(BaseSplitter):
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120) -> None:
        self.chunk_size = max(200, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size // 2))

    def split(self, doc_id: str, text: str, metadata: dict[str, Any]) -> list[RagChunk]:
        chunks: list[RagChunk] = []
        start = 0
        index = 1
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            content = text[start:end].strip()
            if content:
                chunk_metadata = {**metadata, "position": index, "chunk_type": metadata.get("chunk_type", "普通文本")}
                chunks.append(RagChunk(doc_id=doc_id, chunk_id=f"{doc_id}_chunk_{index:04d}", content=content, metadata=chunk_metadata))
            if end == len(text):
                break
            start = end - self.chunk_overlap
            index += 1
        return chunks
