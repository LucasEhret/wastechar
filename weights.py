"""Weight validation shared by every entry mode and report output."""

import math

import pandas as pd


def nonnegative_weight(value) -> float:
    """Accept finite kilogram values, including an explicit zero."""
    try:
        weight = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Weight must be a finite non-negative number") from None
    if not math.isfinite(weight) or weight < 0:
        raise ValueError("Weight must be a finite non-negative number")
    return weight


def gross_weights(text: str) -> list[float]:
    parts = text.strip().split()
    if not parts:
        raise ValueError("Enter at least one weight")
    return [nonnegative_weight(part.replace(",", ".")) for part in parts]


def net_weight(gross, tare) -> float:
    result = nonnegative_weight(gross) - nonnegative_weight(tare)
    if result < 0:
        raise ValueError("Gross weight is below tare")
    return result


def ensure_recorded_tare(df: pd.DataFrame) -> pd.DataFrame:
    """Infer the recorded tare in older reports from their gross and net weights."""
    result = df.copy()
    if "Tare" not in result.columns:
        result["Tare"] = pd.Series(index=result.index, dtype=float)
    for index, row in result.iterrows():
        if pd.notna(row["Tare"]):
            continue
        try:
            gross = nonnegative_weight(row["Poids brut"])
            net = nonnegative_weight(row["Poids net"])
            if net <= gross:
                result.at[index, "Tare"] = gross - net
        except (KeyError, ValueError):
            pass
    return result


def invalid_weighing_rows(df: pd.DataFrame) -> list[int]:
    """Find existing rows that should not appear in a report."""
    invalid = []
    for index, row in df.iterrows():
        try:
            gross = nonnegative_weight(row["Poids brut"])
            net = nonnegative_weight(row["Poids net"])
            if net > gross:
                raise ValueError("Net exceeds gross")
            if "Tare" in row.index:
                tare = nonnegative_weight(row["Tare"])
                if not math.isclose(gross - tare, net, rel_tol=1e-9, abs_tol=1e-9):
                    raise ValueError("Recorded tare does not match net weight")
        except (KeyError, ValueError):
            invalid.append(index)
    return invalid
