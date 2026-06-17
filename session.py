import json
import datetime as dt
import io
import pandas as pd
import streamlit as st

from config import TEMP_DIR


def _session_file():
    return TEMP_DIR / f"{st.query_params.get('session', 'nosession')}.json"


def save_session() -> None:
    """Write current session to a temp file. Called after every data action."""
    try:
        sensor_list = st.session_state.get("sensor_list", [""])
        data = {
            "df_weighings": (
                st.session_state["df_weighings"]
                .drop(columns=["Image"], errors="ignore")
                .to_json(orient="records")
            ),
            "df_containers": st.session_state["df_containers"].to_json(orient="records"),
            "df_collect_times": (
                st.session_state["df_collect_times"]
                .astype({"Date": str}, errors="ignore")
                .to_json(orient="records")
            ),
            "metadata": {
                "workflow":           st.session_state.get("saved_workflow", 0),
                "workflow_order":     st.session_state.get("saved_workflow_order", 0),
                "operator":           st.session_state.get("saved_operator_name", ""),
                "sensor":             st.session_state.get("saved_sensor_name", ""),
                "nb_sample":          st.session_state.get("saved_nb_sample", 1),
                "date":               str(st.session_state.get("saved_test_date", dt.date.today())),
                "global_comment":     st.session_state.get("global_comment", ""),
                "skip_collect_times": st.session_state.get("skip_collect_times", False),
            },
        }
        _session_file().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _restore_df(
    json_str: str,
    dtype_map: dict,
    date_cols: list | None = None,
) -> pd.DataFrame | None:
    df = pd.read_json(io.StringIO(json_str))
    if df.empty:
        return None
    for col, dtype in dtype_map.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    for col in (date_cols or []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date
    return df


def restore_session() -> None:
    """Load session from temp file. Called once on first load."""
    from config import WORKFLOW_MAP  # avoid circular at module level

    f = _session_file()
    if not f.exists():
        return
    try:
        data  = json.loads(f.read_text(encoding="utf-8"))
        sensor_list = st.session_state.get("sensor_list", [""])

        df_w = _restore_df(
            data["df_weighings"],
            {"N° échantillon": str, "Poids brut": float, "Poids net": float},
        )
        if df_w is not None:
            st.session_state["df_weighings"] = df_w

        df_c = _restore_df(
            data["df_containers"],
            {"Contenant": str, "Poids à vide": float},
        )
        if df_c is not None:
            st.session_state["df_containers"] = df_c

        df_t = _restore_df(
            data["df_collect_times"],
            {"Echantillon": int, "Heure de début": str, "Heure de fin": str},
            date_cols=["Date"],
        )
        if df_t is not None:
            st.session_state["df_collect_times"] = df_t

        meta = data["metadata"]
        st.session_state["saved_operator_name"] = meta.get("operator", "")
        st.session_state["saved_sensor_name"]   = meta.get("sensor", sensor_list[0] if sensor_list else "")
        st.session_state["saved_nb_sample"]     = int(meta.get("nb_sample", 1))
        st.session_state["saved_test_date"]     = dt.date.fromisoformat(
            meta.get("date", str(dt.date.today()))
        )
        st.session_state["global_comment"]      = meta.get("global_comment", "")
        st.session_state["skip_collect_times"]  = meta.get("skip_collect_times", False)
        st.session_state["_skip_collect_times_value"] = st.session_state["skip_collect_times"]

        wf = meta.get("workflow", 0)
        if isinstance(wf, str):
            _wf_titles = list(WORKFLOW_MAP.values())
            wf = _wf_titles.index(wf) if wf in _wf_titles else 0
        st.session_state["saved_workflow"] = wf

        wfo = meta.get("workflow_order", 0)
        if isinstance(wfo, str):
            wfo = {"A": 0, "B": 1}.get(wfo, 0)
        st.session_state["saved_workflow_order"] = wfo

        # Clear widget shadow keys so init_metadata_widget_state re-reads
        for k in ("_operator_name", "_sensor_name", "_nb_sample", "_test_date",
                  "workflow_type", "workflow_order"):
            st.session_state.pop(k, None)

    except Exception:
        pass


def clear_session() -> None:
    try:
        _session_file().unlink(missing_ok=True)
    except Exception:
        pass
