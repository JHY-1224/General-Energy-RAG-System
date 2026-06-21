class QueryRewriter:
    def rewrite(self, query: str, conversation_context: str = "") -> str:
        compact = " ".join(query.split())
        if any(word in compact for word in ("这个", "那个", "它")) and conversation_context:
            return f"结合上下文「{conversation_context[-160:]}」，请检索说明：{compact}"
        return compact
