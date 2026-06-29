from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean

from app.core.models import QueryOptions, QueryRequest
from app.evaluation.ragas_evaluator import RagasEvaluator
from app.evaluation.report_generator import ReportGenerator
from app.evaluation.retrieval_metrics import calculate_retrieval_metrics


class ExperimentRunner:
    def __init__(self, engine) -> None:
        self.engine = engine

    def run(self, name: str, cases: list, options: QueryOptions, write_report: bool = True) -> dict:
        started_at = datetime.now()
        run_id = f"ragas_run_{started_at.strftime('%Y%m%d_%H%M%S')}"
        totals: dict[str, list[float]] = defaultdict(list)
        category_totals: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        failed_cases: list[dict] = []
        sample_results: list[dict] = []
        traces = []
        evaluator = RagasEvaluator()
        for case in cases:
            trace = self.engine.query(QueryRequest(question=case.query, options=options))
            traces.append(trace.trace_id)
            retrieved_doc_ids = list(dict.fromkeys(hit.doc_id for hit in trace.reranked_docs))
            retrieved_chunk_ids = list(dict.fromkeys(hit.chunk_id for hit in trace.reranked_docs))
            reference_ids = list(case.gold_doc_ids)
            retrieved_for_reference = retrieved_chunk_ids if any(item.startswith("chunk_") for item in reference_ids) else retrieved_doc_ids
            contexts = trace.compressed_context or [hit.content for hit in trace.reranked_docs]
            retrieval_metrics = calculate_retrieval_metrics(retrieved_for_reference, reference_ids, case.relevance) if reference_ids else {}
            sample_eval = evaluator.evaluate_sample(
                case.query,
                trace.answer,
                contexts,
                case.ground_truth,
                retrieved_chunk_ids=retrieved_for_reference,
                reference_context_ids=reference_ids,
            )
            ragas_metrics = sample_eval["metrics"]
            for key, value in {**retrieval_metrics, **ragas_metrics}.items():
                if value is not None:
                    totals[key].append(float(value))
                    category_totals[case.category][key].append(float(value))
            for key, value in trace.latency_ms.items():
                totals[f"latency_{key}_ms"].append(value)
            totals["input_tokens"].append(trace.token_usage.get("input_tokens", 0))
            totals["output_tokens"].append(trace.token_usage.get("output_tokens", 0))
            totals["cost_total"].append(trace.cost.get("total", 0.0))
            sample_result = {
                "run_id": run_id,
                "eval_id": case.query_id,
                "question": case.query,
                "ground_truth": case.ground_truth,
                "retrieved_contexts": contexts,
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "reference_context_ids": reference_ids,
                "generated_answer": trace.answer,
                "answer": trace.answer,
                "metrics": ragas_metrics,
                "faithfulness": ragas_metrics.get("faithfulness"),
                "answer_relevancy": ragas_metrics.get("answer_relevancy"),
                "context_precision": ragas_metrics.get("context_precision"),
                "context_recall": ragas_metrics.get("context_recall"),
                "failure_type": sample_eval.get("failure_type"),
                "root_cause": sample_eval.get("root_cause"),
                "optimization_suggestion": sample_eval.get("optimization_suggestion"),
                "source_chunks": retrieved_chunk_ids,
                "trace": {
                    "trace_id": trace.trace_id,
                    "retrieval_mode": trace.retrieval_mode,
                    "latency_ms": trace.latency_ms,
                    "tokens": trace.token_usage,
                },
            }
            sample_results.append(sample_result)
            if sample_eval.get("failure_type") or (reference_ids and not retrieval_metrics.get("hit_at_5", 0.0)):
                failed_cases.append(
                    {
                        "query_id": case.query_id,
                        "question": case.query,
                        "domain": case.category,
                        "ground_truth": case.ground_truth,
                        "actual_answer": trace.answer,
                        "expected_chunk_ids": reference_ids,
                        "retrieved_chunk_ids": retrieved_chunk_ids,
                        "faithfulness": ragas_metrics.get("faithfulness"),
                        "answer_relevancy": ragas_metrics.get("answer_relevancy"),
                        "context_precision": ragas_metrics.get("context_precision"),
                        "context_recall": ragas_metrics.get("context_recall"),
                        "failure_type": sample_eval.get("failure_type") or "retrieval_miss",
                        "root_cause": sample_eval.get("root_cause") or "gold document not found in Top5",
                        "optimization_suggestion": sample_eval.get("optimization_suggestion") or "检查检索配置和评测集 reference_context_ids。",
                    }
                )
        finished_at = datetime.now()
        metrics = {key: round(mean(values), 4) for key, values in totals.items() if values}
        report = {
            "run_id": run_id,
            "experiment": name,
            "eval_dataset": name,
            "embedding_model": options.embedding,
            "vector_db": options.vectorstore,
            "retriever_config": options.retrieval_mode,
            "retrieval_config": options.retrieval_mode,
            "reranker_model": options.reranker_model if options.rerank else "disabled",
            "top_k": options.top_k,
            "score_threshold": None,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": finished_at.isoformat(timespec="seconds"),
            "status": "completed",
            "case_count": len(cases),
            "sample_count": len(cases),
            "options": options.model_dump(),
            "metrics": metrics,
            "avg_faithfulness": metrics.get("faithfulness"),
            "avg_answer_relevancy": metrics.get("answer_relevancy"),
            "avg_context_precision": metrics.get("context_precision"),
            "avg_context_recall": metrics.get("context_recall"),
            "category_metrics": {
                category: {key: round(mean(values), 4) for key, values in metrics.items() if values}
                for category, metrics in category_totals.items()
            },
            "sample_results": sample_results,
            "failed_cases": failed_cases,
            "trace_ids": traces,
        }
        report["report_files"] = ReportGenerator().write(name, report) if write_report else {}
        return report
