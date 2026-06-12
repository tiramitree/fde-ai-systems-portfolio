from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "secure-enterprise-knowledge-copilot"
SRC = PROJECT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copilot.evals import run_evals
from copilot.repositories import connect_repository
from copilot.storage import DATA_DIR, init_db


def check(condition: bool, name: str, detail: str) -> tuple[bool, str]:
    status = "PASS" if condition else "FAIL"
    return condition, f"[{status}] {name}: {detail}"


def main() -> int:
    eval_state_path = DATA_DIR / "eval_runtime_state.json"
    init_db(reset=True, state_path=eval_state_path)
    with connect_repository(eval_state_path) as repo:
        result = run_evals(repo, persist=False)

    metrics = result["metrics"]
    checks = [
        check(
            metrics["pass_rate"] == 1.0,
            "P1 eval behavior pass rate",
            f"pass_rate={metrics['pass_rate']}",
        ),
        check(
            metrics["behavior_accuracy"] == 1.0,
            "P1 answer/abstain behavior accuracy",
            f"behavior_accuracy={metrics['behavior_accuracy']}",
        ),
        check(
            metrics["unsafe_leak_failures"] == 0 and metrics["forbidden_retrieval_leak_failures"] == 0,
            "P1 retrieval and citation leak failures stay zero",
            (
                f"unsafe_leak_failures={metrics['unsafe_leak_failures']}; "
                f"forbidden_retrieval_leak_failures={metrics['forbidden_retrieval_leak_failures']}"
            ),
        ),
        check(
            metrics["required_retrieval_recall_at_k"] == 1.0,
            "P1 required retrieval recall@k",
            (
                f"required={metrics['expected_retrieval_doc_count']}; "
                f"retrieved={metrics['retrieved_required_doc_count']}; "
                f"recall={metrics['required_retrieval_recall_at_k']}"
            ),
        ),
        check(
            metrics["mean_reciprocal_rank"] >= 0.8,
            "P1 retrieval mean reciprocal rank",
            f"mrr={metrics['mean_reciprocal_rank']}",
        ),
        check(
            metrics["mean_ndcg_at_k"] >= 0.8,
            "P1 retrieval nDCG@k ranking quality",
            f"mean_ndcg_at_k={metrics['mean_ndcg_at_k']}",
        ),
        check(
            metrics["mean_average_precision_at_k"] >= 0.8,
            "P1 ranked context precision@k",
            f"mean_average_precision_at_k={metrics['mean_average_precision_at_k']}",
        ),
        check(
            metrics["required_citation_coverage"] == 1.0 and metrics["citation_span_coverage"] == 1.0,
            "P1 required citation and source-span coverage",
            (
                f"required_citation_coverage={metrics['required_citation_coverage']}; "
                f"citation_span_coverage={metrics['citation_span_coverage']}"
            ),
        ),
        check(
            metrics["citation_retrieval_alignment"] == 1.0
            and metrics["citation_retrieval_alignment_failures"] == 0,
            "P1 citations come from retrieved context",
            (
                f"citation_retrieval_alignment={metrics['citation_retrieval_alignment']}; "
                f"failures={metrics['citation_retrieval_alignment_failures']}"
            ),
        ),
        check(
            metrics["security_event_coverage"] == 1.0 and metrics["security_event_failures"] == 0,
            "P1 required security-event coverage",
            (
                f"security_event_cases={metrics['security_event_cases']}; "
                f"security_event_failures={metrics['security_event_failures']}"
            ),
        ),
        check(
            metrics["permission_block_coverage"] == 1.0,
            "P1 permission-block eval coverage",
            (
                f"permission_block_cases={metrics['permission_block_cases']}; "
                f"permission_block_failures={metrics['permission_block_failures']}"
            ),
        ),
        check(
            metrics["stale_source_filter_coverage"] == 1.0,
            "P1 stale-source filter coverage",
            (
                f"stale_source_cases={metrics['stale_source_cases']}; "
                f"stale_source_filter_failures={metrics['stale_source_filter_failures']}"
            ),
        ),
    ]

    failures = [line for passed, line in checks if not passed]
    for _, line in checks:
        print(line)
    print(
        "Retrieval metrics summary: "
        + json.dumps(
            {
                "required_retrieval_recall_at_k": metrics["required_retrieval_recall_at_k"],
                "required_retrieval_precision_at_k": metrics["required_retrieval_precision_at_k"],
                "mean_reciprocal_rank": metrics["mean_reciprocal_rank"],
                "mean_ndcg_at_k": metrics["mean_ndcg_at_k"],
                "mean_average_precision_at_k": metrics["mean_average_precision_at_k"],
                "required_citation_coverage": metrics["required_citation_coverage"],
                "citation_retrieval_alignment": metrics["citation_retrieval_alignment"],
                "security_event_coverage": metrics["security_event_coverage"],
                "permission_block_coverage": metrics["permission_block_coverage"],
                "stale_source_filter_coverage": metrics["stale_source_filter_coverage"],
            },
            sort_keys=True,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
