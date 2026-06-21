from html.parser import HTMLParser
from pathlib import Path

from .base_loader import BaseLoader, LoadedDocument, decode_text


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


class HtmlLoader(BaseLoader):
    def load(self, path: str | Path) -> list[LoadedDocument]:
        source = Path(path)
        parser = _TextExtractor()
        parser.feed(decode_text(source))
        return [LoadedDocument(content="\n".join(parser.parts), source=source.name, metadata={"format": "html"})]
