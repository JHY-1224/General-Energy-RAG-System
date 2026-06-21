from pathlib import Path

from .base_loader import BaseLoader, LoadedDocument


class PdfLoader(BaseLoader):
    def load(self, path: str | Path) -> list[LoadedDocument]:
        source = Path(path)
        try:
            import fitz

            pages = [page.get_text("markdown") or page.get_text() for page in fitz.open(source)]
            content = "\n\n".join(f"## Page {index + 1}\n{page}" for index, page in enumerate(pages))
            parser = "pymupdf"
        except ModuleNotFoundError:
            content = f"# {source.stem}\n\nPDF 已保存，安装 pymupdf 后可转换为 Markdown。"
            parser = "placeholder"
        return [LoadedDocument(content=content, source=source.name, metadata={"format": "pdf", "parser": parser})]
