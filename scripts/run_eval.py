import json

from app.api.dependencies import engine
from app.core.models import QueryOptions
from app.evaluation.eval_dataset import EvalDataset
from app.evaluation.experiment_runner import ExperimentRunner


cases = EvalDataset.load("data/eval_sets/energy_rag_eval.jsonl")
print(json.dumps(ExperimentRunner(engine).run("script_eval", cases, QueryOptions()), ensure_ascii=False, indent=2))
