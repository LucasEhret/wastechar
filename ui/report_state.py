"""Route committed data to one Report while leaving widget state in Streamlit."""

from collections.abc import MutableMapping

import streamlit as st

from report import REPORT_FIELDS, Report


def initialize_report() -> Report:
    if "_report" not in st.session_state:
        report = Report.from_state(st.session_state)
        st.session_state["_report"] = report
        for key in REPORT_FIELDS:
            st.session_state.pop(key, None)
    return st.session_state["_report"]


def detach_report() -> None:
    """Expose old keys temporarily when resetting for a different identity."""
    report = st.session_state.pop("_report", None)
    if report is not None:
        st.session_state.update(report.to_state())


class ReportState(MutableMapping):
    """UI compatibility adapter; the model is the only committed-data store."""

    def __getitem__(self, key):
        report = st.session_state.get("_report")
        if report is not None and key in REPORT_FIELDS:
            return report[key]
        return st.session_state[key]

    def __setitem__(self, key, value):
        report = st.session_state.get("_report")
        if report is not None and key in REPORT_FIELDS:
            setattr(report, REPORT_FIELDS[key], value)
        else:
            st.session_state[key] = value

    def __delitem__(self, key):
        report = st.session_state.get("_report")
        if report is not None and key in REPORT_FIELDS:
            setattr(report, REPORT_FIELDS[key], getattr(Report(), REPORT_FIELDS[key]))
        else:
            del st.session_state[key]

    def __iter__(self):
        keys = list(st.session_state)
        if "_report" in st.session_state:
            keys.extend(key for key in REPORT_FIELDS if key not in keys)
        return iter(keys)

    def __len__(self):
        return sum(1 for _ in self)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


app_state = ReportState()
