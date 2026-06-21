from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class ExtractedTable:
    table_id: str
    content: str
    section: str


class TableExtractor:
    markdown_pattern = re.compile(r"(?:^|\n)(\|[^\n]+\|\n\|(?:\s*:?-+:?\s*\|)+\n(?:\|[^\n]+\|\n?)+)", re.MULTILINE)
    html_pattern = re.compile(r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL)

    def extract(self, text: str, section: str = "未分节") -> tuple[str, list[ExtractedTable]]:
        tables: list[ExtractedTable] = []

        def replace(match: re.Match[str]) -> str:
            table_id = f"tbl_{uuid4().hex[:10]}"
            tables.append(ExtractedTable(table_id=table_id, content=match.group(0).strip(), section=section))
            return f"\n[{table_id}]\n"

        text = self.html_pattern.sub(replace, text)
        text = self.markdown_pattern.sub(replace, text)
        return text, tables
