from fastapi import APIRouter

from app.api.dependencies import engine
from app.config.loader import load_config
from app.core.models import QueryOptions
from app.evaluation.eval_dataset import EvalDataset
from app.evaluation.experiment_runner import ExperimentRunner
from app.evaluation.report_generator import ReportGenerator


router = APIRouter(prefix="/api/v2/experiments", tags=["RAG v2 Experiments"])


@router.post("/run")
def run_experiments(config_path: str = "app/config/experiment_config.yaml", eval_set: str = "data/eval_sets/energy_rag_eval.jsonl"):
    config = load_config(config_path)
    cases = EvalDataset.load(eval_set)
    reports = []
    for experiment in config.get("experiments", []):
        values = {key: value for key, value in experiment.items() if key != "name" and key in QueryOptions.model_fields}
        reports.append(ExperimentRunner(engine).run(experiment["name"], cases, QueryOptions.model_validate(values)))
    return {"experiments": reports, "comparison": ReportGenerator().write_comparison(reports)}
