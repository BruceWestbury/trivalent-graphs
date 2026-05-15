"""
src.cache_inspect.reductions
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from algebra.linear_combinations import LinearCombination


@dataclass(frozen=True)
class SourceRelationRecord:
    """One cached source-relation substitution."""

    source: str
    site: tuple[int, ...]
    relation: str
    replacement: LinearCombination

    @classmethod
    def from_json(cls, data: dict) -> "SourceRelationRecord":
        return cls(
            source=str(data["source"]),
            site=tuple(int(d) for d in data["site"]),
            relation=str(data["relation"]),
            replacement=LinearCombination.from_json(data["replacement"]),
        )


def load_source_relation_cache(path: str | Path) -> list[SourceRelationRecord]:
    """Load a source-relation cache file."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [SourceRelationRecord.from_json(record) for record in data]


def source_relation_cache_summary(
    records: list[SourceRelationRecord],
) -> dict:
    """Return a small summary of a source-relation cache."""
    replacement_lengths = [len(record.replacement.terms) for record in records]

    if not replacement_lengths:
        return {
            "records": 0,
            "relations": [],
            "min_replacement_terms": 0,
            "max_replacement_terms": 0,
        }

    return {
        "records": len(records),
        "relations": sorted({record.relation for record in records}),
        "min_replacement_terms": min(replacement_lengths),
        "max_replacement_terms": max(replacement_lengths),
    }
