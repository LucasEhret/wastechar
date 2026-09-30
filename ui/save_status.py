import datetime as dt

import streamlit as st

from i18n import t
from session import save_session
from report_validation import metadata_errors
from time_utils import account_timezone


def render_save_status() -> None:
    """Show whether committed report data has reached the server session file."""
    status = st.session_state.get("_save_status", "new")

    if status == "saved":
        saved_at = st.session_state.get("_last_saved_at")
        if saved_at:
            local_time = dt.datetime.fromisoformat(saved_at).astimezone(
                account_timezone(st.session_state.get("user_timezone"))
            )
            st.success(t("sidebar_save_saved_at", time=local_time.strftime("%H:%M:%S %Z")))
        else:
            st.success(t("sidebar_save_saved"))
        draft_errors = metadata_errors(st.session_state)
        if draft_errors:
            st.warning(t("meta_draft_warning") + " " + "; ".join(draft_errors))
        weighings = st.session_state.get("df_weighings")
        if weighings is not None and "Image" in weighings.columns and weighings["Image"].map(
            lambda image: isinstance(image, bytes)
        ).any():
            st.caption(t("sidebar_save_photos_warning"))
    elif status == "save_failed":
        st.error(t("sidebar_save_failed"))
        st.button(t("sidebar_save_retry"), on_click=save_session, width="stretch")
    elif status == "restore_failed":
        st.error(t("sidebar_restore_failed"))
    elif status == "unsaved":
        st.info(t("sidebar_save_unsaved"))
    else:
        st.info(t("sidebar_save_new"))
