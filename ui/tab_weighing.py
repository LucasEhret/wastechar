import streamlit as st

from data import add_weighing, delete_weighing
from dialogs import dialog_modifier_pesee
from session import save_session
from i18n import t


def render_tab_weighing() -> None:
    material_classes = st.session_state.get("material_classes", [])

    with st.expander(t("weigh_guide_title"), expanded=True):
        st.markdown(t("weigh_guide_body"))

    # Disable weighing if no collect times
    disable_weighing = (
        st.session_state["df_collect_times"].empty
        and not st.session_state.get("skip_collect_times")
    )
    if disable_weighing:
        st.warning(t("weigh_disable_warning"))

    # Entry form
    with st.form("weighing_form", border=True):
        st.markdown(t("weigh_form_title"))

        if st.session_state["weighing_error"]:
            st.warning(st.session_state["weighing_error"])

        _is_standard = st.session_state.get("saved_workflow", 0) == 0
        v = st.session_state.get("weighing_version", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.multiselect(
                t("weigh_sample_label"),
                options=list(range(1, st.session_state["saved_nb_sample"] + 1)),
                default=[1] if _is_standard else None,
                key="sample_nb",
                placeholder=t("weigh_sample_ph"),
                disabled=disable_weighing,
            )
        with col2:
            st.selectbox(
                t("weigh_class_label"),
                material_classes,
                key=f"material_class_{v}",
                index=None,
                placeholder=t("weigh_class_ph"),
                disabled=disable_weighing,
                accept_new_options=True,
            )
        with col3:
            st.selectbox(
                t("weigh_container_label"),
                ["Pas de contenant"] + st.session_state["df_containers"]["Contenant"].tolist(),
                disabled=disable_weighing,
                key="container_used",
            )

        img_file = st.file_uploader(
            t("weigh_image_label"),
            type=["jpg", "jpeg", "png"],
            key=f"weighing_image_{st.session_state['image_uploader_key']}",
        )
        if img_file:
            st.image(img_file, width=200)

        st.divider()

        col4, col5 = st.columns([3, 1], vertical_alignment="bottom")
        with col4:
            st.markdown(
                f"""
                <div style="margin-bottom: -15px; display: flex; align-items: center;">
                    <span style="font-size: 1.15rem; font-weight: 700; color: #1E293B;">
                        {t("weigh_gross_label")}
                    </span>
                    <span style="color: #DC2626; font-weight: bold; margin-left: 2px;">*</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_input(
                t("weigh_gross_label"),
                key=f"gross_weight_{v}",
                placeholder=t("weigh_gross_ph"),
                disabled=disable_weighing,
                label_visibility="hidden",
            )
        with col5:
            submitted = st.form_submit_button(
                t("weigh_add_btn"),
                use_container_width=True,
                disabled=disable_weighing,
                type="primary",
            )
        if submitted:
            add_weighing()

    # Observations
    st.write("")
    with st.container(border=True):
        st.markdown(t("weigh_obs_title"))
        st.text_area(
            t("weigh_obs_title"),
            placeholder=t("weigh_obs_ph"),
            key="global_comment",
            on_change=save_session,
            label_visibility="collapsed",
            height=80,
        )

    # Weighings history
    st.write("")
    df_w = st.session_state["df_weighings"]
    with st.expander(t("weigh_history_title", n=len(df_w)), expanded=True):
        if df_w.empty:
            st.info(t("weigh_history_empty"))
        else:
            for idx, row in df_w.iterrows():
                with st.container(border=True):
                    c_info, c_edit, c_del = st.columns([8, 1, 1], vertical_alignment="center")
                    with c_info:
                        st.markdown(f"**🔹 {row['Classe de matériau']}**")
                        contenant_disp = row["Contenant utilisé"] if row["Contenant utilisé"] else t("weigh_no_container")
                        st.markdown(
                            f"<small>📦 {t('weigh_hist_samples')} : **` {row['N° échantillon']} `** &nbsp;|&nbsp; "
                            f"{t('weigh_hist_tare')} : *{contenant_disp}* &nbsp;|&nbsp; "
                            f"{t('weigh_hist_gross')} : `{row['Poids brut']:.3f} kg` ➡️ "
                            f"**{t('weigh_hist_net')} : <span style='color:#146c43'>{row['Poids net']:.3f} kg</span>**</small>",
                            unsafe_allow_html=True,
                        )
                    with c_edit:
                        if st.button(t("btn_edit"), key=f"edit_w_{idx}", type="secondary",
                                     help=t("weigh_edit_help"), use_container_width=True):
                            dialog_modifier_pesee(idx)
                    with c_del:
                        st.button(t("btn_delete"), key=f"del_w_{idx}", type="secondary",
                                  help=t("weigh_delete_help"), use_container_width=True,
                                  on_click=delete_weighing, args=(idx,))

    st.write("")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button(t("btn_back"), use_container_width=True):
            st.session_state.step_index = 1
            st.rerun()
    with col_next:
        if st.button(t("btn_next_summary"), use_container_width=True, type="primary"):
            st.session_state.step_index = 3
            st.rerun()
