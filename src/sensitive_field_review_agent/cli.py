"""CLI for Sensitive Field Review Agent intake and policy loading foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sensitive_field_review_agent import __version__
from sensitive_field_review_agent.intake import load_dataset
from sensitive_field_review_agent.policy_loader import load_policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sensitive Field Review Agent")
    parser.add_argument("--input", required=True, help="Path to input dataset file")
    parser.add_argument("--policy", required=True, help="Path to policy configuration file")
    parser.add_argument(
        "--output-dir",
        default="outputs/sensitive_field_review",
        help="Directory for output artifacts",
    )
    parser.add_argument(
        "--sheet",
        default=None,
        help="Optional sheet name for Excel input (.xlsx/.xlsm)",
    )
    parser.add_argument(
        "--llm-review",
        action="store_true",
        help="Request optional LLM review mode (non-authoritative)",
    )
    parser.add_argument("--model", default=None, help="Optional model name for future LLM review")
    parser.add_argument(
        "--version",
        action="version",
        version=f"sensitive-field-review-agent {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    _, dataset_metadata = load_dataset(args.input, sheet=args.sheet)
    policy = load_policy(args.policy)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

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
        "status": "intake_and_policy_loaded",
    }

    trace_path = output_dir / "sensitive_field_trace.json"
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    print("Loaded dataset and policy successfully. Detection engine will be implemented in later PRs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
