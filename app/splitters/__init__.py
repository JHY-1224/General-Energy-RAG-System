from .business_object_splitter import BusinessObjectSplitter
from .markdown_header_splitter import MarkdownHeaderSplitter
from .parent_child_splitter import ParentChildSplitter
from .recursive_splitter import RecursiveSplitter


def get_splitter(name: str, chunk_size: int = 700, chunk_overlap: int = 120):
    normalized = name.lower().replace("-", "_")
    if normalized in {"parent_child", "parentchild"}:
        return ParentChildSplitter(child_size=chunk_size, overlap=chunk_overlap)
    if normalized in {"markdown", "markdown_header"}:
        return MarkdownHeaderSplitter()
    if normalized in {"business", "business_object", "semantic"}:
        return BusinessObjectSplitter()
    return RecursiveSplitter(chunk_size, chunk_overlap)
