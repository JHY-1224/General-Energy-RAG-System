class RagChain:
    def generate(self, question: str, contexts: list[str], sources: list[str]) -> str:
        if not contexts:
            return "当前配置未召回可用知识片段，请放宽 metadata filter、提高 TopK 或切换 Hybrid Search。"
        evidence = "\n".join(f"- {item}" for item in contexts[:5])
        source_text = "、".join(sources[:5])
        return (
            f"【回答结论】针对“{question}”，应结合以下知识片段进行判断。\n"
            f"【检索依据】\n{evidence}\n"
            "【人工复核提示】当前回答由本地可配置 RAG fallback 生成，生产结论需工程师复核。\n"
            f"【引用来源】{source_text}"
        )
