from __future__ import annotations

import csv
import json
from pathlib import Path


class ReportGenerator:
    def __init__(self, output_dir: str | Path = "reports/eval_reports") -> None:
        self.output_dir = Path(output_dir)

    def write(self, name: str, report: dict) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / f"{name}.json"
        csv_path = self.output_dir / f"{name}.csv"
        md_path = self.output_dir / f"{name}.md"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        metrics = report.get("metrics", {})
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["metric", "value"])
            writer.writerows(metrics.items())
        lines = [f"# {name}", "", "## Metrics", "", "| Metric | Value |", "|---|---:|"]
        lines.extend(f"| {key} | {value} |" for key, value in metrics.items())
        lines.extend(["", "## Failed Cases", ""])
        for item in report.get("failed_cases", []):
            lines.append(f"- `{item.get('query_id')}` {item.get('query')} - {item.get('reason')}")
        md_path.write_text("\n".join(lines), encoding="utf-8")
        return {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}

    def write_comparison(self, reports: list[dict], name: str = "experiment_comparison") -> dict:
        rows = []
        for report in reports:
            metrics = report.get("metrics", {})
            quality_score = (
                metrics.get("recall_at_5", 0.0) * 0.30
                + metrics.get("mrr", 0.0) * 0.20
                + metrics.get("faithfulness", 0.0) * 0.20
                + metrics.get("context_precision", 0.0) * 0.15
                + metrics.get("answer_correctness", 0.0) * 0.15
            )
            rows.append(
                {
                    "experiment": report.get("experiment", "unknown"),
                    "quality_score": round(quality_score, 4),
                    "recall_at_5": metrics.get("recall_at_5"),
                    "mrr": metrics.get("mrr"),
                    "ndcg_at_5": metrics.get("ndcg_at_5"),
                    "faithfulness": metrics.get("faithfulness"),
                    "context_precision": metrics.get("context_precision"),
                    "answer_correctness": metrics.get("answer_correctness"),
                    "latency_total_ms": metrics.get("latency_total_ms"),
                }
            )
        rows.sort(key=lambda item: item["quality_score"], reverse=True)
        comparison = {"recommended_experiment": rows[0]["experiment"] if rows else None, "experiments": rows}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / f"{name}.json"
        csv_path = self.output_dir / f"{name}.csv"
        md_path = self.output_dir / f"{name}.md"
        json_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
        fieldnames = list(rows[0]) if rows else ["experiment", "quality_score"]
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        lines = [f"# {name}", "", f"Recommended: `{comparison['recommended_experiment']}`", ""]
        if rows:
            lines.extend(["| " + " | ".join(fieldnames) + " |", "|" + "---|" * len(fieldnames)])
            lines.extend("| " + " | ".join(str(row.get(key, "")) for key in fieldnames) + " |" for row in rows)
        md_path.write_text("\n".join(lines), encoding="utf-8")
        comparison["report_files"] = {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}
        return comparison
