class HydeGenerator:
    def generate(self, query: str) -> str:
        return f"假设答案文档：{query}。应从定义、业务含义、单位、规则和案例中说明。"
