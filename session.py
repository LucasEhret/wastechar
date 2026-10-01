from ui.report_state import app_state
import json
import datetime as dt
import logging
import uuid
import os
import tempfile
import streamlit as st

from config import TEMP_DIR
from weights import ensure_recorded_tare
from weighing_identity import ensure_weighing_ids

logger = logging.getLogger(__name__)
from report import Report
from report_storage import SESSION_SCHEMA_VERSION, serialize_report, deserialize_report


def _atomic_write(path, payload: str) -> None:
    """Replace the backup only after its complete replacement reaches disk."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.stem}-", suffix=".tmp",
                                         delete=False) as handle:
            temporary = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


class SessionAccessError(ValueError):
    pass


def _identity() -> tuple[str, str]:
    if app_state.get("authentication_status") is not True:
        raise SessionAccessError("Authentication required")
    owner = app_state.get("username")
    facility = app_state.get("facility_name")
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
    app_state["_save_status"] = "unsaved"


def save_observation() -> None:
    """Copy the text-area value before Streamlit removes its widget key."""
    app_state["_global_comment_value"] = app_state.get("global_comment", "")
    save_session()


def save_session() -> bool:
    """Write the current session to a temp file and report whether it succeeded."""
    mark_session_unsaved()
    try:
        app_state["df_weighings"] = ensure_weighing_ids(ensure_recorded_tare(
            app_state["df_weighings"].drop(columns=["Début", "Fin"], errors="ignore")
        ))
        data = serialize_report(
            Report.from_state(app_state), app_state["username"], dt.datetime.now(dt.timezone.utc)
        )
        _atomic_write(_session_file(), json.dumps(data, ensure_ascii=False))
    except Exception:
        app_state["_save_status"] = "save_failed"
        logger.exception("Could not save WasteChar session")
        return False

    app_state["_save_status"] = "saved"
    app_state["_last_saved_at"] = data["saved_at"]
    return True


def restore_session() -> None:
    """Load session from temp file. Called once on first load."""
    try:
        f = _session_file()
        if not f.exists():
            return
        data  = json.loads(f.read_text(encoding="utf-8"))
        report, saved_at = deserialize_report(data, Report.from_state(app_state))
        saved_at = saved_at or dt.datetime.fromtimestamp(
            f.stat().st_mtime, dt.timezone.utc
        ).isoformat()
        # All decoding succeeds before the canonical report is replaced.
        if "_report" in app_state:
            app_state["_report"] = report
        else:
            app_state.update(report.to_state())
        app_state["skip_collect_times"] = report.skip_collection_times
        app_state["_save_status"] = "saved"
        app_state["_last_saved_at"] = saved_at
        for key in list(app_state):
            if key in ("global_comment", "_operator_name", "_sensor_name", "_nb_sample",
                       "_test_date", "workflow_type_seg", "workflow_order_seg", "_table_draft") or key.startswith(("_start_", "_end_")):
                app_state.pop(key, None)
    except Exception:
        app_state["_save_status"] = "restore_failed"
        logger.exception("Could not restore WasteChar session")


def clear_session() -> None:
    try:
        _session_file().unlink(missing_ok=True)
    except Exception:
        pass
