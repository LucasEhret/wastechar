import matplotlib.pyplot as plt
import streamlit as st

from data import summarize_by_material, get_missing_classes
from dialogs import dialog_nouvelle_saisie
from i18n import t
from ui.export_controls import render_export_controls
from weights import invalid_weighing_rows


def _on_dropbox_upload_change() -> None:
    st.session_state["dropbox_upload_enabled"] = st.session_state["_dropbox_upload_widget"]


def _render_review_actions(has_data: bool) -> None:
    with st.container(border=True):
        st.subheader(t("summ_export_title"))

        if has_data:
            if st.session_state.get("is_admin", False):
                if "_dropbox_upload_widget" not in st.session_state:
                    st.session_state["_dropbox_upload_widget"] = st.session_state.get(
                        "dropbox_upload_enabled", True
                    )
                st.checkbox(
                    t("summ_dropbox_upload"),
                    key="_dropbox_upload_widget",
                    on_change=_on_dropbox_upload_change,
                )
            if (
                not st.session_state.get("is_admin", False)
                or st.session_state.get("dropbox_upload_enabled", True)
            ):
                st.caption(t("summ_upload_on_download"))
            else:
                st.caption(t("summ_download_only"))

            col_export, col_reset = st.columns(2)
            with col_export:
                render_export_controls()
            with col_reset:
                if st.button(t("btn_new_entry"), width="stretch", type="secondary", key="new_entry"):
                    dialog_nouvelle_saisie()
        elif st.button(t("btn_new_entry"), width="stretch", type="secondary", key="new_entry"):
            dialog_nouvelle_saisie()


def render_tab_summary() -> None:
    if st.session_state.get("show_tutorials", True):
        with st.expander(t("summ_guide_title"), expanded=True):
            st.markdown(t("summ_guide_body"))
            st.success(t("summ_guide_tip"))

    if st.session_state["df_weighings"].empty:
        st.info(t("summ_no_data"))
        _render_review_actions(has_data=False)
        if st.button(t("btn_back"), width="stretch"):
            st.session_state.step_index = 2
            st.rerun()
        return

    invalid_rows = invalid_weighing_rows(st.session_state["df_weighings"])
    if invalid_rows:
        st.error(t("summ_invalid_weights", n=len(invalid_rows)))
        if st.button(t("btn_back"), width="stretch"):
            st.session_state.step_index = 2
            st.rerun()
        return

    # Global summary
    df_summary = summarize_by_material(st.session_state["df_weighings"])
    total_net  = df_summary["Poids net"].sum() if not df_summary.empty else 0.0
    st.subheader(t("summ_dashboard_title"))
    st.metric(t("summ_total_metric"), f"{total_net:.2f} kg")
    st.dataframe(df_summary, hide_index=True, width="stretch")

    # Pie charts need a positive total; zero is still a valid recorded result.
    if total_net > 0:
        with st.container(border=True):
            plt.rcParams['axes.prop_cycle'] = plt.cycler(  # type: ignore
                color=['#00D494', '#0A3D2E', '#7A9E89', '#AC6F4E', '#DAB996', '#2B2420', "#D4E5DE", "#FFFFFF"]
            )
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(
                df_summary["Pourcentage de la masse totale"],
                labels=df_summary["Classe de matériau"],  # type: ignore
                autopct="%1.1f%%",
            )
            ax.set_title(t("summ_chart_title"))
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info(t("summ_zero_distribution"))

    # Per-sample detail
    st.markdown(t("summ_sample_detail"))
    sample_ids = sorted(
        st.session_state["df_weighings"]["N° échantillon"].dropna().unique()
    )
    for sample_id in sample_ids:
        with st.expander(t("summ_sample_label", id=sample_id)):
            df_s = st.session_state["df_weighings"][
                st.session_state["df_weighings"]["N° échantillon"] == sample_id
            ]
            st.dataframe(summarize_by_material(df_s), hide_index=True, width="stretch")

    # Completeness check
    missing = get_missing_classes()
    if missing:
        st.warning(
            t("summ_missing_warning", n=len(missing)) + "  \n"
            + "\n".join(f"- `{c}`" for c in missing)
        )

    _render_review_actions(has_data=True)
