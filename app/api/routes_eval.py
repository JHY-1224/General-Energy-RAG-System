from pathlib import Path
import json
import re

from fastapi import APIRouter, Body, HTTPException, Query, Request
from fastapi.responses import FileResponse

from app.api.dependencies import engine
from app.core.models import EvalCase, EvalRunRequest
from app.evaluation.eval_dataset import EvalDataset
from app.evaluation.experiment_runner import ExperimentRunner
from app.evaluation.ragas_diagnostics import (
    EVALUATION_DATASETS,
    EVALUATION_RUNS,
    SAMPLE_RESULTS,
    build_evaluation_summary,
    diagnose_scores,
)


router = APIRouter(prefix="/api/v2/eval", tags=["RAG v2 Evaluation"])
evaluation_router = APIRouter(prefix="/api/v1/evaluation", tags=["RAGAS Evaluation Center"])
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


def _load_report_payloads() -> list[dict]:
    if not REPORT_DIR.is_dir():
        return []
    payloads: list[dict] = []
    for path in sorted(REPORT_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("metrics") or payload.get("sample_results"):
            payloads.append(payload)
    return payloads


def _run_record_from_report(payload: dict) -> dict:
    metrics = payload.get("metrics", {})
    return {
        "run_id": payload.get("run_id") or payload.get("experiment"),
        "eval_dataset": payload.get("eval_dataset") or payload.get("experiment"),
        "embedding_model": payload.get("embedding_model") or payload.get("options", {}).get("embedding"),
        "vector_db": payload.get("vector_db") or payload.get("options", {}).get("vectorstore"),
        "retriever_config": payload.get("retriever_config") or payload.get("options", {}).get("retrieval_mode"),
        "retrieval_config": payload.get("retrieval_config") or payload.get("options", {}).get("retrieval_mode"),
        "reranker_model": payload.get("reranker_model") or payload.get("options", {}).get("reranker_model"),
        "top_k": payload.get("top_k") or payload.get("options", {}).get("top_k"),
        "score_threshold": payload.get("score_threshold"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "status": payload.get("status", "completed"),
        "sample_count": payload.get("sample_count") or payload.get("case_count"),
        "avg_faithfulness": payload.get("avg_faithfulness") or metrics.get("faithfulness"),
        "avg_answer_relevancy": payload.get("avg_answer_relevancy") or metrics.get("answer_relevancy"),
        "avg_context_precision": payload.get("avg_context_precision") or metrics.get("context_precision"),
        "avg_context_recall": payload.get("avg_context_recall") or metrics.get("context_recall"),
        "report_files": payload.get("report_files", {}),
    }


def _combined_runs() -> list[dict]:
    report_runs = [_run_record_from_report(payload) for payload in _load_report_payloads()]
    seen = {item.get("run_id") for item in report_runs}
    return report_runs + [item for item in EVALUATION_RUNS if item.get("run_id") not in seen]


def _find_report(run_id: str) -> dict | None:
    for payload in _load_report_payloads():
        if payload.get("run_id") == run_id or payload.get("experiment") == run_id:
            return payload
    return None


@router.post("/run")
def run_evaluation(payload: EvalRunRequest):
    cases = EvalDataset.load(_resolve_eval_set(payload.eval_set))
    result = ExperimentRunner(engine).run(payload.experiment_name, cases, payload.options)
    result["eval_dataset"] = payload.eval_set
    return result


@router.post("/upload")
async def upload_eval_set(request: Request, filename: str = Query(...)):
    safe_name = _safe_filename(filename, ".jsonl")
    content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Evaluation file is empty")
    try:
        text = content.decode("utf-8-sig")
        cases = EvalDataset.loads(text)
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


@evaluation_router.get("/datasets")
def list_evaluation_datasets():
    return {"items": EVALUATION_DATASETS}


@evaluation_router.post("/datasets")
def create_evaluation_dataset(payload: dict = Body(...)):
    dataset_id = str(payload.get("dataset_id") or payload.get("name") or "").strip()
    samples = payload.get("samples") or []
    if not dataset_id or not isinstance(samples, list) or not samples:
        raise HTTPException(status_code=400, detail="dataset_id and non-empty samples are required")
    safe_name = _safe_filename(f"{dataset_id}.jsonl", ".jsonl")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    target = EVAL_DIR / safe_name
    if target.exists():
        raise HTTPException(status_code=409, detail="Evaluation dataset already exists")
    try:
        cases = [EvalCase.model_validate(EvalDataset.normalize(sample)) for sample in samples]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid evaluation samples: {exc}") from exc
    target.write_text("\n".join(case.model_dump_json() for case in cases) + "\n", encoding="utf-8")
    return {"dataset_id": dataset_id, "eval_set": target.as_posix(), "sample_count": len(cases)}


@evaluation_router.get("/datasets/{dataset_id}")
def get_evaluation_dataset(dataset_id: str):
    for dataset in EVALUATION_DATASETS:
        if dataset["dataset_id"] == dataset_id:
            return dataset
    safe_name = _safe_filename(f"{dataset_id}.jsonl", ".jsonl")
    target = EVAL_DIR / safe_name
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Evaluation dataset not found")
    cases = EvalDataset.load(target)
    return {
        "dataset_id": dataset_id,
        "eval_set": target.as_posix(),
        "sample_count": len(cases),
        "samples": [case.model_dump() for case in cases],
    }


@evaluation_router.post("/run")
def run_evaluation_v1(payload: EvalRunRequest):
    cases = EvalDataset.load(_resolve_eval_set(payload.eval_set))
    result = ExperimentRunner(engine).run(payload.experiment_name, cases, payload.options)
    result["eval_dataset"] = payload.eval_set
    return result


@evaluation_router.get("/runs")
def list_evaluation_runs():
    return {"items": _combined_runs()}


@evaluation_router.get("/runs/{run_id}")
def get_evaluation_run(run_id: str):
    for run in _combined_runs():
        if run.get("run_id") == run_id:
            payload = _find_report(run_id)
            return {**run, **({"report": payload} if payload else {})}
    raise HTTPException(status_code=404, detail="Evaluation run not found")


@evaluation_router.get("/runs/{run_id}/samples")
def list_run_samples(run_id: str):
    payload = _find_report(run_id)
    if payload:
        return {"items": payload.get("sample_results", [])}
    return {"items": [item for item in SAMPLE_RESULTS if item.get("run_id") == run_id]}


@evaluation_router.get("/runs/{run_id}/failures")
def list_run_failures(run_id: str):
    payload = _find_report(run_id)
    if payload:
        failures = payload.get("failed_cases") or [item for item in payload.get("sample_results", []) if item.get("failure_type")]
        return {"items": failures}
    return {"items": [item for item in SAMPLE_RESULTS if item.get("run_id") == run_id and item.get("failure_type")]}


@evaluation_router.get("/metrics/summary")
def get_metrics_summary():
    return build_evaluation_summary(_combined_runs())


@evaluation_router.post("/diagnose")
def diagnose_evaluation_scores(payload: dict = Body(...)):
    return diagnose_scores(payload)
