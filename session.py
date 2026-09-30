import json
import datetime as dt
import io
import logging
import uuid
import pandas as pd
import streamlit as st

from config import TEMP_DIR
from weights import ensure_recorded_tare
from weighing_identity import ensure_weighing_ids
from time_utils import local_today

logger = logging.getLogger(__name__)


class SessionAccessError(ValueError):
    pass


def _identity() -> tuple[str, str]:
    if st.session_state.get("authentication_status") is not True:
        raise SessionAccessError("Authentication required")
    owner = st.session_state.get("username")
    facility = st.session_state.get("facility_name")
    if not isinstance(owner, str) or not owner or not isinstance(facility, str) or not facility:
        raise SessionAccessError("Session identity unavailable")
    return owner, facility


def _valid_token(value) -> str:
    if not isinstance(value, str):
        raise SessionAccessError("Invalid session token")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        raise SessionAccessError("Invalid session token") from None
    if value not in (parsed.hex, str(parsed)):
        raise SessionAccessError("Invalid session token")
    return parsed.hex


def _session_file():
    owner, facility = _identity()
    token = _valid_token(st.query_params.get("session"))
    root = TEMP_DIR.resolve()
    path = (root / f"{token}.json").resolve()
    if not path.is_relative_to(root) or path.parent != root:
        raise SessionAccessError("Session path outside storage directory")
    if path.exists():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            raise SessionAccessError("Unreadable session") from None
        if not isinstance(saved, dict) or saved.get("owner") != owner or saved.get("facility") != facility:
            raise SessionAccessError("Session belongs to another identity or is unbound")
    return path


def prepare_session_token() -> None:
    """Use a fresh token for missing, malformed, or inaccessible URLs."""
    try:
        _session_file()
    except SessionAccessError:
        st.query_params["session"] = uuid.uuid4().hex


def mark_session_unsaved() -> None:
    """Mark edited report data as needing a successful session save."""
    st.session_state["_save_status"] = "unsaved"


def save_observation() -> None:
    """Copy the text-area value before Streamlit removes its widget key."""
    st.session_state["_global_comment_value"] = st.session_state.get("global_comment", "")
    save_session()


def save_session() -> bool:
    """Write the current session to a temp file and report whether it succeeded."""
    mark_session_unsaved()
    try:
        st.session_state["df_weighings"] = ensure_weighing_ids(ensure_recorded_tare(
            st.session_state["df_weighings"].drop(columns=["Début", "Fin"], errors="ignore")
        ))
        data = {
            "owner": st.session_state["username"],
            "facility": st.session_state["facility_name"],
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
                "date":               str(st.session_state.get("saved_test_date", local_today(st.session_state.get("user_timezone")))),
                "global_comment":     st.session_state.get("_global_comment_value", ""),
                "skip_collect_times": st.session_state.get("_skip_collect_times_value", False),
            },
        }
        _session_file().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        st.session_state["_save_status"] = "save_failed"
        logger.exception("Could not save WasteChar session")
        return False

    st.session_state["_save_status"] = "saved"
    st.session_state["_last_saved_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return True


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

    try:
        f = _session_file()
        if not f.exists():
            return
        data  = json.loads(f.read_text(encoding="utf-8"))
        sensor_list = st.session_state.get("sensor_list", [""])

        df_w = _restore_df(
            data["df_weighings"],
            {"N° échantillon": str, "Poids brut": float, "Poids net": float},
        )
        if df_w is not None:
            st.session_state["df_weighings"] = ensure_weighing_ids(ensure_recorded_tare(
                df_w.drop(columns=["Début", "Fin"], errors="ignore")
            ))

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
            meta.get("date", str(local_today(st.session_state.get("user_timezone"))))
        )
        st.session_state["_global_comment_value"] = meta.get("global_comment", "")
        st.session_state.pop("global_comment", None)
        st.session_state["skip_collect_times"]  = meta.get("skip_collect_times", False)
        st.session_state["_skip_collect_times_value"] = st.session_state["skip_collect_times"]

        wf = meta.get("workflow", 0)
        if isinstance(wf, str):
            wf = {
                "Standard": 0, "Estándar": 0, "Single": 0, "Unique": 0, "Único": 0,
                "Multi-échantillon": 1, "Multi-sample": 1,
                "Multi-muestra": 1, "Multiple": 1, "Múltiple": 1,
                **{label: value for value, label in WORKFLOW_MAP.items()},
            }.get(wf, 0)
        st.session_state["saved_workflow"] = wf

        wfo = meta.get("workflow_order", 0)
        if isinstance(wfo, str):
            wfo = {
                "A": 0, "B": 1, "Standard": 0, "Estándar": 0,
                "Inverse": 1, "Contrarrestar": 1,
                "Before weighing": 0, "After weighing": 1,
                "Avant la pesée": 0, "Après la pesée": 1,
                "Antes del pesaje": 0, "Después del pesaje": 1,
            }.get(wfo, 0)
        st.session_state["saved_workflow_order"] = wfo

        # Clear widget shadow keys so init_metadata_widget_state re-reads
        for k in ("_operator_name", "_sensor_name", "_nb_sample", "_test_date",
                  "workflow_type_seg", "workflow_order_seg"):
            st.session_state.pop(k, None)

        st.session_state["_save_status"] = "saved"
        st.session_state["_last_saved_at"] = dt.datetime.fromtimestamp(
            f.stat().st_mtime, dt.timezone.utc
        ).isoformat()
    except Exception:
        st.session_state["_save_status"] = "restore_failed"
        logger.exception("Could not restore WasteChar session")


def clear_session() -> None:
    try:
        _session_file().unlink(missing_ok=True)
    except Exception:
        pass
