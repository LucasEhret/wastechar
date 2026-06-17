import streamlit as st

from data import add_container, remove_container


def render_tab_containers() -> None:
    with st.expander("⁉️ Guide — Contenants", expanded=True):
        st.markdown("""
        Les contenants sont les bacs ou cartons utilisés pour peser les matériaux.
        Leur poids à vide (tare) est automatiquement soustrait pour calculer le **poids net**.

        **Comment ajouter un contenant :**
        1. Saisissez un nom clair (ex : `Carton A`, `Bac Bleu 1`)
        2. Pesez le contenant vide et entrez son poids en kg
        3. Cliquez sur **✅ Ajouter le contenant**

        > Si vous ne pesez pas dans un contenant, **laissez cet onglet vide** — le poids brut sera égal au poids net.
        """)

    col_left, col_right = st.columns(2, gap="small")

    with col_left:
        with st.container(border=True):
            st.markdown("### 📥 Ajout de contenant")
            if st.session_state["container_error"]:
                st.warning(st.session_state["container_error"])

            st.text_input(
                "Identificateur du contenant",
                placeholder="Ex: Carton A, Bac Bleu 1...",
                key="container_name",
            )
            st.number_input(
                "Poids à vide (kg)",
                min_value=0.0, step=0.1, format="%.3f",
                key="container_weight",
            )
            st.write("")
            st.button(
                "✅ Ajouter le contenant",
                use_container_width=True,
                on_click=add_container,
                key="add_container_button",
                type="primary",
            )

    with col_right:
        with st.container(border=True):
            st.markdown("### 📋 Contenants enregistrés")
            if st.session_state["df_containers"].empty:
                st.info("Aucun contenant enregistré. Tare = 0.000 kg par défaut.")
            else:
                for _, row in st.session_state["df_containers"].iterrows():
                    with st.container(border=True):
                        c_info, c_action = st.columns([4, 1], vertical_alignment="center")
                        with c_info:
                            st.markdown(f"**📦 {row['Contenant']}**")
                            st.caption(f"Tare : `{row['Poids à vide']:.3f} kg`")
                        with c_action:
                            if st.button(
                                "✕", key=f"del_{row['Contenant']}",
                                type="secondary", help="Supprimer ce contenant",
                            ):
                                remove_container(row["Contenant"])

    st.write("")
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.step_index = 0
            st.rerun()
    with col_next:
        if st.button("Étape suivante : Saisir les Pesées ➡️",
                     use_container_width=True, type="primary"):
            st.session_state.step_index = 2
            st.rerun()
