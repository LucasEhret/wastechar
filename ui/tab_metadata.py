import streamlit as st

from data import init_metadata_widget_state, save_metadata, _on_skip_collect_times_change
from helpers import time_text_widget
from i18n import t


def render_tab_metadata() -> None:
    sensor_list = st.session_state.get("sensor_list", [])
    init_metadata_widget_state()

    with st.expander(t("meta_guide_title"), expanded=True):
        st.image(".streamlit/images/process carac.png", width="stretch")
        st.markdown(t("meta_guide_body"))

    # ── Workflow ──────────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(t("meta_workflow_container_title"))

        col_wf, col_wfo = st.columns(2)

        with col_wf:
            wf_options = [t("meta_wf_standard"), t("meta_wf_multi")]
            wf_captions = [t("meta_wf_standard_caption"), t("meta_wf_multi_caption")]
            current_wf_idx = st.session_state.get("saved_workflow", 0)

            workflow = st.segmented_control(
                t("meta_workflow_label"),
                options=wf_options,
                default=wf_options[current_wf_idx],
                key="workflow_type_seg",
                selection_mode="single"
            )

            if workflow is None:
                workflow = wf_options[current_wf_idx]

            captions_map = dict(zip(wf_options, wf_captions))
            st.caption(captions_map[workflow])

        new_wf = wf_options.index(workflow)
        if new_wf != st.session_state.get("saved_workflow"):
            st.session_state["saved_workflow"] = new_wf
            save_metadata()

        with col_wfo:
            wfo_options = [t("meta_wfo_order_a"), t("meta_wfo_order_b")]
            wfo_captions = [t("meta_order_a_caption"), t("meta_order_b_caption")]
            current_wfo_idx = st.session_state.get("saved_workflow_order", 0)

            workflow_order = st.segmented_control(
                t("meta_order_label"),
                options=wfo_options,
                default=wfo_options[current_wfo_idx],
                key="workflow_order_seg",
                selection_mode="single",
            )

            if workflow_order is None:
                workflow_order = wfo_options[current_wfo_idx]

            captions_map = dict(zip(wfo_options, wfo_captions))
            st.caption(captions_map[workflow_order])

        new_wfo = wfo_options.index(workflow_order)
        if new_wfo != st.session_state.get("saved_workflow_order"):
            st.session_state["saved_workflow_order"] = new_wfo
            save_metadata()

        # ── General info ──────────────────────────────────────────────────────
        st.write("")
        with st.container(border=True):
            st.markdown(t("meta_info_title"))
            c1, c2 = st.columns(2)
            with c1:
                st.text_input(t("meta_operator_name"), placeholder=t("meta_operator_ph"),
                              key="_operator_name", on_change=save_metadata)
                st.selectbox(t("meta_sensor"), sensor_list,
                             key="_sensor_name", index=0, on_change=save_metadata)
            with c2:
                st.date_input(t("meta_date"), key="_test_date", on_change=save_metadata)
                _is_standard = st.session_state.get("saved_workflow", 0) == 0
                st.number_input(
                    t("meta_nb_samples"),
                    step=1, min_value=1,
                    max_value=1 if _is_standard else 100,
                    format="%d",
                    key="_nb_sample",
                    disabled=_is_standard,
                    on_change=save_metadata,
                )

    # ── Collection times ──────────────────────────────────────────────────────
    st.write("")
    with st.container(border=True):
        st.markdown(t("meta_times_title"))
        _skip_times = st.toggle(
            t("meta_skip_toggle"),
            key="skip_collect_times",
            on_change=_on_skip_collect_times_change,
        )

        if not _skip_times:
            if st.session_state.get("metadata_error"):
                st.error(st.session_state["metadata_error"])

            for i in range(1, int(st.session_state["_nb_sample"]) + 1):
                with st.expander(t("meta_sample_label", n=i), expanded=True):
                    col_start, col_end = st.columns(2)
                    with col_start:
                        time_text_widget(t("meta_start_time"), f"_start_{i}", save_metadata)
                    with col_end:
                        time_text_widget(t("meta_end_time"), f"_end_{i}", save_metadata)

            st.write("")
            if st.button(t("btn_save"), type="primary", use_container_width=True, key="savebutton"):
                save_metadata()
                if not st.session_state.get("metadata_error"):
                    st.toast(t("meta_saved_toast"), icon="✅")
        else:
            st.caption(t("meta_skip_caption"))

    # ── Times recap ───────────────────────────────────────────────────────────
    st.write("")
    with st.container(border=True):
        st.markdown(t("meta_recap_title"))
        df_times = st.session_state["df_collect_times"]
        if df_times.empty:
            st.caption(t("meta_recap_empty"))
        else:
            th = st.columns([1.5, 2.5, 3, 3])
            headers = [t("meta_recap_sample"), t("meta_recap_date"), t("meta_recap_start"), t("meta_recap_end")]
            for col, label in zip(th, headers):
                col.markdown(f"<small>**{label}**</small>", unsafe_allow_html=True)
            st.divider()
            for _, row in df_times.iterrows():
                tr = st.columns([1.5, 2.5, 3, 3], vertical_alignment="center")
                tr[0].markdown(f"**` {row['Echantillon']} `**")
                dv = row["Date"]
                tr[1].write(dv.strftime('%d/%m/%Y') if hasattr(dv, 'strftime') else str(dv))
                tr[2].write(f"🟢 {row['Heure de début']}")
                tr[3].write(f"🔴 {row['Heure de fin']}")

    st.write("")
    _, col_next = st.columns(2)
    with col_next:
        if st.button(t("btn_next_containers"), use_container_width=True, type="primary"):
            save_metadata()
            st.session_state.step_index = 1
            st.rerun()
