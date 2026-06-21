from app.core.models import RetrievalHit


class ParentChildIndex:
    def recover(self, hits: list[RetrievalHit]) -> list[RetrievalHit]:
        for hit in hits:
            parent_content = hit.metadata.get("parent_content")
            if parent_content:
                hit.content = parent_content
                hit.metadata["parent_recovered"] = True
        return hits
