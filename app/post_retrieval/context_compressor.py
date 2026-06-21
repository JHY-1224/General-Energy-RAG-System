import re

from app.embeddings.embedding_factory import tokenize


class ContextCompressor:
    def compress(self, query: str, content: str, max_sentences: int = 4, mode: str = "auto") -> str:
        if mode == "table" or (mode == "auto" and "|" in content):
            return self._compress_table(query, content)
        if mode == "keyword":
            return self._compress_keyword(query, content, max_sentences)
        return self._compress_sentences(query, content, max_sentences)

    def _compress_sentences(self, query: str, content: str, max_sentences: int) -> str:
        sentences = [item.strip() for item in re.split(r"(?<=[。！？!?；;])", content) if item.strip()]
        if not sentences:
            return content[:800]
        query_terms = set(tokenize(query))
        scored = [(sentence, len(query_terms & set(tokenize(sentence)))) for sentence in sentences]
        selected = sorted(scored, key=lambda item: item[1], reverse=True)[:max_sentences]
        return "".join(sentence for sentence, _ in selected)[:1200]

    def _compress_keyword(self, query: str, content: str, max_sentences: int) -> str:
        terms = set(tokenize(query))
        sentences = [item.strip() for item in re.split(r"(?<=[。！？!?；;\n])", content) if item.strip()]
        selected = [item for item in sentences if terms & set(tokenize(item))]
        return "".join(selected[:max_sentences])[:1200] or content[:800]

    def _compress_table(self, query: str, content: str) -> str:
        terms = set(tokenize(query))
        rows = [row for row in content.splitlines() if row.strip()]
        if len(rows) <= 2:
            return content[:1200]
        header = rows[:2]
        matched = [row for row in rows[2:] if terms & set(tokenize(row))]
        return "\n".join(header + (matched[:12] or rows[2:6]))[:1600]
