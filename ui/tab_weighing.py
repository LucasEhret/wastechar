import hashlib
import pandas as pd
import streamlit as st

from data import add_weighing, delete_weighing
from dialogs import dialog_modifier_pesee
from session import save_observation
from i18n import t
from table_entry import duplicate_table_classes, make_table_draft, preview_table, save_table
from report_validation import metadata_errors
from weights import nonnegative_weight
from weighing_identity import WEIGHING_ID_COLUMN


def _clear_weighing_error() -> None:
    st.session_state["weighing_error"] = ""


def _render_table_mode(disable_weighing: bool) -> None:
    material_classes = st.session_state.get("material_classes", [])
    is_single = st.session_state.get("saved_workflow", 0) == 0
    nb_sample = st.session_state["saved_nb_sample"]
    container_options = ["Pas de contenant"] + st.session_state["df_containers"]["Contenant"].tolist()

    with st.container(border=True):
        st.markdown(t("weigh_table_title"))
        st.caption(t("weigh_table_intro"))
        recorded = st.session_state["df_weighings"]
        if not recorded.empty and (
            "__table_class" not in recorded.columns
            or recorded["__table_class"].fillna("").eq("").any()
        ):
            st.caption(t("weigh_table_other_entries"))
        for material_class in duplicate_table_classes():
            st.warning(t("weigh_table_error_duplicate", material=material_class))

        if st.session_state["weighing_error"]:
            st.warning(st.session_state["weighing_error"])

        if not material_classes:
            st.info(t("weigh_table_no_classes"))
            return

        table_key = "weighing_table"
        draft = st.session_state.get(table_key)
        if draft is not None and WEIGHING_ID_COLUMN in draft.columns:
            recorded_ids = set(recorded.get(WEIGHING_ID_COLUMN, pd.Series(dtype=str)).dropna())
            draft_ids = set(draft[WEIGHING_ID_COLUMN].dropna())
            if not draft_ids.issubset(recorded_ids):
                draft = None
        if (draft is None or WEIGHING_ID_COLUMN not in draft.columns
                or draft["Classe de matériau"].tolist() != material_classes):
            draft = make_table_draft(material_classes, nb_sample, is_single)
            st.session_state[table_key] = draft
            st.session_state["weighing_table_editor_version"] = (
                st.session_state.get("weighing_table_editor_version", 0) + 1
            )

        visible_columns = ["Classe de matériau"]
        if not is_single:
            visible_columns.append("N° échantillon")
        if len(container_options) > 1:
            visible_columns.append("Contenant utilisé")
        visible_columns.append("Poids brut")

        filter_text = st.text_input(
            t("weigh_table_filter"),
            key="weighing_table_filter",
            placeholder=t("weigh_table_filter_placeholder"),
        ).strip()
        if filter_text:
            shown = draft.loc[
                draft["Classe de matériau"].str.casefold().str.contains(
                    filter_text.casefold(), regex=False
                )
            ]
            st.caption(t("weigh_table_shown", shown=len(shown), total=len(draft)))
        else:
            shown = draft

        edited = draft.copy()
        if shown.empty:
            st.info(t("weigh_table_no_match"))
        else:
            filter_key = hashlib.sha256(filter_text.casefold().encode("utf-8")).hexdigest()[:8]
            schema_key = hashlib.sha256(
                repr((visible_columns, container_options, nb_sample)).encode("utf-8")
            ).hexdigest()[:8]
            display = shown[visible_columns].copy()
            tares = dict(zip(
                st.session_state["df_containers"]["Contenant"],
                st.session_state["df_containers"]["Poids à vide"],
            ))

            def net_preview(row):
                gross = row["Poids brut"]
                container = row["Contenant utilisé"] if "Contenant utilisé" in row else "Pas de contenant"
                if pd.isna(gross) or pd.isna(container):
                    return None
                tare = 0.0 if container == "Pas de contenant" else tares.get(container)
                try:
                    return nonnegative_weight(gross) - nonnegative_weight(tare)
                except ValueError:
                    return None

            display["Poids net"] = display.apply(net_preview, axis=1)
            edited_visible = st.data_editor(
                display,
                key=(
                    f"editor_{table_key}_{st.session_state.get('weighing_table_editor_version', 0)}"
                    f"_{filter_key}_{schema_key}"
                ),
                on_change=_clear_weighing_error,
                hide_index=True,
                width="stretch",
                height=min(680, max(220, 35 * (len(shown) + 1))),
                num_rows="fixed",
                disabled=disable_weighing or ["Classe de matériau", "Poids net"],
                column_config={
                    "Classe de matériau": st.column_config.TextColumn(
                        t("weigh_class_label"), disabled=True,
                    ),
                    "Contenant utilisé": st.column_config.SelectboxColumn(
                        t("weigh_container_label"), options=container_options, required=True,
                    ),
                    "N° échantillon": st.column_config.SelectboxColumn(
                        t("weigh_sample_label"), options=list(range(1, nb_sample + 1)),
                    ),
                    "Poids brut": st.column_config.NumberColumn(
                        t("weigh_gross_label"), min_value=0.0, step=0.1, format="%.3f",
                    ),
                    "Poids net": st.column_config.NumberColumn(
                        t("weigh_table_net_label"), format="%.3f", disabled=True,
                    ),
                },
            )
            for index, (_, row) in zip(shown.index, edited_visible.iterrows()):
                for column in visible_columns:
                    edited.at[index, column] = row[column]
        if is_single:
            edited["N° échantillon"] = 1
        if len(container_options) == 1:
            edited["Contenant utilisé"] = "Pas de contenant"
        st.session_state[table_key] = edited

        try:
            preview = preview_table(edited)
            added = sum(change.weighing_id is None for change in preview.changes)
            st.caption(t(
                "weigh_table_preview",
                filled=preview.filled_count,
                added=added,
                corrected=len(preview.changes) - added,
                net=preview.net_total,
            ))
            can_save = bool(preview.changes)
        except ValueError as exc:
            st.warning(str(exc))
            can_save = False

        st.button(
            t("weigh_table_save_btn"),
            type="primary",
            width="stretch",
            disabled=disable_weighing or not can_save,
            on_click=save_table,
            args=(edited.copy(),),
        )


