import hashlib


class Deduplicator:
    def deduplicate(self, hits: list) -> list:
        seen: set[str] = set()
        unique = []
        for hit in hits:
            key = hit.chunk_id or hashlib.sha1(hit.content.encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            unique.append(hit)
        return unique
