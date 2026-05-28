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
