import json

import pytest

from sensitive_field_review_agent.cli import main


RAW_SENSITIVE_VALUES = [
    "Alice Example",
    "alice@example.com",
    "07111 000001",
    "SW1A 1AA",
    "10 Demo Street",
]


def test_main_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "sensitive-field-review-agent 0.1.0" in captured.out


def test_cli_help(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Sensitive Field Review Agent" in captured.out
    assert "--sheet" in captured.out


def test_cli_writes_trace_and_profile(tmp_path, capsys):
    input_file = tmp_path / "input.csv"
    policy_file = tmp_path / "policy.yaml"
    output_dir = tmp_path / "very_sensitive_output_directory"

    input_file.write_text(
        "name,email,phone,postcode,address\n"
        "Alice Example,alice@example.com,07111 000001,SW1A 1AA,10 Demo Street\n"
        "Bob Example,bob@example.com,07111 000002,EC1A 1BB,20 Demo Street\n",
        encoding="utf-8",
    )
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
categories:
  contact:
    default_review_level: high
redaction:
  max_redacted_examples_per_field: 2
""".strip(),
        encoding="utf-8",
    )

    rc = main(
        [
            "--input",
            str(input_file),
            "--policy",
            str(policy_file),
            "--output-dir",
            str(output_dir),
            "--llm-review",
        ]
    )

    assert rc == 0
    captured = capsys.readouterr()
    assert "Deterministic safe profile, signals, and review artifacts generated" in captured.out

    trace_file = output_dir / "sensitive_field_trace.json"
    profile_file = output_dir / "sensitive_field_profile.json"
    assert trace_file.exists()
    signals_file = output_dir / "sensitive_field_signals.json"
    assert profile_file.exists()
    assert signals_file.exists()

    trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
    assert trace_data["status"] == "review_artifacts_generated"
    assert trace_data["llm_review_requested"] is True
    assert trace_data["llm_review_status"] in {"skipped_missing_api_key", "failed_fallback", "completed"}
    assert trace_data["dataset_metadata"]["row_count"] == 2
    assert trace_data["dataset_metadata"]["column_count"] == 5
    assert trace_data["policy_metadata"]["policy_name"] == "test_policy"
    assert trace_data["policy_metadata"]["category_names"] == ["contact"]
    assert "field_profile_path" in trace_data["profile_artifacts"]
    assert "field_signals_path" in trace_data["signal_artifacts"]
    assert "results_path" in trace_data["review_artifacts"]
    assert "findings_csv_path" in trace_data["review_artifacts"]
    assert "review_report_path" in trace_data["review_artifacts"]

    profile_data = json.loads(profile_file.read_text(encoding="utf-8"))
    profile_field_names = [field["column_name"] for field in profile_data["field_profiles"]]
    assert profile_field_names == ["name", "email", "phone", "postcode", "address"]

    rendered_profile = profile_file.read_text(encoding="utf-8")
    rendered_signals = signals_file.read_text(encoding="utf-8")
    rendered_results = (output_dir / "sensitive_field_results.json").read_text(encoding="utf-8")
    rendered_findings = (output_dir / "sensitive_field_findings.csv").read_text(encoding="utf-8")
    rendered_report = (output_dir / "sensitive_field_review_report.md").read_text(encoding="utf-8")
    for raw in RAW_SENSITIVE_VALUES + ["sk_live_1234567890abcdef", "12345678"]:
        assert raw not in rendered_profile
        assert raw not in rendered_signals
        assert raw not in rendered_results
        assert raw not in rendered_findings
        assert raw not in rendered_report

    signal_data = json.loads(rendered_signals)
    assert [field["column_name"] for field in signal_data["fields"]] == ["name", "email", "phone", "postcode", "address"]


def test_cli_accepts_sheet_argument(tmp_path):
    input_file = tmp_path / "input.xlsx"
    policy_file = tmp_path / "policy.yaml"
    output_dir = tmp_path / "outputs"

    pytest.importorskip("openpyxl")
    import pandas as pd

    pd.DataFrame({"id": [1], "name": ["Alice"]}).to_excel(
        input_file, sheet_name="Customers", index=False
    )
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
categories:
  contact:
    default_review_level: high
""".strip(),
        encoding="utf-8",
    )

    rc = main(
        [
            "--input",
            str(input_file),
            "--policy",
            str(policy_file),
            "--output-dir",
            str(output_dir),
            "--sheet",
            "Customers",
            "--llm-review",
        ]
    )

    assert rc == 0
    trace_data = json.loads((output_dir / "sensitive_field_trace.json").read_text(encoding="utf-8"))
    assert trace_data["sheet"] == "Customers"
    assert trace_data["dataset_metadata"]["sheet_name"] == "Customers"


