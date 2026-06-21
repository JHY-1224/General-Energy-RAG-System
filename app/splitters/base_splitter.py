from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.models import RagChunk


class BaseSplitter(ABC):
    @abstractmethod
    def split(self, doc_id: str, text: str, metadata: dict[str, Any]) -> list[RagChunk]:
        raise NotImplementedError
