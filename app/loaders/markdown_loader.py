from pathlib import Path

from .base_loader import BaseLoader, LoadedDocument, decode_text


class MarkdownLoader(BaseLoader):
    def load(self, path: str | Path) -> list[LoadedDocument]:
        source = Path(path)
        return [LoadedDocument(content=decode_text(source), source=source.name, metadata={"format": "markdown"})]


class TextLoader(BaseLoader):
    def load(self, path: str | Path) -> list[LoadedDocument]:
        source = Path(path)
        return [LoadedDocument(content=decode_text(source), source=source.name, metadata={"format": "text"})]
