"""CLI for Sensitive Field Review Agent deterministic intake, profiling, signals, and review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from sensitive_field_review_agent import __version__
from sensitive_field_review_agent.intake import load_dataset
from sensitive_field_review_agent.llm_review import build_safe_payload, run_llm_review, write_llm_artifacts
from sensitive_field_review_agent.policy_loader import load_policy
from sensitive_field_review_agent.profiling import dataset_profile_to_dict, profile_dataset
from sensitive_field_review_agent.review_engine import dataset_review_to_dict, generate_dataset_review
from sensitive_field_review_agent.signals import dataset_signals_to_dict, generate_dataset_signals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sensitive Field Review Agent")
    parser.add_argument("--input", required=True, help="Path to input dataset file")
    parser.add_argument("--policy", required=True, help="Path to policy configuration file")
    parser.add_argument("--output-dir", default="outputs/sensitive_field_review", help="Directory for output artifacts")
    parser.add_argument("--sheet", default=None, help="Optional sheet name for Excel input (.xlsx/.xlsm)")
    parser.add_argument("--llm-review", action="store_true", help="Request optional LLM review mode (non-authoritative)")
    parser.add_argument("--model", default=None, help="Optional model name for future LLM review")
    parser.add_argument("--version", action="version", version=f"sensitive-field-review-agent {__version__}")
    return parser


def _write_findings_csv(path: Path, review_dict: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "column_name",
                "review_required",
                "suggested_policy_category",
                "suggested_review_level",
                "confidence",
                "evidence_summary",
            ],
        )
        writer.writeheader()
        for field in review_dict["fields"]:
            writer.writerow({k: field[k] for k in writer.fieldnames})


def _build_review_report(review_dict: dict, trace: dict) -> str:
    fields = review_dict["fields"]
    requiring_review = [f for f in fields if f["review_required"]]
    no_signal = [f for f in fields if f["confidence"] == "none"]

    lines = [
        "# Sensitive Field Review Report",
        "",
        "This deterministic report supports triage. It is not a legal or compliance verdict.",
        "Human reviewer makes the final decision.",
        "",
        "## Authority boundary",
        f"- {review_dict.get('authority_note') or 'This workflow supports field-level triage only.'}",
        "",
        "## Inputs",
        f"- Input file: `{Path(trace['input_path']).name}`",
        f"- Policy file: `{Path(trace['policy_path']).name}`",
        "- Output artifacts: generated in the selected output directory",
        f"- Row count: {review_dict['row_count']}",
        f"- Column count: {review_dict['column_count']}",
        "",
        "## Summary",
        f"- Fields reviewed: {len(fields)}",
        f"- Fields that may require review: {len(requiring_review)}",
        f"- Fields with no configured deterministic signals: {len(no_signal)}",
        "",
        "## Fields that may require review",
    ]
    for field in requiring_review:
        lines.append(
            f"- `{field['column_name']}` → suggested policy category `{field['suggested_policy_category']}`, "
            f"suggested review level `{field['suggested_review_level']}` ({field['confidence']} confidence)."
        )
        lines.append(f"  - Evidence: {field['evidence_summary']}")

    lines.extend(["", "## Fields with no configured deterministic signals"])
    for field in no_signal:
        lines.append(f"- `{field['column_name']}`")

    lines.extend([
        "",
        "## Decision note",
        "These outputs are deterministic review suggestions for triage. Human reviewer decides final handling.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dataframe, dataset_metadata = load_dataset(args.input, sheet=args.sheet)
    policy = load_policy(args.policy)
    dataset_profile = profile_dataset(dataframe, max_examples_per_field=policy.redaction.max_redacted_examples_per_field)
    dataset_signals = generate_dataset_signals(dataframe, policy)
    dataset_review = generate_dataset_review(policy=policy, profile=dataset_profile, signals=dataset_signals)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_path = output_dir / "sensitive_field_profile.json"
    signals_path = output_dir / "sensitive_field_signals.json"
    results_path = output_dir / "sensitive_field_results.json"
    findings_csv_path = output_dir / "sensitive_field_findings.csv"
    review_report_path = output_dir / "sensitive_field_review_report.md"

    profile_path.write_text(json.dumps(dataset_profile_to_dict(dataset_profile), indent=2), encoding="utf-8")
    signals_path.write_text(json.dumps(dataset_signals_to_dict(dataset_signals), indent=2), encoding="utf-8")
    review_dict = dataset_review_to_dict(dataset_review)
    results_path.write_text(json.dumps(review_dict, indent=2), encoding="utf-8")
    _write_findings_csv(findings_csv_path, review_dict)

    trace = {
        "input_path": str(args.input),
        "policy_path": str(args.policy),
        "output_directory": str(output_dir),
        "sheet": args.sheet,
        "llm_review_requested": bool(args.llm_review),
        "model": args.model,
        "dataset_metadata": {
            "file_name": dataset_metadata.file_name,
            "file_extension": dataset_metadata.file_extension,
            "sheet_name": dataset_metadata.sheet_name,
            "row_count": dataset_metadata.row_count,
            "column_count": dataset_metadata.column_count,
            "columns": dataset_metadata.columns,
        },
        "policy_metadata": {
            "policy_name": policy.policy_name,
            "policy_version": policy.policy_version,
            "review_level_names": sorted(policy.review_levels.keys()),
            "category_names": sorted(policy.categories.keys()),
            "field_override_names": sorted(policy.field_overrides.keys()),
        },
        "profile_artifacts": {"field_profile_path": str(profile_path)},
        "signal_artifacts": {"field_signals_path": str(signals_path)},
        "review_artifacts": {
            "results_path": str(results_path),
            "findings_csv_path": str(findings_csv_path),
            "review_report_path": str(review_report_path),
        },
        "llm_review_status": "not_requested",
        "status": "review_artifacts_generated",
    }

    review_report_path.write_text(_build_review_report(review_dict, trace), encoding="utf-8")

    if args.llm_review:
        safe_payload = build_safe_payload(dataset_review, dataset_profile, dataset_signals)
        llm_result = run_llm_review(safe_payload, args.model)
        trace["llm_artifacts"] = write_llm_artifacts(output_dir, safe_payload, llm_result)
        trace["llm_review_status"] = llm_result.get("llm_review_status", "failed_fallback")

    (output_dir / "sensitive_field_trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")

    print("Loaded dataset and policy successfully. Deterministic safe profile, signals, and review artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
