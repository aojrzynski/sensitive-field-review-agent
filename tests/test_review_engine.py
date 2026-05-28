import json

import pandas as pd

from sensitive_field_review_agent.policy_loader import load_policy
from sensitive_field_review_agent.profiling import profile_dataset
from sensitive_field_review_agent.review_engine import dataset_review_to_dict, generate_dataset_review
from sensitive_field_review_agent.signals import generate_dataset_signals

RAW_VALUES = [
    "Alice Example",
    "alice@example.com",
    "07111 000001",
    "SW1A 1AA",
    "10 Demo Street",
    "sk_live_1234567890abcdef",
    "12345678",
]


def _build_review_dict() -> dict:
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    df = pd.DataFrame(
        {
            "customer_id": ["C001", "C002", "C003"],
            "email": ["alice@example.com", "bob@example.com", "eve@example.com"],
            "phone": ["07111 000001", "07111 000002", "07111 000003"],
            "postcode": ["SW1A 1AA", "EC1A 1BB", "W1A 0AX"],
            "address": ["10 Demo Street", "11 Demo Street", "12 Demo Street"],
            "misc": ["ok", "done", "clear"],
        }
    )
    review = generate_dataset_review(policy, profile_dataset(df, 3), generate_dataset_signals(df, policy))
    return dataset_review_to_dict(review)


def test_review_engine_core_behaviors():
    review = _build_review_dict()
    by_col = {f["column_name"]: f for f in review["fields"]}

    assert by_col["customer_id"]["confidence"] == "policy_override"
    assert by_col["customer_id"]["suggested_policy_category"] == "operational_identifier"

    assert by_col["email"]["suggested_policy_category"] == "contact_information"
    assert by_col["phone"]["suggested_policy_category"] == "contact_information"
    assert by_col["postcode"]["suggested_policy_category"] == "location"
    assert by_col["address"]["suggested_policy_category"] == "location"

    assert by_col["misc"]["review_required"] is False
    assert by_col["misc"]["suggested_review_level"] in {"none", "low"}
    assert by_col["misc"]["confidence"] == "none"

    assert by_col["email"]["reviewer_questions"]


def test_review_artifacts_wording_and_raw_value_safety(tmp_path):
    from sensitive_field_review_agent.cli import main

    input_file = tmp_path / "input.csv"
    input_file.write_text(
        "name,email,phone,postcode,address,token,account_number\n"
        "Alice Example,alice@example.com,07111 000001,SW1A 1AA,10 Demo Street,sk_live_1234567890abcdef,12345678\n",
        encoding="utf-8",
    )

    out = tmp_path / "out"
    rc = main([
        "--input",
        str(input_file),
        "--policy",
        "config/examples/sensitive_field_policy.yaml",
        "--output-dir",
        str(out),
    ])
    assert rc == 0

    rendered_results = (out / "sensitive_field_results.json").read_text(encoding="utf-8")
    rendered_csv = (out / "sensitive_field_findings.csv").read_text(encoding="utf-8")
    rendered_report = (out / "sensitive_field_review_report.md").read_text(encoding="utf-8")

    for raw in RAW_VALUES:
        assert raw not in rendered_results
        assert raw not in rendered_csv
        assert raw not in rendered_report

    lower_report = rendered_report.lower()
    banned = ["gdpr", "compliant", "non-compliant", "pii", "sensitive data detected", "detected pii"]
    for word in banned:
        assert word not in lower_report

    assert "may require review" in lower_report
    assert "human reviewer makes the final decision" in lower_report

    parsed = json.loads(rendered_results)
    assert parsed["fields"]
