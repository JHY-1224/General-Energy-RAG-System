from pathlib import Path
import re

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse

from app.api.dependencies import engine
from app.core.models import EvalCase, EvalRunRequest
from app.evaluation.eval_dataset import EvalDataset
from app.evaluation.experiment_runner import ExperimentRunner


router = APIRouter(prefix="/api/v2/eval", tags=["RAG v2 Evaluation"])
EVAL_DIR = Path("data/eval_sets")
REPORT_DIR = Path("reports/eval_reports")


def _safe_filename(filename: str, suffix: str) -> str:
    name = Path(filename).name
    if name != filename or Path(name).suffix.lower() != suffix:
        raise HTTPException(status_code=400, detail=f"Only {suffix} files are supported")
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not safe or safe.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return safe


def _resolve_eval_set(path: str) -> Path:
    target = Path(path).resolve()
    root = EVAL_DIR.resolve()
    if root not in target.parents or not target.is_file():
        raise HTTPException(status_code=404, detail="Evaluation set not found")
    return target


@router.post("/run")
def run_evaluation(payload: EvalRunRequest):
    cases = EvalDataset.load(_resolve_eval_set(payload.eval_set))
    return ExperimentRunner(engine).run(payload.experiment_name, cases, payload.options)


@router.post("/upload")
async def upload_eval_set(request: Request, filename: str = Query(...)):
    safe_name = _safe_filename(filename, ".jsonl")
    content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Evaluation file is empty")
    try:
        text = content.decode("utf-8-sig")
        lines = [line for line in text.splitlines() if line.strip()]
        cases = [EvalCase.model_validate_json(line) for line in lines]
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid JSONL evaluation set: {exc}") from exc
    if not cases:
        raise HTTPException(status_code=422, detail="Evaluation set contains no cases")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    target = EVAL_DIR / safe_name
    target.write_text("\n".join(case.model_dump_json() for case in cases) + "\n", encoding="utf-8")
    return {"eval_set": target.as_posix(), "case_count": len(cases), "filename": safe_name}


@router.get("/reports/{filename}")
def download_report(filename: str):
    safe_name = _safe_filename(filename, Path(filename).suffix.lower())
    if Path(safe_name).suffix.lower() not in {".json", ".csv", ".md"}:
        raise HTTPException(status_code=400, detail="Unsupported report format")
    target = (REPORT_DIR / safe_name).resolve()
    if target.parent != REPORT_DIR.resolve() or not target.is_file():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(target, filename=safe_name)
