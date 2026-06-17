import streamlit as st

from data import add_weighing, delete_weighing
from dialogs import dialog_modifier_pesee
from session import save_session


def render_tab_weighing() -> None:
    material_classes = st.session_state.get("material_classes", [])

    with st.expander("⁉️ Guide — Résultats de pesée", expanded=True):
        st.markdown("""
        Saisissez les pesées **une classe de matériau à la fois**.

        **Pour chaque pesée :**
        1. **Numéro(s) d'échantillon** — Standard = figé à 1. Multi = libre.
        2. **Classe de matériau** — Choisissez dans la liste ou saisissez une nouvelle valeur.
        3. **Contenant utilisé** — Ou *Pas de contenant* pour une pesée directe.
        4. **Poids brut (kg)** — Plusieurs poids séparés par des espaces (ex : `12.5 8.3`).
        5. Cliquez sur ✅ **Ajouter la pesée**.

        ---

        #### Corriger une erreur
        Cliquez sur **✕** pour supprimer une ligne ou **✏️** pour la modifier.

        > Si le bouton **Ajouter la pesée** est grisé, vérifiez que les heures de
        prélèvement sont renseignées dans **Métadonnées** (ou activez le mode sans heures).
        """)

    # Disable weighing if no collect times
    disable_weighing = (
        st.session_state["df_collect_times"].empty
        and not st.session_state.get("skip_collect_times")
    )
    if disable_weighing:
        st.warning("⚠️ Renseignez d'abord les heures de prélèvement dans l'onglet **Métadonnées**.")

    # Entry form
    with st.form("weighing_form", border=True):
        st.markdown("### 📥 Entrée de pesée")

        if st.session_state["weighing_error"]:
            st.warning(st.session_state["weighing_error"])

        _is_standard = st.session_state.get("saved_workflow", 0) == 0
        v = st.session_state.get("weighing_version", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.multiselect(
                "Numéro(s) d'échantillon",
                options=list(range(1, st.session_state["saved_nb_sample"] + 1)),
                default=[1] if _is_standard else None,
                key="sample_nb",
                placeholder="Choisir l'échantillon...",
                disabled=disable_weighing,
            )
        with col2:
            st.selectbox(
                "Classe de matériau",
                material_classes,
                key=f"material_class_{v}",
                index=None,
                placeholder="Choisir...",
                disabled=disable_weighing,
                accept_new_options=True,
            )
        with col3:
            st.selectbox(
                "Contenant utilisé",
                ["Pas de contenant"] + st.session_state["df_containers"]["Contenant"].tolist(),
                disabled=disable_weighing,
                key="container_used",
            )

        img_file = st.file_uploader(
            "Photo du matériau (optionnel)",
            type=["jpg", "jpeg", "png"],
            key=f"weighing_image_{st.session_state['image_uploader_key']}",
        )
        if img_file:
            st.image(img_file, width=200)

        st.divider()

        col4, col5 = st.columns([3, 1], vertical_alignment="bottom")
        with col4:
            st.markdown(
                """
                <div style="margin-bottom: -15px; display: flex; align-items: center;">
                    <span style="font-size: 1.15rem; font-weight: 700; color: #1E293B;">
                        POIDS BRUT (kg)
                    </span>
                    <span style="color: #DC2626; font-weight: bold; margin-left: 2px;">*</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_input(
                "Poids brut (kg)",
                key=f"gross_weight_{v}",
                placeholder="Ex: 12.5 14.2 — séparés par un espace",
                disabled=disable_weighing,
                label_visibility="hidden",
            )
        with col5:
            submitted = st.form_submit_button(
                "✅ Ajouter la pesée",
                use_container_width=True,
                disabled=disable_weighing,
                type="primary",
            )
        if submitted:
            add_weighing()

    # Observations
    st.write("")
    with st.container(border=True):
        st.markdown("### Observations")
        st.text_area(
            "Commentaire général (optionnel)",
            placeholder="Ajoutez ici toute remarque sur la session.",
            key="global_comment",
            on_change=save_session,
            label_visibility="collapsed",
            height=80,
        )

    # Weighings history
    st.write("")
    df_w = st.session_state["df_weighings"]
    with st.expander(f"📋 Historique des pesées ({len(df_w)})", expanded=True):
        if df_w.empty:
            st.info("Aucune pesée enregistrée.")
        else:
            for idx, row in df_w.iterrows():
                with st.container(border=True):
                    c_info, c_edit, c_del = st.columns([8, 1, 1], vertical_alignment="center")
                    with c_info:
                        st.markdown(f"**🔹 {row['Classe de matériau']}**")
                        contenant_disp = row["Contenant utilisé"] if row["Contenant utilisé"] else "Pas de contenant"
                        st.markdown(
                            f"<small>📦 Échantillon(s) : **` {row['N° échantillon']} `** &nbsp;|&nbsp; "
                            f"Tarage : *{contenant_disp}* &nbsp;|&nbsp; "
                            f"Brut : `{row['Poids brut']:.3f} kg` ➡️ "
                            f"**Net : <span style='color:#146c43'>{row['Poids net']:.3f} kg</span>**</small>",
                            unsafe_allow_html=True,
                        )
                    with c_edit:
                        if st.button("✏️", key=f"edit_w_{idx}", type="secondary",
                                     help="Modifier", use_container_width=True):
                            dialog_modifier_pesee(idx)
                    with c_del:
                        st.button("✕", key=f"del_w_{idx}", type="secondary",
                                  help="Supprimer", use_container_width=True,
                                  on_click=delete_weighing, args=(idx,))

    st.write("")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.step_index = 1
            st.rerun()
    with col_next:
        if st.button("Étape suivante : Consulter le Résumé ➡️",
                     use_container_width=True, type="primary"):
            st.session_state.step_index = 3
            st.rerun()
