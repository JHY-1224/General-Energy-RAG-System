import json

from app.api.dependencies import engine
from app.config.loader import load_config
from app.core.models import QueryOptions
from app.evaluation.eval_dataset import EvalDataset
from app.evaluation.experiment_runner import ExperimentRunner


config = load_config("app/config/experiment_config.yaml")
cases = EvalDataset.load("data/eval_sets/energy_rag_eval.jsonl")
reports = []
for experiment in config.get("experiments", []):
    values = {key: value for key, value in experiment.items() if key != "name" and key in QueryOptions.model_fields}
    reports.append(ExperimentRunner(engine).run(experiment["name"], cases, QueryOptions.model_validate(values)))
print(json.dumps({"experiments": reports}, ensure_ascii=False, indent=2))
