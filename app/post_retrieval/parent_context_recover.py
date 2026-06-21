class ParentContextRecover:
    def recover(self, hits: list) -> list:
        for hit in hits:
            parent = hit.metadata.get("parent_content")
            if parent:
                hit.metadata["child_content"] = hit.content
                hit.content = parent
                hit.metadata["parent_recovered"] = True
        return hits
