import json

import pytest

from sensitive_field_review_agent.cli import main


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


def test_cli_writes_trace(tmp_path, capsys):
    input_file = tmp_path / "input.csv"
    policy_file = tmp_path / "policy.yaml"
    output_dir = tmp_path / "outputs"

    input_file.write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")
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
            "--llm-review",
        ]
    )

    assert rc == 0
    captured = capsys.readouterr()
    assert "Loaded dataset and policy successfully" in captured.out

    trace_file = output_dir / "sensitive_field_trace.json"
    assert trace_file.exists()

    trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
    assert trace_data["status"] == "intake_and_policy_loaded"
    assert trace_data["llm_review_requested"] is True
    assert trace_data["dataset_metadata"]["row_count"] == 2
    assert trace_data["dataset_metadata"]["column_count"] == 2
    assert trace_data["policy_metadata"]["policy_name"] == "test_policy"
    assert trace_data["policy_metadata"]["category_names"] == ["contact"]


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
