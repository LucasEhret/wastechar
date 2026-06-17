import streamlit as st
# from streamlit_extras.card_selector import card_selector

from data import init_metadata_widget_state, save_metadata, _on_skip_collect_times_change
from helpers import time_text_widget


def render_tab_metadata() -> None:
    sensor_list = st.session_state.get("sensor_list", [])
    init_metadata_widget_state()

    with st.expander("⁉️ Guide — Métadonnées", expanded=True):
        st.image(".streamlit/images/process carac.png", width="stretch")
        st.markdown("""
        Renseignez les informations du test **avant de commencer à peser**. Les modifications
        sont sauvegardées automatiquement ; le bouton **💾 Sauvegarder** force une sauvegarde manuelle.

        ---

        #### 1. Type de workflow

        | Option | Description |
        |---|---|
        | **Ordre A** | Le capteur mesure **avant** la collecte (Capteur ➡️ Collecte ➡️ Pesée) |
        | **Ordre B** | Le capteur mesure **après** la pesée (Collecte ➡️ Pesée ➡️ Capteur) |
        | **Standard** | 1 seul échantillon |
        | **Multi-échantillon** | Plusieurs prélèvements distincts (pour une seule caractérisation) |

        #### 2. Informations générales
        Renseignez votre nom, la date, le capteur et le nombre d'échantillons.

        #### 3. Heures de passage
        Pour chaque échantillon, indiquez l'heure de début et de fin de passage sous le capteur.
        Formats acceptés : `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
        """)

    # ── Workflow ──────────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("### ⚙️ Type de workflow")

        col_wf, col_wfo = st.columns(2)

        with col_wf:
            wf_options = ["Standard", "Multi-échantillon"]
            current_wf_idx = st.session_state.get("saved_workflow", 0)
            
            # 🌟 Replaced st.radio with st.segmented_control
            workflow = st.segmented_control(
                "Type de workflow",
                options=wf_options,
                default=wf_options[current_wf_idx], # Uses the value instead of the index
                key="workflow_type_seg",
                selection_mode="single"
            )
            
            # Safeguard: st.segmented_control allows deselecting a pill by clicking it again.
            # This prevents an error and forces it to fall back to the last saved choice.
            if workflow is None:
                workflow = wf_options[current_wf_idx]

        new_wf = wf_options.index(workflow)
        if new_wf != st.session_state.get("saved_workflow"):
            st.session_state["saved_workflow"] = new_wf
            save_metadata()

        with col_wfo:
            wfo_options = ["Ordre A", "Ordre B"]
            current_wfo_idx = st.session_state.get("saved_workflow_order", 0)
            
            # 🌟 Replaced st.radio with st.segmented_control
            workflow_order = st.segmented_control(
                "Ordre de passage",
                options=wfo_options,
                default=wfo_options[current_wfo_idx],
                key="workflow_order_seg",
                selection_mode="single",
            )
            
            if workflow_order is None:
                workflow_order = wfo_options[current_wfo_idx]
                
            # Note: st.segmented_control doesn't support the 'captions' parameter natively.
            # We display a clean dynamic caption underneath based on the active selection instead:
            captions_map = {
                "Ordre A": "Capteur ➡️ Collecte ➡️ Pesée",
                "Ordre B": "Collecte ➡️ Pesée ➡️ Capteur"
            }
            st.caption(captions_map[workflow_order])

        new_wfo = wfo_options.index(workflow_order)
        if new_wfo != st.session_state.get("saved_workflow_order"):
            st.session_state["saved_workflow_order"] = new_wfo
            save_metadata()

        # ── General info ──────────────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("### ℹ️ Informations générales")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Nom *", placeholder="Entrez votre nom",
                            key="_operator_name", on_change=save_metadata)
                st.selectbox("Nom du capteur", sensor_list,
                            key="_sensor_name", index=0, on_change=save_metadata)
            with c2:
                st.date_input("Date de prélèvement", key="_test_date", on_change=save_metadata)
                _is_standard = st.session_state.get("saved_workflow", 0) == 0
                st.number_input(
                    "Nombre d'échantillons",
                    step=1, min_value=1,
                    max_value=1 if _is_standard else 100,
                    format="%d",
                    key="_nb_sample",
                    disabled=_is_standard,
                    on_change=save_metadata,
                )

    # ── Collection times ──────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("### 🕒 Heures de passage sous le capteur WasteFlow")
        _skip_times = st.toggle(
            "Ne pas renseigner d'heures de collecte maintenant",
            key="skip_collect_times",
            on_change=_on_skip_collect_times_change,
        )

        if not _skip_times:
            if st.session_state.get("metadata_error"):
                st.error(st.session_state["metadata_error"])

            for i in range(1, int(st.session_state["_nb_sample"]) + 1):
                with st.expander(f"📦 Échantillon {i}", expanded=True):
                    col_start, col_end = st.columns(2)
                    with col_start:
                        time_text_widget("Heure de début *", f"_start_{i}", save_metadata)
                    with col_end:
                        time_text_widget("Heure de fin *", f"_end_{i}", save_metadata)

            st.write("")
            if st.button("💾 Sauvegarder", type="primary", use_container_width=True, key="savebutton"):
                save_metadata()
                if not st.session_state.get("metadata_error"):
                    st.toast("Métadonnées sauvegardées ✓", icon="✅")
        else:
            st.caption("Les heures de collecte ne seront pas renseignées.")

    # ── Times recap ───────────────────────────────────────────────────────────
    st.write("")
    with st.container(border=True):
        st.markdown("📋 **Récapitulatif des plages horaires**")
        df_times = st.session_state["df_collect_times"]
        if df_times.empty:
            st.caption("Aucune plage horaire enregistrée.")
        else:
            th = st.columns([1.5, 2.5, 3, 3])
            for col, label in zip(th, ["Échantillon", "Date", "Début", "Fin"]):
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
        if st.button("Étape suivante : Configurer les Contenants ➡️",
                     use_container_width=True, type="primary"):
            save_metadata()
            st.session_state.step_index = 1
            st.rerun()
