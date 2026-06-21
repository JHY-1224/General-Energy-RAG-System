from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LoadedDocument:
    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseLoader:
    def load(self, path: str | Path) -> list[LoadedDocument]:
        raise NotImplementedError


def decode_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "gb18030", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
