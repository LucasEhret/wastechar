"""One-click export download, generated only when the user clicks."""

from ui.report_state import app_state

import io

import streamlit as st
from report import Report

from export import build_zip_export, upload_to_dropbox, safe_export_name
from i18n import t
from report_validation import report_errors
from time_utils import local_now


def _report_snapshot() -> Report:
    """Give the deferred download thread report data without Streamlit access."""
    return Report.from_state(app_state)


def render_export_controls() -> None:
    errors = report_errors(app_state)
    if errors:
        st.warning(t("export_draft_warning") + " " + "; ".join(errors))
        return

    upload_status = app_state.setdefault("_export_upload_status", {})
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
    base_name = safe_export_name(f"Resultat_{facility}_{sensor_name}_{timestamp}")
    file_name = f"{base_name}.zip"

    upload_enabled = (
        not app_state.get("is_admin", False)
        or app_state.get("dropbox_upload_enabled", True)
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
