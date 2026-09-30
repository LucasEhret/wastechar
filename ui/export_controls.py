import io

import streamlit as st

from export import build_zip_export, upload_to_dropbox
from i18n import t
from report_validation import report_errors
from time_utils import local_now


def render_export_controls() -> None:
    """Prepare the review export on request and reuse it until the report changes."""
    errors = report_errors(st.session_state)
    if errors:
        st.warning(t("export_draft_warning") + "\n\n" + "\n".join(f"- {error}" for error in errors))
        st.session_state.pop("_prepared_export", None)
        return
    revision = st.session_state.get("_export_revision", 0)
    owner = st.session_state.get("username", "")
    facility = st.session_state.get("facility_name", "")
    timezone_name = st.session_state.get("user_timezone", "")
    prepared = st.session_state.get("_prepared_export")

    if prepared is not None and (
        prepared["revision"] != revision
        or prepared["owner"] != owner
        or prepared["facility"] != facility
        or prepared.get("timezone") != timezone_name
    ):
        st.session_state.pop("_prepared_export", None)
        prepared = None

    if prepared is None and st.button(
        t("btn_prepare_export"), width="stretch", type="primary",
        key="prepare_summary",
    ):
        generated_at = local_now(st.session_state.get("user_timezone"))
        timestamp = generated_at.strftime("%Y%m%d_%H%M%z")
        sensor_name = st.session_state["saved_sensor_name"].replace(" ", "_")
        base_name = f"Resultat_{facility}_{sensor_name}_{timestamp}"
        with st.spinner(t("export_preparing")):
            try:
                zip_data = build_zip_export(base_name, generated_at)
            except Exception as exc:
                st.error(t("export_prepare_failed", error=str(exc)))
                return
        prepared = {
            "revision": revision,
            "owner": owner,
            "facility": facility,
            "timezone": timezone_name,
            "file_name": f"{base_name}.zip",
            "data": zip_data.getvalue(),
        }
        st.session_state["_prepared_export"] = prepared

    if prepared is not None:
        if st.download_button(
            t("btn_download"),
            data=prepared["data"],
            file_name=prepared["file_name"],
            mime="application/zip",
            width="stretch",
            type="primary",
            key="download_summary",
        ) and (
            not st.session_state.get("is_admin", False)
            or st.session_state.get("dropbox_upload_enabled", True)
        ):
            with st.spinner(t("dropbox_uploading")):
                if upload_to_dropbox(io.BytesIO(prepared["data"]), prepared["file_name"]):
                    st.toast(t("dropbox_success"), icon="☁️")
