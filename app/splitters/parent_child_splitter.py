from typing import Any

from app.core.models import RagChunk

from .base_splitter import BaseSplitter
from .recursive_splitter import RecursiveSplitter


class ParentChildSplitter(BaseSplitter):
    def __init__(self, child_size: int = 420, overlap: int = 80, parent_size: int = 1400) -> None:
        self.child = RecursiveSplitter(child_size, overlap)
        self.parent_size = max(parent_size, child_size)

    def split(self, doc_id: str, text: str, metadata: dict[str, Any]) -> list[RagChunk]:
        parents = RecursiveSplitter(self.parent_size, 0).split(doc_id, text, {**metadata, "chunk_type": "Parent"})
        children: list[RagChunk] = []
        for parent_index, parent in enumerate(parents, start=1):
            parent_id = f"{doc_id}_parent_{parent_index:04d}"
            for child in self.child.split(doc_id, parent.content, {**metadata, "chunk_type": "Child", "parent_id": parent_id}):
                child.parent_id = parent_id
                child.parent_content = parent.content
                child.chunk_id = f"{parent_id}_{child.chunk_id.rsplit('_', 1)[-1]}"
                children.append(child)
        return children
