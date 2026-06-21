import json
from pathlib import Path

from app.core.models import EvalCase


class EvalDataset:
    @staticmethod
    def load(path: str | Path) -> list[EvalCase]:
        cases: list[EvalCase] = []
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                cases.append(EvalCase.model_validate(json.loads(line)))
        return cases
