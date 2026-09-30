"""Stable identifiers for recorded weighings."""

import uuid

import pandas as pd


WEIGHING_ID_COLUMN = "__weighing_id"


def new_weighing_id() -> str:
    return uuid.uuid4().hex


def ensure_weighing_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Assign IDs to legacy rows, keeping existing unique IDs unchanged."""
    result = df.copy()
    if WEIGHING_ID_COLUMN not in result.columns:
        result[WEIGHING_ID_COLUMN] = pd.Series(index=result.index, dtype=str)
    seen = set()
    for index, value in result[WEIGHING_ID_COLUMN].items():
        try:
            valid = isinstance(value, str) and value == uuid.UUID(value).hex
        except (ValueError, AttributeError):
            valid = False
        if not valid or value in seen:
            value = new_weighing_id()
            result.at[index, WEIGHING_ID_COLUMN] = value
        seen.add(value)
    return result
