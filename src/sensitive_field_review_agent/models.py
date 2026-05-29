"""Shared dataclass models for the sensitive field review workflow.

The models in this module carry deterministic evidence from one stage to the
next: intake metadata, human-authored YAML policy, safe/redacted profiles,
aggregate field signals, and suggested review outputs. They are deliberately
plain dataclasses so JSON artifacts and tests can inspect the same structure
used by the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DatasetMetadata:
    """Intake metadata for the loaded dataset.

    This records where the dataset came from and its basic shape so the trace
    can explain the run without storing row values.
    """

    source_path: Path
    file_name: str
    file_extension: str
    sheet_name: str | None
    row_count: int
    column_count: int
    columns: list[str]


@dataclass(slots=True)
class ReviewLevelPolicy:
    """Human-authored review level from the YAML policy.

    A review level is a label the deterministic review engine can suggest for
    triage. The label comes from policy, not from model inference.
    """

    name: str
    description: str | None = None


@dataclass(slots=True)
class CategoryPolicy:
    """Human-authored policy category used to group review criteria.

    Categories define the configured column-name keywords, pattern families,
    default review level, and reviewer questions that guide deterministic
    evidence collection for a field.
    """

    name: str
    description: str | None = None
    default_review_level: str = "medium"
    name_keywords: list[str] = field(default_factory=list)
    pattern_families: list[str] = field(default_factory=list)
    reviewer_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FieldOverride:
    """Policy instruction that pins one field to a category and level.

    Overrides let a human-authored YAML policy handle known columns before the
    review engine considers generated signals.
    """

    field_name: str
    category: str
    review_level: str
    reason: str | None = None


@dataclass(slots=True)
class RedactionConfig:
    """Policy settings for safe/redacted profile examples.

    These settings control how many example shapes are retained and make the
    intended raw-value boundary explicit for downstream stages.
    """

    max_redacted_examples_per_field: int = 3
    never_include_raw_values: bool = True


@dataclass(slots=True)
class ThresholdsConfig:
    """Policy thresholds for deterministic aggregate signals.

    Thresholds keep pattern-family and free-text heuristics configurable in the
    YAML policy instead of baking review criteria into code.
    """

    pattern_match_min_count: int = 2
    pattern_match_min_ratio: float = 0.6
    free_text_avg_length: int = 40


@dataclass(slots=True)
class SensitiveFieldPolicy:
    """Parsed human-authored YAML policy for one review run.

    The policy combines authority wording, review levels, categories,
    field-specific overrides, redaction settings, and signal thresholds used by
    deterministic profiling and review.
    """

    policy_name: str
    policy_version: str | None
    authority_note: str | None
    review_levels: dict[str, ReviewLevelPolicy]
    categories: dict[str, CategoryPolicy]
    field_overrides: dict[str, FieldOverride]
    redaction: RedactionConfig
    thresholds: ThresholdsConfig


@dataclass(slots=True)
class SafeExampleShape:
    """Redacted shape summary for one example string value.

    This represents length and character classes only. It is suitable for
    review artifacts and LLM payloads because it does not store the raw value.
    """

    length: int
    letters_count: int
    digits_count: int
    whitespace_count: int
    punctuation_or_symbol_count: int
    generalized_shape: str


@dataclass(slots=True)
class FieldProfile:
    """Structured profile for one dataset column.

    This is safe evidence for review and LLM payloads: counts, ratios, inferred
    physical type, optional string length stats, and redacted example shapes.
    """

    column_name: str
    row_count: int
    non_null_count: int
    null_count: int
    null_ratio: float
    distinct_count: int
    distinct_ratio: float
    inferred_physical_type: str
    string_min_length: int | None
    string_max_length: int | None
    string_avg_length: float | None
    safe_example_shapes: list[SafeExampleShape] = field(default_factory=list)


@dataclass(slots=True)
class DatasetProfile:
    """Safe structural profile for the whole dataset.

    The profile is the profiling artifact consumed by the review engine and the
    optional LLM stage; it contains field summaries rather than row data.
    """

    row_count: int
    column_count: int
    field_profiles: list[FieldProfile] = field(default_factory=list)


@dataclass(slots=True)
class FieldSignalEvidence:
    """Aggregate evidence attached to one deterministic signal.

    Pattern signals store counts and ratios; keyword signals store the matched
    configured keyword. Matched raw values are not represented here.
    """

    checked_count: int | None = None
    matched_count: int | None = None
    matched_ratio: float | None = None
    min_count: int | None = None
    min_ratio: float | None = None
    threshold_met: bool | None = None
    matched_keyword: str | None = None


@dataclass(slots=True)
class FieldSignal:
    """One deterministic signal observed for a field.

    Signals connect aggregate evidence to a policy category. They support
    review suggestions, but they are not final decisions.
    """

    column_name: str
    signal_type: str
    signal_name: str
    policy_category: str
    evidence: FieldSignalEvidence
    matched: bool
    notes: str


@dataclass(slots=True)
class FieldSignalSet:
    """Collection of deterministic signals for one column.

    A column is represented even when no signals match so downstream artifacts
    can show complete field coverage.
    """

    column_name: str
    signals: list[FieldSignal] = field(default_factory=list)


@dataclass(slots=True)
class DatasetSignals:
    """Dataset-level signal artifact produced from policy and data.

    This groups per-field deterministic signals while keeping only aggregate or
    policy-derived evidence.
    """

    row_count: int
    column_count: int
    fields: list[FieldSignalSet] = field(default_factory=list)


@dataclass(slots=True)
class FieldReviewEvidence:
    """Human-readable evidence line for a field review result.

    The review engine converts lower-level signals into concise summaries for
    JSON, CSV, Markdown, and optional LLM review.
    """

    signal_type: str
    signal_name: str
    summary: str


@dataclass(slots=True)
class FieldReviewResult:
    """Suggested deterministic review result for one field.

    This combines policy, profile summary, and matched signals into a triage
    suggestion. The human reviewer remains responsible for final decisions.
    """

    column_name: str
    suggested_policy_category: str | None
    suggested_review_level: str
    confidence: str
    review_required: bool
    evidence_summary: str
    supporting_signals: list[FieldReviewEvidence] = field(default_factory=list)
    profile_summary: dict = field(default_factory=dict)
    reviewer_questions: list[str] = field(default_factory=list)
    decision_authority_note: str = ""


@dataclass(slots=True)
class DatasetReviewResult:
    """Complete deterministic review artifact for one dataset.

    This is the main result consumed by report writers and the optional LLM
    review stage. It preserves policy metadata and field-level suggestions.
    """

    row_count: int
    column_count: int
    policy_name: str
    policy_version: str | None
    authority_note: str | None
    fields: list[FieldReviewResult] = field(default_factory=list)
