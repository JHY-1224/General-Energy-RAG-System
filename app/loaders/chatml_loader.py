import json
from pathlib import Path

from .base_loader import BaseLoader, LoadedDocument, decode_text


class ChatMLLoader(BaseLoader):
    def load(self, path: str | Path) -> list[LoadedDocument]:
        source = Path(path)
        documents: list[LoadedDocument] = []
        for index, line in enumerate(decode_text(source).splitlines(), start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            messages = payload.get("messages", payload if isinstance(payload, list) else [])
            content = "\n".join(f"{item.get('role', 'unknown')}: {item.get('content', '')}" for item in messages)
            metadata = {
                "format": "chatml",
                "category": "Case",
                "case_id": payload.get("case_id", f"case_{index:04d}") if isinstance(payload, dict) else f"case_{index:04d}",
                "intent": payload.get("intent", "") if isinstance(payload, dict) else "",
                "node": payload.get("node", "") if isinstance(payload, dict) else "",
            }
            documents.append(LoadedDocument(content=content, source=source.name, metadata=metadata))
        return documents
