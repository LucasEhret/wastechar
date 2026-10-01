"""Validation of saved report data, independent of transient widget values."""

import datetime as dt

import pandas as pd

from helpers import parse_time_str, sample_ids_from_label
from i18n import t
from weights import invalid_weighing_rows
from report import Report


def metadata_errors(state) -> list[str]:
    state = state if isinstance(state, Report) else Report.from_state(state)
    errors = []
    if not str(state.operator or "").strip():
        errors.append(t("meta_missing_operator"))
    if not str(state.sensor or "").strip():
        errors.append(t("meta_missing_sensor"))
    if not isinstance(state.test_date, dt.date):
        errors.append(t("meta_missing_date"))
    try:
        count = int(state.sample_count)
        if count < 1:
            raise ValueError
    except (TypeError, ValueError):
        errors.append(t("meta_invalid_sample_count"))
        return errors

    if state.skip_collection_times:
        return errors
    times = state.collection_times
    if "Echantillon" not in times.columns:
        for i in range(1, count + 1):
            errors.extend((t("meta_missing_start", n=i), t("meta_missing_end", n=i)))
        return errors
    for i in range(1, count + 1):
        rows = times.loc[times["Echantillon"] == i]
        if rows.empty:
            errors.extend((t("meta_missing_start", n=i), t("meta_missing_end", n=i)))
            continue
        row = rows.iloc[0]
        start_raw, end_raw = row.get("Heure de début"), row.get("Heure de fin")
        start = start_raw.strip() if isinstance(start_raw, str) else ""
        end = end_raw.strip() if isinstance(end_raw, str) else ""
        if not start:
            errors.append(t("meta_missing_start", n=i))
        if not end:
            errors.append(t("meta_missing_end", n=i))
        if not start or not end:
            continue
        try:
            start_time = parse_time_str(start)
        except ValueError:
            errors.append(t("meta_error_start", n=i, raw=start))
            continue
        try:
            end_time = parse_time_str(end)
        except ValueError:
            errors.append(t("meta_error_end", n=i, raw=end))
            continue
        if end_time <= start_time:
            errors.append(t("meta_error_time_order", n=i))
    return errors


def report_errors(state) -> list[str]:
    state = state if isinstance(state, Report) else Report.from_state(state)
    errors = metadata_errors(state)
    weighings = state.weighings
    if weighings.empty:
        errors.append(t("report_missing_weighings"))
    elif invalid_weighing_rows(weighings):
        errors.append(t("report_invalid_weighings"))
    if not weighings.empty:
        count = state.sample_count
        try:
            valid_samples = set(range(1, int(count) + 1))
            for label in weighings["N° échantillon"]:
                if any(part not in valid_samples for part in sample_ids_from_label(label)):
                    raise ValueError
        except (KeyError, TypeError, ValueError):
            errors.append(t("report_invalid_samples"))
    return errors
