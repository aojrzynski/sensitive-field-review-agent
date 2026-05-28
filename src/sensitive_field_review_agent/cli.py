"""CLI scaffold for Sensitive Field Review Agent.

This module provides a minimal command-line interface for PR #1. It creates
placeholder trace output so workflow shape and tooling can be validated before
implementing the real review engine in later PRs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sensitive_field_review_agent import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for scaffold execution."""
    parser = argparse.ArgumentParser(description="Sensitive Field Review Agent (scaffold)")
    parser.add_argument("--input", required=True, help="Path to input dataset file")
    parser.add_argument("--policy", required=True, help="Path to policy configuration file")
    parser.add_argument(
        "--output-dir",
        default="outputs/sensitive_field_review",
        help="Directory for output artifacts",
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
    """Run scaffold CLI and emit placeholder trace metadata.

    The scaffold records request metadata and emits a `scaffold_only` status.
    No sensitive field detection or classification is performed in PR #1.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    trace = {
        "input_path": str(args.input),
        "policy_path": str(args.policy),
        "output_directory": str(output_dir),
        "llm_review_requested": bool(args.llm_review),
        "model": args.model,
        "status": "scaffold_only",
    }

    trace_path = output_dir / "sensitive_field_trace.json"
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    print("Scaffold installed. Review engine implementation will arrive in later PRs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
