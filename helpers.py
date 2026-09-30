import re
import datetime as dt
from pathlib import Path

import streamlit as st

from weights import gross_weights


def inject_css() -> None:
    css = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)



def check_entry_typo(text: str) -> bool:
    try:
        gross_weights(text)
        return True
    except ValueError:
        return False


def parse_time_str(s: str) -> dt.time:
    """Parse a time string in many formats into a dt.time.

    Accepted: HH:MM:SS, HH:MM, HHMMSS, HHMM,
              H:MM:SS, H:MM, HH.MM.SS, HH-MM-SS,
              HH MM SS, HH MM (space-separated).
    """
    s = s.strip()
    s = re.sub(r"\s+", " ", s)

    m = re.fullmatch(r"(\d{1,2})[:\.\-,](\d{2})(?:[:\.\-,](\d{2}))?", s)
    if m:
        return dt.time(int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))

    m = re.fullmatch(r"(\d{1,2}) (\d{2})(?: (\d{2}))?", s)
    if m:
        return dt.time(int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))

    m = re.fullmatch(r"(\d{2})(\d{2})(\d{2})", s)
    if m:
        return dt.time(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.fullmatch(r"(\d{2})(\d{2})", s)
    if m:
        return dt.time(int(m.group(1)), int(m.group(2)), 0)

    raise ValueError(f"Format non reconnu : '{s}'")


def time_text_widget(label: str, key: str, on_change_callback) -> None:
    st.text_input(label, placeholder="hh:mm:ss",
                  key=key, on_change=on_change_callback)


def get_sample_collect_times(sample_id: int, state=None) -> dict | None:
    state = st.session_state if state is None else state
    existing = state["df_collect_times"]
    if existing.empty or "Echantillon" not in existing.columns:
        return None
    row = existing.loc[existing["Echantillon"] == sample_id]
    if row.empty:
        return None
    if not row.iloc[0].get("Heure de début") or not row.iloc[0].get("Heure de fin"):
        return None
    sample_date = (
        row.iloc[0]["Date"]
        if "Date" in row.columns
        else state["saved_test_date"]
    )
    try:
        t_start = dt.time.fromisoformat(row.iloc[0]["Heure de début"])
        t_end   = dt.time.fromisoformat(row.iloc[0]["Heure de fin"])
    except (TypeError, ValueError):
        return None
    return {
        "Début": dt.datetime.combine(sample_date, t_start),
        "Fin":   dt.datetime.combine(sample_date, t_end),
    }


def sample_ids_from_label(label) -> tuple[int, ...]:
    """Parse the sample references stored on a weighing."""
    try:
        parts = tuple(int(part.strip()) for part in str(label).split(","))
    except ValueError:
        raise ValueError("Invalid sample reference") from None
    if not parts or any(part < 1 for part in parts) or len(set(parts)) != len(parts):
        raise ValueError("Invalid sample reference")
    return parts


def get_weighing_collect_times(label, state=None) -> tuple[str, str]:
    """Resolve current collection times for all samples on a weighing."""
    sample_ids = sample_ids_from_label(label)
    starts, ends = [], []
    for sample_id in sample_ids:
        times = get_sample_collect_times(sample_id, state)
        if times is None:
            return "", ""
        prefix = f"{sample_id}: " if len(sample_ids) > 1 else ""
        starts.append(prefix + str(times["Début"]))
        ends.append(prefix + str(times["Fin"]))
    return "; ".join(starts), "; ".join(ends)


def get_container_weight(container_name: str) -> float:
    if not container_name:
        return 0.0
    row = st.session_state["df_containers"].loc[
        st.session_state["df_containers"]["Contenant"] == container_name
    ]
    if row.empty:
        return 0.0
    return float(row.iloc[0]["Poids à vide"])


def _clean_time_widget_keys(nb_sample: int) -> None:
    """Remove widget keys for sample indices above nb_sample."""
    i = nb_sample + 1
    while f"_start_{i}" in st.session_state or f"_end_{i}" in st.session_state:
        for key in (f"_start_{i}", f"_end_{i}", f"_date_{i}"):
            st.session_state.pop(key, None)
        i += 1
