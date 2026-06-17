import datetime as dt
import streamlit as st

from config import APP_VERSION, DEV_MODE, WORKFLOW_MAP, ORDER_MAP
from export import build_zip_export, upload_to_dropbox
from dialogs import dialog_nouvelle_saisie


def render_sidebar(authenticator) -> None:
    facility   = st.session_state.get("facility_name", "")
    is_admin   = st.session_state.get("is_admin", False)
    all_facils = st.session_state.get("all_facilities", [])

    with st.sidebar:
        st.image(".streamlit/images/logo-wasteflow-trademark.png", width=180)
        st.markdown(f"## {facility}")
        st.caption(f"👤 Connecté en tant que **{st.session_state['name']}**")
        authenticator.logout("🚪 Se déconnecter", location="sidebar")
        st.divider()

        if is_admin:
            with st.container(border=True):
                st.caption("**Voir en tant que :**")
                st.selectbox(
                    "Visualiser comme :",
                    options=all_facils,
                    key="_preview_facility",
                    label_visibility="collapsed",
                )
            st.divider()

        st.caption(f"Version : {APP_VERSION}")
        st.write("")

        if st.button(
            "🔄 Nouvelle session",
            use_container_width=True,
            type="secondary",
            help="Réinitialiser pour un nouveau test",
        ):
            dialog_nouvelle_saisie()

        st.divider()

        # Session info
        _wf_label  = WORKFLOW_MAP.get(st.session_state.get("saved_workflow"), "—")   # type: ignore
        _wfo_label = ORDER_MAP.get(st.session_state.get("saved_workflow_order"), "—")  # type: ignore
        with st.container(border=True):
            st.markdown("### 📌 Configuration active")
            st.markdown(
                f"""
                <div style="font-size: 0.9rem; line-height: 1.6;">
                    👤 <b>Opérateur :</b> {st.session_state.get('saved_operator_name') or '—'}<br>
                    📅 <b>Date :</b> {st.session_state.get('saved_test_date') or '—'}<br>
                    📡 <b>Capteur :</b> {st.session_state.get('saved_sensor_name') or '—'}<br>
                    ⚙️ <b>Workflow :</b> {_wf_label} (<b>{_wfo_label}</b>)
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown(f"⚖️ Pesées enregistrées : **` {len(st.session_state['df_weighings'])} `**")

        st.write("")

        # Export
        has_data = not st.session_state["df_weighings"].empty
        if has_data:
            st.markdown("### 💾 Sauvegarde")
            timestamp   = dt.datetime.now().strftime("%Y%m%d_%H%M")
            sensor_name = st.session_state["saved_sensor_name"].replace(" ", "_")
            base_name   = f"Resultat_{facility}_{sensor_name}_{timestamp}"
            zip_data    = build_zip_export()

            if st.download_button(
                "⬇️ Télécharger (Excel + PDF + photos)",
                data=zip_data,
                file_name=f"{base_name}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
            ) and not DEV_MODE:
                with st.spinner("Envoi sur Dropbox..."):
                    try:
                        if upload_to_dropbox(zip_data, f"{base_name}.zip"):
                            st.toast("Sauvegardé sur Dropbox !", icon="☁️")
                    except Exception:
                        pass

            if DEV_MODE:
                st.caption("🛠️ *DEV MODE — Dropbox désactivé.*")
        else:
            st.info("📦 L'export s'activera ici dès qu'une pesée sera enregistrée.")

        st.divider()

        with st.expander("📖 Guide d'utilisation rapide"):
            st.info("💡 Suivez les 4 étapes dans l'ordre via la barre de navigation en haut.")
            st.markdown("""
            **1️⃣ Métadonnées** — Workflow, informations, heures de passage sous le capteur.

            **2️⃣ Contenants** — Tares des bacs ou cartons. Passez si pesée directe.

            **3️⃣ Résultats de pesée** — Saisissez les poids bruts classe par classe.

            **4️⃣ Résumé** — Tableau de bord et export.
            """)

        st.link_button("🌐 wasteflow.ai", "https://wasteflow.ai", use_container_width=True)
        st.link_button(
            "⏱️ Mesures de temps",
            "https://deltatgit-e8vsfavsgwkxhq9jw4rzoq.streamlit.app/",
            use_container_width=True,
        )
        st.link_button("✉️ Contact", "mailto:lucas.ehret@wasteflow.ai", use_container_width=True)
