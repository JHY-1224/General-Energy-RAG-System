import re
from typing import Any

from app.core.models import RagChunk

from .base_splitter import BaseSplitter


class MarkdownHeaderSplitter(BaseSplitter):
    def split(self, doc_id: str, text: str, metadata: dict[str, Any]) -> list[RagChunk]:
        sections = re.split(r"(?m)^(#{1,6}\s+.+)$", text)
        chunks: list[RagChunk] = []
        title = metadata.get("section", "未分节")
        index = 1
        for part in sections:
            if part.startswith("#"):
                title = part.lstrip("# ").strip()
            elif part.strip():
                chunks.append(RagChunk(doc_id=doc_id, chunk_id=f"{doc_id}_section_{index:04d}", content=part.strip(), metadata={**metadata, "section": title}))
                index += 1
        return chunks
