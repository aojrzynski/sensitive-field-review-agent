from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DatasetMetadata:
    source_path: Path
    file_name: str
    file_extension: str
    sheet_name: str | None
    row_count: int
    column_count: int
    columns: list[str]


@dataclass(slots=True)
class ReviewLevelPolicy:
    name: str
    description: str | None = None


@dataclass(slots=True)
class CategoryPolicy:
    name: str
    description: str | None = None
    default_review_level: str = "medium"
    name_keywords: list[str] = field(default_factory=list)
    pattern_families: list[str] = field(default_factory=list)
    reviewer_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FieldOverride:
    field_name: str
    category: str
    review_level: str
    reason: str | None = None


@dataclass(slots=True)
class RedactionConfig:
    max_redacted_examples_per_field: int = 3
    never_include_raw_values: bool = True


@dataclass(slots=True)
class ThresholdsConfig:
    pattern_match_min_count: int = 2
    pattern_match_min_ratio: float = 0.6
    free_text_avg_length: int = 40


@dataclass(slots=True)
class SensitiveFieldPolicy:
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
    length: int
    letters_count: int
    digits_count: int
    whitespace_count: int
    punctuation_or_symbol_count: int
    generalized_shape: str


@dataclass(slots=True)
class FieldProfile:
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
    row_count: int
    column_count: int
    field_profiles: list[FieldProfile] = field(default_factory=list)


@dataclass(slots=True)
class FieldSignalEvidence:
    checked_count: int | None = None
    matched_count: int | None = None
    matched_ratio: float | None = None
    min_count: int | None = None
    min_ratio: float | None = None
    threshold_met: bool | None = None
    matched_keyword: str | None = None


@dataclass(slots=True)
class FieldSignal:
    column_name: str
    signal_type: str
    signal_name: str
    policy_category: str
    evidence: FieldSignalEvidence
    matched: bool
    notes: str


@dataclass(slots=True)
class FieldSignalSet:
    column_name: str
    signals: list[FieldSignal] = field(default_factory=list)


@dataclass(slots=True)
class DatasetSignals:
    row_count: int
    column_count: int
    fields: list[FieldSignalSet] = field(default_factory=list)
