import pytest

from sensitive_field_review_agent.policy_loader import load_policy


def test_sample_policy_loads_successfully():
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    assert policy.policy_name == "default_sensitive_field_policy"
    assert "high" in policy.review_levels
    assert "direct_identifier" in policy.categories
    assert "customer_id" in policy.field_overrides


def test_missing_policy_file_raises():
    with pytest.raises(FileNotFoundError):
        load_policy("missing_policy.yaml")


def test_unsupported_extension_raises(tmp_path):
    path = tmp_path / "policy.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported policy extension"):
        load_policy(path)


def test_missing_policy_name_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text("review_levels: {high: {}}\ncategories: {x: {default_review_level: high}}", encoding="utf-8")
    with pytest.raises(ValueError, match="policy_name is required"):
        load_policy(path)


def test_missing_review_levels_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text("policy_name: x\ncategories: {x: {default_review_level: high}}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_policy(path)


def test_missing_categories_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text("policy_name: x\nreview_levels: {high: {}}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_policy(path)


def test_unknown_category_default_review_level_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(
        "policy_name: x\nreview_levels: {high: {}}\ncategories: {x: {default_review_level: medium}}",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown level"):
        load_policy(path)


def test_unknown_override_review_level_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(
        """
policy_name: x
review_levels: {high: {}}
categories: {x: {default_review_level: high}}
field_overrides:
  id:
    category: x
    review_level: medium
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown level"):
        load_policy(path)


def test_malformed_yaml_raises(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text("policy_name: [", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed YAML"):
        load_policy(path)
