from __future__ import annotations


ACTIVE_SOURCE_STATE = "active"
FILTERED_SOURCE_STATES = {"superseded", "deprecated", "deleted"}
VALID_SOURCE_STATES = {ACTIVE_SOURCE_STATE, *FILTERED_SOURCE_STATES}
SOURCE_LIFECYCLE_POLICY = "active_sources_only"


def source_lifecycle_state(row: dict) -> str:
    value = str(row.get("source_lifecycle_state") or ACTIVE_SOURCE_STATE).strip().lower()
    return value if value in VALID_SOURCE_STATES else ACTIVE_SOURCE_STATE


def is_active_source(row: dict) -> bool:
    return source_lifecycle_state(row) == ACTIVE_SOURCE_STATE