def test_report_uses_file_names_not_full_paths(tmp_path):
    input_dir = tmp_path / "very_sensitive_literal_directory"
    input_dir.mkdir()
    input_file = input_dir / "input.csv"
    policy_file = tmp_path / "policy.yaml"
    output_dir = tmp_path / "very_sensitive_output_directory"

    input_file.write_text("email\na@example.com\n", encoding="utf-8")
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
  none: {}
categories:
  contact:
    default_review_level: high
    name_keywords: [email]
""".strip(),
        encoding="utf-8",
    )

    rc = main([
        "--input", str(input_file),
        "--policy", str(policy_file),
        "--output-dir", str(output_dir),
    ])
    assert rc == 0

    report = (output_dir / "sensitive_field_review_report.md").read_text(encoding="utf-8")
    trace = (output_dir / "sensitive_field_trace.json").read_text(encoding="utf-8")

    assert "very_sensitive_literal_directory" not in report
    assert "input.csv" in report
    assert "policy.yaml" in report
    assert "very_sensitive_literal_directory" in trace
    assert "very_sensitive_output_directory" not in report
    assert "very_sensitive_output_directory" in trace


def test_cli_without_llm_flag_sets_not_requested(tmp_path):
    input_file = tmp_path / "input.csv"
    input_file.write_text("email\na@example.com\n", encoding="utf-8")
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("""
policy_name: test_policy
review_levels:
  high: {}
  none: {}
categories:
  contact:
    default_review_level: high
    name_keywords: [email]
""".strip(), encoding="utf-8")

    out = tmp_path / "out"
    rc = main(["--input", str(input_file), "--policy", str(policy_file), "--output-dir", str(out)])
    assert rc == 0
    trace = json.loads((out / "sensitive_field_trace.json").read_text(encoding="utf-8"))
    assert trace["llm_review_status"] == "not_requested"
    assert not (out / "llm_field_review.json").exists()


def test_cli_with_llm_flag_missing_key_writes_skipped_artifacts(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    input_file = tmp_path / "input.csv"
    input_file.write_text("email\na@example.com\n", encoding="utf-8")
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("""
policy_name: test_policy
review_levels:
  high: {}
  none: {}
categories:
  contact:
    default_review_level: high
    name_keywords: [email]
""".strip(), encoding="utf-8")

    out = tmp_path / "out"
    rc = main(["--input", str(input_file), "--policy", str(policy_file), "--output-dir", str(out), "--llm-review"])
    assert rc == 0
    trace = json.loads((out / "sensitive_field_trace.json").read_text(encoding="utf-8"))
    assert trace["llm_review_status"] == "skipped_missing_api_key"
    assert (out / "llm_safe_field_summary.json").exists()
    assert (out / "llm_field_review.json").exists()
    assert (out / "llm_field_review.md").exists()


def _assert_clean_cli_error(captured, expected: str) -> None:
    combined = captured.out + captured.err
    assert captured.err.strip() == expected
    assert captured.out == ""
    assert "Traceback" not in combined


def test_cli_missing_input_file_returns_clean_error(tmp_path, capsys):
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
categories:
  contact:
    default_review_level: high
""".strip(),
        encoding="utf-8",
    )

    rc = main([
        "--input", "missing.csv",
        "--policy", str(policy_file),
        "--output-dir", str(tmp_path / "out"),
    ])

    assert rc == 1
    _assert_clean_cli_error(capsys.readouterr(), "Error: Dataset file not found: missing.csv")


def test_cli_unsupported_extension_returns_clean_error(tmp_path, capsys):
    input_file = tmp_path / "input.txt"
    input_file.write_text("email\na@example.com\n", encoding="utf-8")
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
categories:
  contact:
    default_review_level: high
""".strip(),
        encoding="utf-8",
    )

    rc = main([
        "--input", str(input_file),
        "--policy", str(policy_file),
        "--output-dir", str(tmp_path / "out"),
    ])

    assert rc == 1
    _assert_clean_cli_error(
        capsys.readouterr(),
        "Error: Unsupported dataset extension: .txt. Supported formats: .csv, .xlsx, .xlsm",
    )


def test_cli_wrong_excel_sheet_returns_clean_error(tmp_path, capsys):
    pytest.importorskip("openpyxl")
    import pandas as pd

    input_file = tmp_path / "input.xlsx"
    pd.DataFrame({"id": [1], "name": ["Alice"]}).to_excel(
        input_file, sheet_name="Customers", index=False
    )
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
policy_name: test_policy
review_levels:
  high: {}
categories:
  contact:
    default_review_level: high
""".strip(),
        encoding="utf-8",
    )

    rc = main([
        "--input", str(input_file),
        "--policy", str(policy_file),
        "--output-dir", str(tmp_path / "out"),
        "--sheet", "MissingSheet",
    ])

    assert rc == 1
    captured = capsys.readouterr()
    _assert_clean_cli_error(
        captured,
        "Error: Sheet 'MissingSheet' not found in workbook. Available sheets: ['Customers']",
    )
    assert "not found" in captured.err
