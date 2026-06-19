import datetime as dt

import matplotlib.pyplot as plt
import streamlit as st

from config import DEV_MODE
from data import summarize_by_material, get_missing_classes
from dialogs import dialog_nouvelle_saisie
from export import build_zip_export, upload_to_dropbox
from i18n import t


def render_tab_summary() -> None:
    facility = st.session_state.get("facility_name", "")

    with st.expander(t("summ_guide_title"), expanded=True):
        st.markdown(t("summ_guide_body"))
        st.success(t("summ_guide_tip"))

    if st.session_state["df_weighings"].empty:
        st.info(t("summ_no_data"))
        if st.button(t("btn_back"), use_container_width=True):
            st.session_state.step_index = 2
            st.rerun()
        return

    # Prepare export once
    timestamp   = dt.datetime.now(dt.timezone(dt.timedelta(hours=2))).strftime("%Y%m%d_%H%M")
    sensor_name = st.session_state["saved_sensor_name"].replace(" ", "_")
    base_name   = f"Resultat_{facility}_{sensor_name}_{timestamp}"
    zip_data    = build_zip_export()

    # Global summary
    df_summary = summarize_by_material(st.session_state["df_weighings"])
    total_net  = df_summary["Poids net"].sum() if not df_summary.empty else 0.0
    st.subheader(t("summ_dashboard_title"))
    st.metric(t("summ_total_metric"), f"{total_net:.2f} kg")
    st.dataframe(df_summary, hide_index=True, use_container_width=True)

    # Pie chart
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
            st.dataframe(summarize_by_material(df_s), hide_index=True, use_container_width=True)

    # Completeness check
    missing = get_missing_classes()
    if missing:
        st.warning(
            t("summ_missing_warning", n=len(missing)) + "  \n"
            + "\n".join(f"- `{c}`" for c in missing)
        )

    # Export & reset
    with st.container(border=True):
        st.subheader(t("summ_export_title"))
        col_export, col_reset = st.columns([1.5, 1])

        with col_export:
            if st.download_button(
                t("btn_download"),
                data=zip_data,
                file_name=f"{base_name}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
                key="download_summary",
            ) and not DEV_MODE:
                with st.spinner(t("dropbox_uploading")):
                    try:
                        if upload_to_dropbox(zip_data, f"{base_name}.zip"):
                            st.toast(t("dropbox_success"), icon="☁️")
                    except Exception:
                        pass

        with col_reset:
            if st.button(t("btn_new_entry"), use_container_width=True, type="primary", key="new_entry"):
                dialog_nouvelle_saisie()

        if DEV_MODE:
            st.info(t("dev_mode_warning"))
