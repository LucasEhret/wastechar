import datetime as dt
import streamlit as st

from config import APP_VERSION, DEV_MODE, ORDER_MAP
from export import build_zip_export, upload_to_dropbox
from dialogs import dialog_nouvelle_saisie
from i18n import t, set_lang, LANGUAGES


def render_sidebar(authenticator) -> None:
    facility   = st.session_state.get("facility_name", "")
    is_admin   = st.session_state.get("is_admin", False)
    all_facils = st.session_state.get("all_facilities", [])

    with st.sidebar:
        st.selectbox("🌐 Language", LANGUAGES,
             index=LANGUAGES.index(st.session_state.get("lang", "FR")),
             on_change=lambda: set_lang(st.session_state["_lang_sel"]),
             key="_lang_sel", width=100)
        st.divider()
        st.image(".streamlit/images/logo-wasteflow-trademark.png", width=180)
        st.caption(t("sidebar_version", version=APP_VERSION))
        st.markdown(f"## {facility}")
        st.caption(t("auth_connected_as", name=st.session_state["name"]))
        authenticator.logout(t("btn_logout"), location="sidebar")
        # st.divider()

        if is_admin:
            with st.container(border=True):
                st.caption(f"**{t('sidebar_preview_as')}**")
                st.selectbox(
                    t("sidebar_preview_as"),
                    options=all_facils,
                    key="_preview_facility",
                    label_visibility="collapsed",
                )
            # st.divider()

        
        # st.write("")

        if st.button(
            t("btn_new_session"),
            width="stretch",
            type="secondary",
            help=t("sidebar_new_session_help"),
            key="new_session"
        ):
            dialog_nouvelle_saisie()

        st.divider()

        # Session info
        _wf_options = [t("meta_wf_standard"), t("meta_wf_multi")]
        _wf_idx     = st.session_state.get("saved_workflow", 0)
        _wf_label   = _wf_options[_wf_idx] if _wf_idx is not None else "—"
        _wfo_label  = ORDER_MAP.get(st.session_state.get("saved_workflow_order"), "—")  # type: ignore
        with st.container(border=True):
            st.markdown(t("sidebar_config_title"))
            st.markdown(
                f"""
                <div style="font-size: 0.9rem; line-height: 1.6;">
                    👤 <b>{t('sidebar_operator')} :</b> {st.session_state.get('saved_operator_name') or '—'}<br>
                    📅 <b>{t('sidebar_date')} :</b> {st.session_state.get('saved_test_date') or '—'}<br>
                    📡 <b>{t('sidebar_sensor')} :</b> {st.session_state.get('saved_sensor_name') or '—'}<br>
                    ⚙️ <b>{t('sidebar_workflow')} :</b> {_wf_label} (<b>{_wfo_label}</b>)
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown(f"⚖️ {t('sidebar_weighings')} : **` {len(st.session_state['df_weighings'])} `**")

        st.write("")

        # Export
        has_data = not st.session_state["df_weighings"].empty
        if has_data:
            st.markdown(t("sidebar_export_title"))
            timestamp   = dt.datetime.now().strftime("%Y%m%d_%H%M")
            sensor_name = st.session_state["saved_sensor_name"].replace(" ", "_")
            base_name   = f"Resultat_{facility}_{sensor_name}_{timestamp}"
            zip_data    = build_zip_export()

            if st.download_button(
                t("btn_download"),
                data=zip_data,
                file_name=f"{base_name}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
                key="download_sidebar"
            ) and not DEV_MODE:
                with st.spinner(t("dropbox_uploading")):
                    try:
                        if upload_to_dropbox(zip_data, f"{base_name}.zip"):
                            st.toast(t("dropbox_success"), icon="☁️")
                    except Exception:
                        pass

            if DEV_MODE:
                st.caption(t("dev_mode_warning"))
        else:
            st.info(t("sidebar_no_data"))

        st.divider()

        with st.expander(t("sidebar_guide_title")):
            st.info(t("sidebar_guide_intro"))
            st.markdown(t("sidebar_guide_body"))

        st.link_button("🌐 wasteflow.ai", "https://wasteflow.ai", use_container_width=True)
        st.link_button(
            t("btn_timing_app"),
            "https://deltatgit-e8vsfavsgwkxhq9jw4rzoq.streamlit.app/",
            use_container_width=True,
        )
        st.link_button("✉️ Contact", "mailto:lucas.ehret@wasteflow.ai", use_container_width=True)
