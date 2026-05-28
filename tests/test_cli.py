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


def test_scaffold_writes_trace(tmp_path, capsys):
    input_file = tmp_path / "input.csv"
    policy_file = tmp_path / "policy.yaml"
    output_dir = tmp_path / "outputs"

    input_file.write_text("id,name\n1,Alice\n", encoding="utf-8")
    policy_file.write_text("rules: []\n", encoding="utf-8")

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
    assert "Scaffold installed" in captured.out

    trace_file = output_dir / "sensitive_field_trace.json"
    assert trace_file.exists()

    trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
    assert trace_data["status"] == "scaffold_only"
    assert trace_data["llm_review_requested"] is True
    assert trace_data["input_path"] == str(input_file)
    assert trace_data["policy_path"] == str(policy_file)
