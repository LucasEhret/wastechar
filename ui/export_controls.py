"""One-click export download, generated only when the user clicks."""

import io

import pandas as pd
import streamlit as st

from export import build_zip_export, upload_to_dropbox
from i18n import t
from report_validation import report_errors
from time_utils import local_now


_REPORT_KEYS = (
    "df_weighings", "df_collect_times", "saved_sensor_name", "saved_test_date",
    "saved_operator_name", "saved_nb_sample", "saved_workflow",
    "saved_workflow_order", "_skip_collect_times_value", "_global_comment_value",
    "material_classes", "facility_name", "user_timezone",
)


def _report_snapshot() -> dict:
    """Give the deferred download thread report data without Streamlit access."""
    snapshot = {}
    for key in _REPORT_KEYS:
        if key in st.session_state:
            value = st.session_state[key]
            snapshot[key] = value.copy(deep=True) if isinstance(value, pd.DataFrame) else (
                value.copy() if isinstance(value, list) else value
            )
    return snapshot


def render_export_controls() -> None:
    errors = report_errors(st.session_state)
    if errors:
        st.warning(t("export_draft_warning") + " " + "; ".join(errors))
        return

    upload_status = st.session_state.setdefault("_export_upload_status", {})
    previous_upload = upload_status.pop("result", None)
    if previous_upload is True:
        st.toast(t("dropbox_success"), icon="☁️")
    elif previous_upload is False:
        st.error(t("dropbox_upload_failed"))

    snapshot = _report_snapshot()
    generated_at = local_now(snapshot.get("user_timezone"))
    timestamp = generated_at.strftime("%Y%m%d_%H%M%z")
    facility = snapshot.get("facility_name", "")
    sensor_name = snapshot["saved_sensor_name"].replace(" ", "_")
    base_name = f"Resultat_{facility}_{sensor_name}_{timestamp}"
    file_name = f"{base_name}.zip"

    upload_enabled = (
        not st.session_state.get("is_admin", False)
        or st.session_state.get("dropbox_upload_enabled", True)
    )
    upload_settings = None
    if upload_enabled:
        upload_settings = {
            key: st.secrets.get(key)
            for key in ("DROPBOX_APP_KEY", "DROPBOX_APP_SECRET", "DROPBOX_REFRESH_TOKEN")
        }
        upload_settings["DROPBOX_DESTINATION_PATH"] = st.secrets.get(
            "DROPBOX_DESTINATION_PATH", "/"
        )

    def generate_download() -> bytes:
        data = build_zip_export(base_name, generated_at, snapshot).getvalue()
        if upload_enabled:
            upload_status["result"] = upload_to_dropbox(
                io.BytesIO(data), file_name, upload_settings
            )
        return data

    st.download_button(
        t("btn_download"),
        data=generate_download,
        file_name=file_name,
        mime="application/zip",
        width="stretch",
        type="primary",
        key="download_summary",
        on_click="rerun",
    )
