import json
from pathlib import Path

from app.core.models import EvalCase


class EvalDataset:
    @staticmethod
    def normalize(raw: dict) -> dict:
        data = dict(raw)
        if "query" not in data and "question" in data:
            data["query"] = data["question"]
        if "query_id" not in data and "eval_id" in data:
            data["query_id"] = data["eval_id"]
        if "category" not in data:
            data["category"] = data.get("domain") or data.get("doc_type") or "evaluation"
        if "gold_doc_ids" not in data and "reference_context_ids" in data:
            data["gold_doc_ids"] = data["reference_context_ids"]
        return data

    @staticmethod
    def load(path: str | Path) -> list[EvalCase]:
        return EvalDataset.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def loads(text: str) -> list[EvalCase]:
        cases: list[EvalCase] = []
        for line in text.splitlines():
            if line.strip():
                cases.append(EvalCase.model_validate(EvalDataset.normalize(json.loads(line))))
        return cases