def _render_manual_mode(disable_weighing: bool) -> None:
    material_classes = st.session_state.get("material_classes", [])

    with st.form("weighing_form", border=True):
        st.markdown(t("weigh_form_title"))

        if st.session_state["weighing_error"]:
            st.warning(st.session_state["weighing_error"])

        _is_single = st.session_state.get("saved_workflow", 0) == 0
        v = st.session_state.get("weighing_version", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.multiselect(
                t("weigh_sample_label"),
                options=list(range(1, st.session_state["saved_nb_sample"] + 1)),
                default=[1] if _is_single else None,
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
                width="stretch",
                disabled=disable_weighing,
                type="primary",
            )
        if submitted:
            add_weighing()


def render_tab_weighing() -> None:
    if st.session_state.get("show_tutorials", True):
        with st.expander(t("weigh_guide_title"), expanded=False):
            st.markdown(t("weigh_guide_body"))

    # A partially saved collection table is still a draft.
    disable_weighing = bool(metadata_errors(st.session_state))
    if disable_weighing:
        st.warning(t("weigh_disable_warning"))

    # Mode switch — table (default) vs manual
    WEIGH_MODES = [t("weigh_mode_table"), t("weigh_mode_manual")]
    if "weighing_mode_index" not in st.session_state:
        st.session_state["weighing_mode_index"] = 0

    def _sync_weighing_mode():
        st.session_state["weighing_mode_index"] = WEIGH_MODES.index(
            st.session_state["weighing_mode_seg"]
        )

    st.session_state["weighing_mode_seg"] = WEIGH_MODES[st.session_state["weighing_mode_index"]]
    st.segmented_control(
        t("weigh_mode_label"),
        options=WEIGH_MODES,
        key="weighing_mode_seg",
        label_visibility="collapsed",
        on_change=_sync_weighing_mode,
    )

    if st.session_state["weighing_mode_index"] == 0:
        _render_table_mode(disable_weighing)
    else:
        _render_manual_mode(disable_weighing)

    # Keep the value outside the widget key, which Streamlit drops on other tabs.
    if "global_comment" not in st.session_state:
        st.session_state["global_comment"] = st.session_state.get("_global_comment_value", "")

    # Observations
    st.write("")
    with st.container(border=True):
        st.markdown(t("weigh_obs_title"))
        st.text_area(
            t("weigh_obs_title"),
            placeholder=t("weigh_obs_ph"),
            key="global_comment",
            on_change=save_observation,
            label_visibility="collapsed",
            height=80,
        )

    # Weighings history
    st.write("")
    df_w = st.session_state["df_weighings"]
    with st.expander(t("weigh_history_title", n=len(df_w)), expanded=False):
        if df_w.empty:
            st.info(t("weigh_history_empty"))
        else:
            for idx, row in df_w.iterrows():
                with st.container(border=True):
                    c_info, c_edit, c_del = st.columns([8, 1, 1], vertical_alignment="center")
                    with c_info:
                        st.markdown(f"**🔹 {row['Classe de matériau']}**")
                        if isinstance(row.get("__table_class"), str) and row["__table_class"]:
                            st.caption(t("weigh_table_recorded_badge"))
                        contenant_disp = row["Contenant utilisé"] if row["Contenant utilisé"] else t("weigh_no_container")
                        st.markdown(
                            f"<small>📦 {t('weigh_hist_samples')} : **` {row['N° échantillon']} `** &nbsp;|&nbsp; "
                            f"{t('weigh_hist_tare')} : *{contenant_disp} ({row.get('Tare', row['Poids brut'] - row['Poids net']):.3f} kg)* &nbsp;|&nbsp; "
                            f"{t('weigh_hist_gross')} : `{row['Poids brut']:.3f} kg` ➡️ "
                            f"**{t('weigh_hist_net')} : <span style='color:#146c43'>{row['Poids net']:.3f} kg</span>**</small>",
                            unsafe_allow_html=True,
                        )
                    with c_edit:
                        if isinstance(row.get("__table_class"), str) and row["__table_class"]:
                            st.caption(t("weigh_table_edit_here"))
                        elif st.button(t("btn_edit"), key=f"edit_w_{idx}", type="secondary",
                                       help=t("weigh_edit_help"), width="stretch"):
                            dialog_modifier_pesee(idx)
                    with c_del:
                        st.button(t("btn_delete"), key=f"del_w_{idx}", type="secondary",
                                  help=t("weigh_delete_help"), width="stretch",
                                  on_click=delete_weighing, args=(idx,))

    st.write("")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button(t("btn_back"), width="stretch"):
            st.session_state.step_index = 1
            st.rerun()
    with col_next:
        if st.button(t("btn_next_summary"), width="stretch", type="primary"):
            st.session_state.step_index = 3
            st.rerun()
