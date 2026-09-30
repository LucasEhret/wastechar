import streamlit as st

from data import add_container, remove_container
from i18n import t


def render_tab_containers() -> None:
    if st.session_state.get("show_tutorials", True):
        with st.expander(t("cont_guide_title"), expanded=True):
            st.markdown(t("cont_guide_body"))

    col_left, col_right = st.columns(2, gap="small")

    with col_left:
        with st.container(border=True):
            st.markdown(t("cont_add_title"))
            if st.session_state["container_error"]:
                st.warning(st.session_state["container_error"])

            st.text_input(
                t("cont_name_label"),
                placeholder=t("cont_name_ph"),
                key="container_name",
            )
            st.number_input(
                t("cont_weight_label"),
                min_value=0.0, step=0.1, format="%.3f",
                key="container_weight",
            )
            st.write("")
            st.button(
                t("cont_add_btn"),
                width="stretch",
                on_click=add_container,
                key="add_container_button",
                type="primary",
            )

    with col_right:
        with st.container(border=True):
            st.markdown(t("cont_list_title"))
            if st.session_state["df_containers"].empty:
                st.info(t("cont_empty_info"))
            else:
                for _, row in st.session_state["df_containers"].iterrows():
                    used_count = int((
                        st.session_state["df_weighings"]["Contenant utilisé"] == row["Contenant"]
                    ).sum())
                    with st.container(border=True):
                        c_info, c_action = st.columns([4, 1], vertical_alignment="center")
                        with c_info:
                            st.markdown(f"**📦 {row['Contenant']}**")
                            st.caption(t("cont_tare_caption", tare=row["Poids à vide"]))
                            if used_count:
                                st.caption(t("cont_used_cannot_delete", n=used_count))
                        with c_action:
                            if st.button(
                                t("btn_delete"), key=f"del_{row['Contenant']}",
                                type="secondary", help=t("cont_delete_help"),
                                disabled=bool(used_count),
                            ):
                                remove_container(row["Contenant"])

    st.write("")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button(t("btn_back"), width="stretch"):
            st.session_state.step_index = 0
            st.rerun()
    with col_next:
        if st.button(t("btn_next_weighing"), width="stretch", type="primary"):
            st.session_state.step_index = 2
            st.rerun()
