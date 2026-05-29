"""Load and validate human-authored YAML review policy files.

The policy is the source of review levels, categories, field overrides,
thresholds, and authority wording. This loader validates the expected YAML
structure early and raises clear ValueError messages so policy issues fail fast
before profiling or review artifacts are written.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from sensitive_field_review_agent.models import (
    CategoryPolicy,
    FieldOverride,
    RedactionConfig,
    ReviewLevelPolicy,
    SensitiveFieldPolicy,
    ThresholdsConfig,
)


def _expect_dict(value: object, field_name: str) -> dict:
    """Return a YAML object as a dict, or raise a field-specific error."""

    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _parse_list(value: object, field_name: str) -> list[str]:
    """Parse an optional YAML list field while rejecting scalar shortcuts."""

    if value is None:
        return []
    # Policy list fields must be YAML lists so authors do not accidentally turn
    # a comma-separated string into one broad keyword or question.
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return [str(item) for item in value]


def load_policy(path: str | Path) -> SensitiveFieldPolicy:
    """Load a YAML policy and validate references used by the review pipeline.

    The loader accepts ``.yaml`` and ``.yml`` files. It checks required top-level
    sections, confirms list-valued fields are lists, and verifies that category
    defaults and field overrides reference known review levels and categories.
    It raises FileNotFoundError or ValueError with CLI-friendly messages for
    expected user and policy-authoring errors.
    """

    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    if policy_path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError(f"Unsupported policy extension: {policy_path.suffix.lower()}")

    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Malformed YAML policy file: {policy_path}") from exc

    raw_policy = _expect_dict(raw, "Policy")

    policy_name = raw_policy.get("policy_name")
    if not policy_name:
        raise ValueError("policy_name is required")

    raw_review_levels = _expect_dict(raw_policy.get("review_levels"), "review_levels")
    if not raw_review_levels:
        raise ValueError("At least one review_levels entry is required")

    raw_categories = _expect_dict(raw_policy.get("categories"), "categories")
    if not raw_categories:
        raise ValueError("At least one categories entry is required")

    review_levels: dict[str, ReviewLevelPolicy] = {}
    for name, cfg in raw_review_levels.items():
        cfg_dict = _expect_dict(cfg or {}, f"review_levels.{name}")
        review_levels[name] = ReviewLevelPolicy(name=name, description=cfg_dict.get("description"))

    categories: dict[str, CategoryPolicy] = {}
    for name, cfg in raw_categories.items():
        cfg_dict = _expect_dict(cfg or {}, f"categories.{name}")
        default_level = cfg_dict.get("default_review_level", "medium")
        if default_level not in review_levels:
            raise ValueError(
                f"categories.{name}.default_review_level references unknown level: {default_level}"
            )
        categories[name] = CategoryPolicy(
            name=name,
            description=cfg_dict.get("description"),
            default_review_level=default_level,
            name_keywords=_parse_list(cfg_dict.get("name_keywords"), f"categories.{name}.name_keywords"),
            pattern_families=_parse_list(cfg_dict.get("pattern_families"), f"categories.{name}.pattern_families"),
            reviewer_questions=_parse_list(cfg_dict.get("reviewer_questions"), f"categories.{name}.reviewer_questions"),
        )

    raw_overrides = _expect_dict(raw_policy.get("field_overrides", {}), "field_overrides")
    field_overrides: dict[str, FieldOverride] = {}
    for field_name, cfg in raw_overrides.items():
        cfg_dict = _expect_dict(cfg or {}, f"field_overrides.{field_name}")
        review_level = cfg_dict.get("review_level")
        if review_level not in review_levels:
            raise ValueError(
                f"field_overrides.{field_name}.review_level references unknown level: {review_level}"
            )
        category = cfg_dict.get("category")
        if category not in categories:
            raise ValueError(
                f"field_overrides.{field_name}.category references unknown category: {category}"
            )
        field_overrides[field_name] = FieldOverride(
            field_name=field_name,
            category=str(category),
            review_level=review_level,
            reason=cfg_dict.get("reason"),
        )

    authority_boundary = _expect_dict(raw_policy.get("authority_boundary", {}), "authority_boundary")
    raw_redaction = _expect_dict(raw_policy.get("redaction", {}), "redaction")
    raw_thresholds = _expect_dict(raw_policy.get("thresholds", {}), "thresholds")

    return SensitiveFieldPolicy(
        policy_name=str(policy_name),
        policy_version=raw_policy.get("policy_version"),
        authority_note=authority_boundary.get("note"),
        review_levels=review_levels,
        categories=categories,
        field_overrides=field_overrides,
        redaction=RedactionConfig(
            max_redacted_examples_per_field=int(
                raw_redaction.get("max_redacted_examples_per_field", 3)
            ),
            never_include_raw_values=bool(raw_redaction.get("never_include_raw_values", True)),
        ),
        thresholds=ThresholdsConfig(
            pattern_match_min_count=int(raw_thresholds.get("pattern_match_min_count", 2)),
            pattern_match_min_ratio=float(raw_thresholds.get("pattern_match_min_ratio", 0.6)),
            free_text_avg_length=int(raw_thresholds.get("free_text_avg_length", 40)),
        ),
    )
