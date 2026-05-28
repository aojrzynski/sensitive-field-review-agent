import json

import pandas as pd

from sensitive_field_review_agent.policy_loader import load_policy
from sensitive_field_review_agent.signals import dataset_signals_to_dict, generate_dataset_signals


RAW_VALUES = [
    "Alice Example",
    "alice@example.com",
    "07111 000001",
    "SW1A 1AA",
    "10 Demo Street",
    "sk_live_1234567890abcdef",
    "12345678",
]


def test_generate_signals_pattern_and_keyword_matches():
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    df = pd.DataFrame(
        {
            "email": ["alice@example.com", "bob@example.com", "c@example.com"],
            "phone": ["07111 000001", "07111 000002", "07111 000003"],
            "postcode": ["SW1A 1AA", "EC1A 1BB", "W1A 0AX"],
            "created_at": ["1985-05-01", "1986-06-02", "1987-07-03"],
            "account_number": ["12345678", "23456789", "34567890"],
            "api_token": ["sk_live_1234567890abcdef", "token_abc12345678", "secret_value_1234"],
            "notes": ["Alice Example", "10 Demo Street", "follow-up"],
        }
    )

    signals = dataset_signals_to_dict(generate_dataset_signals(df, policy))
    by_field = {f["column_name"]: f["signals"] for f in signals["fields"]}

    assert any(s["signal_name"] == "email_like" for s in by_field["email"])
    assert any(s["signal_name"] == "phone_like" for s in by_field["phone"])
    assert any(s["signal_name"] == "uk_postcode_like" for s in by_field["postcode"])
    date_policy = load_policy("config/examples/sensitive_field_policy.yaml")
    date_policy.categories["contact_information"].pattern_families.append("date_like")
    date_signals = dataset_signals_to_dict(generate_dataset_signals(df, date_policy))
    date_by_field = {f["column_name"]: f["signals"] for f in date_signals["fields"]}
    assert any(s["signal_name"] == "date_like" for s in date_by_field["created_at"])
    assert any(s["signal_name"] == "account_number_like" for s in by_field["account_number"])
    assert any(s["signal_name"] == "secret_or_token_like" for s in by_field["api_token"])
    assert any(s["signal_type"] == "column_name_keyword" for s in by_field["email"])


def test_generate_signals_thresholds_and_empty_fields():
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    df = pd.DataFrame({"misc": ["alice@example.com", "not-an-email", "none"]})

    signals = dataset_signals_to_dict(generate_dataset_signals(df, policy))
    assert signals["row_count"] == 3
    assert signals["column_count"] == 1
    assert signals["fields"][0]["column_name"] == "misc"
    assert signals["fields"][0]["signals"] == []


def test_signal_artifact_contains_no_raw_values():
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    df = pd.DataFrame(
        {
            "email": ["alice@example.com", "bob@example.com"],
            "phone": ["07111 000001", "07111 000002"],
            "postcode": ["SW1A 1AA", "EC1A 1BB"],
            "address": ["10 Demo Street", "11 Demo Street"],
            "token": ["sk_live_1234567890abcdef", "token_xyz987654321"],
            "name": ["Alice Example", "Bob Example"],
            "account_number": ["12345678", "23456789"],
        }
    )

    rendered = json.dumps(dataset_signals_to_dict(generate_dataset_signals(df, policy)))
    for raw in RAW_VALUES:
        assert raw not in rendered
