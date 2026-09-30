import streamlit as st

from config import APP_VERSION
from i18n import LANGUAGES, set_lang, t
from ui.save_status import render_save_status
from time_utils import DEFAULT_TIMEZONE


def render_sidebar(authenticator) -> None:
    facility = st.session_state.get("facility_name", "")

    with st.sidebar:
        st.image(".streamlit/images/logo-wasteflow-trademark.png", width=150)
        st.markdown(f"### {facility}")
        st.caption(t("auth_connected_as", name=st.session_state["name"]))
        st.caption(t("sidebar_timezone", timezone=st.session_state.get("user_timezone", DEFAULT_TIMEZONE)))
        authenticator.logout(t("btn_logout"), location="sidebar")

        st.divider()
        if st.session_state.get("_save_status", "new") == "new":
            st.info(t("sidebar_no_report"))
        else:
            st.caption(t("sidebar_report_title"))
            st.caption(t(
                "sidebar_report_details",
                date=st.session_state.get("saved_test_date") or "—",
                sensor=st.session_state.get("saved_sensor_name") or "—",
            ))
            st.caption(t("sidebar_weighings_count", n=len(st.session_state["df_weighings"])))
            render_save_status()

        st.divider()
        st.selectbox(
            t("sidebar_language"),
            LANGUAGES,
            index=LANGUAGES.index(st.session_state.get("lang", "FR")),
            on_change=lambda: set_lang(st.session_state["_lang_sel"]),
            key="_lang_sel",
        )
        st.toggle(t("sidebar_show_tutorials"), key="show_tutorials")

        if st.session_state.get("is_admin", False):
            st.selectbox(
                t("sidebar_preview_as"),
                options=st.session_state.get("all_facilities", []),
                key="_preview_facility",
            )

        st.caption(t("sidebar_version", version=APP_VERSION))
