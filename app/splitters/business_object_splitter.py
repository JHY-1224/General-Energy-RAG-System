import re
from typing import Any

from app.core.models import RagChunk

from .base_splitter import BaseSplitter


class BusinessObjectSplitter(BaseSplitter):
    def split(self, doc_id: str, text: str, metadata: dict[str, Any]) -> list[RagChunk]:
        objects = [item.strip() for item in re.split(r"\n(?=(?:变量|故障|规则|案例|任务|字段)[:：])", text) if item.strip()]
        return [RagChunk(doc_id=doc_id, chunk_id=f"{doc_id}_object_{index:04d}", content=item, metadata={**metadata, "chunk_type": "业务对象"}) for index, item in enumerate(objects, start=1)]
