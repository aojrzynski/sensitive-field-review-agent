import pandas as pd

from sensitive_field_review_agent.profiling import profile_dataset


def test_profile_dataset_basic_metrics_and_types():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice Example", "Bob", None],
            "age": [30, 40, 40],
            "active": [True, False, True],
            "joined": ["2024-01-01", "2024-02-01", None],
            "empty_col": [None, None, None],
        }
    )

    profile = profile_dataset(dataframe, max_examples_per_field=2)
    by_name = {f.column_name: f for f in profile.field_profiles}

    name = by_name["name"]
    assert name.non_null_count == 2
    assert name.null_count == 1
    assert name.distinct_count == 2
    assert name.null_ratio == 1 / 3
    assert name.inferred_physical_type == "string"
    assert len(name.safe_example_shapes) == 2

    age = by_name["age"]
    assert age.inferred_physical_type == "number"
    assert age.safe_example_shapes == []

    active = by_name["active"]
    assert active.inferred_physical_type == "boolean"

    joined = by_name["joined"]
    assert joined.inferred_physical_type == "datetime"

    empty_col = by_name["empty_col"]
    assert empty_col.non_null_count == 0
    assert empty_col.distinct_count == 0
    assert empty_col.safe_example_shapes == []


def test_profile_safe_examples_are_limited_and_redacted():
    dataframe = pd.DataFrame(
        {
            "contact": [
                "Alice Example",
                "alice@example.com",
                "07111 000001",
                "SW1A 1AA",
                "10 Demo Street",
            ]
        }
    )

    profile = profile_dataset(dataframe, max_examples_per_field=3)
    field = profile.field_profiles[0]

    assert len(field.safe_example_shapes) == 3
    rendered = str(field.safe_example_shapes)
    for raw in [
        "Alice Example",
        "alice@example.com",
        "07111 000001",
        "SW1A 1AA",
        "10 Demo Street",
    ]:
        assert raw not in rendered


def test_profile_sample_business_types_do_not_infer_phone_as_datetime():
    dataframe = pd.DataFrame(
        {
            "phone": ["07111 000001", "07111 000002", "07111 000003"],
            "date_of_birth": ["1980-01-01", "1991-02-03", "1975-12-31"],
            "account_balance": [125.50, 0.0, 9999.99],
            "marketing_consent": [True, False, True],
        }
    )

    profile = profile_dataset(dataframe, max_examples_per_field=3)
    by_name = {f.column_name: f for f in profile.field_profiles}

    assert by_name["phone"].inferred_physical_type == "string"
    assert by_name["date_of_birth"].inferred_physical_type == "datetime"
    assert by_name["account_balance"].inferred_physical_type == "number"
    assert by_name["marketing_consent"].inferred_physical_type == "boolean"
