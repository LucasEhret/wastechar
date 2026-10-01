from ui.report_state import app_state
import streamlit as st

from data import init_metadata_widget_state, save_metadata, _on_skip_collect_times_change
from helpers import time_text_widget
from i18n import t
from report_validation import metadata_errors


def render_tab_metadata() -> None:
    sensor_list = app_state.get("sensor_list", [])
    init_metadata_widget_state()

    if app_state.get("show_tutorials", True):
        with st.expander(t("meta_guide_title"), expanded=True):
            st.image(".streamlit/images/process carac.png", width="stretch")
            st.markdown(t("meta_guide_body"))

    transient_error = app_state.get("metadata_error")
    draft_errors = [transient_error] if transient_error else metadata_errors(app_state)
    if draft_errors:
        st.warning(t("meta_draft_warning") + " " + "; ".join(draft_errors))

    # ── Sampling and sensor passage ───────────────────────────────────────────
    with st.container(border=True):
        st.markdown(t("meta_workflow_container_title"))

        col_wf, col_wfo = st.columns(2)

        with col_wf:
            wf_options = [0, 1]
            wf_labels = {0: t("meta_wf_standard"), 1: t("meta_wf_multi")}
            if app_state.get("workflow_type_seg") not in (*wf_options, None):
                app_state.pop("workflow_type_seg", None)
            wf_captions = [t("meta_wf_standard_caption"), t("meta_wf_multi_caption")]
            current_wf_idx = app_state.get("saved_workflow", 0)

            workflow = st.segmented_control(
                t("meta_workflow_label"),
                options=wf_options,
                format_func=wf_labels.__getitem__,
                default=wf_options[current_wf_idx],
                key="workflow_type_seg",
                selection_mode="single"
            )

            if workflow is None:
                workflow = wf_options[current_wf_idx]

            captions_map = dict(zip(wf_options, wf_captions))
            st.caption(captions_map[workflow])

        new_wf = workflow
        if new_wf != app_state.get("saved_workflow"):
            app_state["saved_workflow"] = new_wf
            save_metadata()

        with col_wfo:
            wfo_options = [0, 1]
            wfo_labels = {0: t("meta_wfo_order_a"), 1: t("meta_wfo_order_b")}
            if app_state.get("workflow_order_seg") not in (*wfo_options, None):
                app_state.pop("workflow_order_seg", None)
            wfo_captions = [t("meta_order_a_caption"), t("meta_order_b_caption")]
            current_wfo_idx = app_state.get("saved_workflow_order", 0)

            workflow_order = st.segmented_control(
                t("meta_order_label"),
                options=wfo_options,
                format_func=wfo_labels.__getitem__,
                default=wfo_options[current_wfo_idx],
                key="workflow_order_seg",
                selection_mode="single",
            )

            if workflow_order is None:
                workflow_order = wfo_options[current_wfo_idx]

            captions_map = dict(zip(wfo_options, wfo_captions))
            st.caption(captions_map[workflow_order])

        new_wfo = workflow_order
        if new_wfo != app_state.get("saved_workflow_order"):
            app_state["saved_workflow_order"] = new_wfo
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
                _is_single = app_state.get("saved_workflow", 0) == 0
                st.number_input(
                    t("meta_nb_samples"),
                    step=1, min_value=1,
                    max_value=1 if _is_single else 100,
                    format="%d",
                    key="_nb_sample",
                    disabled=_is_single,
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
            if app_state.get("metadata_error"):
                st.error(app_state["metadata_error"])

            for i in range(1, int(app_state["_nb_sample"]) + 1):
                with st.expander(t("meta_sample_label", n=i), expanded=True):
                    col_start, col_end = st.columns(2)
                    with col_start:
                        time_text_widget(t("meta_start_time"), f"_start_{i}", save_metadata)
                    with col_end:
                        time_text_widget(t("meta_end_time"), f"_end_{i}", save_metadata)

            st.write("")
            if st.button(t("btn_save"), type="primary", width="stretch", key="savebutton"):
                if save_metadata().saved:
                    st.toast(t("meta_saved_toast"), icon="✅")
                st.rerun()
        else:
            st.caption(t("meta_skip_caption"))

    # ── Times recap ───────────────────────────────────────────────────────────
    st.write("")
    with st.container(border=True):
        st.markdown(t("meta_recap_title"))
        df_times = app_state["df_collect_times"]
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
        if st.button(t("btn_next_containers"), width="stretch", type="primary"):
            if save_metadata().can_progress:
                app_state.step_index = 1
            st.rerun()
