from __future__ import annotations

from collections import defaultdict
from statistics import mean

from app.core.models import QueryOptions, QueryRequest
from app.evaluation.ragas_evaluator import RagasEvaluator
from app.evaluation.report_generator import ReportGenerator
from app.evaluation.retrieval_metrics import calculate_retrieval_metrics


class ExperimentRunner:
    def __init__(self, engine) -> None:
        self.engine = engine

    def run(self, name: str, cases: list, options: QueryOptions, write_report: bool = True) -> dict:
        totals: dict[str, list[float]] = defaultdict(list)
        category_totals: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        failed_cases: list[dict] = []
        traces = []
        for case in cases:
            trace = self.engine.query(QueryRequest(question=case.query, options=options))
            traces.append(trace.trace_id)
            retrieved = list(dict.fromkeys(hit.doc_id for hit in trace.reranked_docs))
            retrieval_metrics = calculate_retrieval_metrics(retrieved, case.gold_doc_ids, case.relevance) if case.gold_doc_ids else {}
            ragas_metrics = RagasEvaluator().evaluate(case.query, trace.answer, trace.compressed_context, case.ground_truth)
            for key, value in {**retrieval_metrics, **ragas_metrics}.items():
                if value is not None:
                    totals[key].append(float(value))
                    category_totals[case.category][key].append(float(value))
            for key, value in trace.latency_ms.items():
                totals[f"latency_{key}_ms"].append(value)
            totals["input_tokens"].append(trace.token_usage.get("input_tokens", 0))
            totals["output_tokens"].append(trace.token_usage.get("output_tokens", 0))
            totals["cost_total"].append(trace.cost.get("total", 0.0))
            if case.gold_doc_ids and not retrieval_metrics.get("hit_at_5", 0.0):
                failed_cases.append({"query_id": case.query_id, "query": case.query, "reason": "gold document not found in Top5"})
        report = {
            "experiment": name,
            "case_count": len(cases),
            "options": options.model_dump(),
            "metrics": {key: round(mean(values), 4) for key, values in totals.items() if values},
            "category_metrics": {
                category: {key: round(mean(values), 4) for key, values in metrics.items() if values}
                for category, metrics in category_totals.items()
            },
            "failed_cases": failed_cases,
            "trace_ids": traces,
        }
        report["report_files"] = ReportGenerator().write(name, report) if write_report else {}
        return report
