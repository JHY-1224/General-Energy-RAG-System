from __future__ import annotations


class QueryExpander:
    SYNONYMS = {
        "实际功率": ["并网功率", "grid power", "active power", "var_name_pow"],
        "叶轮转速": ["rotor speed", "发电机转速", "gen_speed", "传动比"],
        "AccY": ["Y 向加速度", "机舱横向振动", "tower acceleration y"],
        "塔架共振": ["一阶固有频率", "FFT 峰值", "RMS 阈值"],
        "lag_96": ["前一天同一时刻", "96 个 15 分钟采样点", "日周期特征"],
        "SOC": ["荷电状态", "state of charge"],
        "SOH": ["健康状态", "state of health"],
    }

    def expand(self, query: str) -> list[str]:
        expansions = [query]
        additions: list[str] = []
        for term, synonyms in self.SYNONYMS.items():
            if term.lower() in query.lower():
                additions.extend(synonyms)
        if additions:
            expansions.append(f"{query} {' '.join(additions)}")
        return list(dict.fromkeys(expansions))
