import streamlit as st

from helpers import get_container_weight
from session import save_session, clear_session
from weights import net_weight as calculate_net_weight, nonnegative_weight
from i18n import t


@st.dialog("Nouvelle saisie")
def dialog_nouvelle_saisie() -> None:
    st.warning(
        "Cette action effacera toutes les données de la session en cours. "
        "Cette opération est irréversible."
    )
    col1, col2 = st.columns(2)
    if col1.button("Confirmer", type="primary", width="stretch"):
        clear_session()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()
    if col2.button("Annuler", width="stretch"):
        st.rerun()


@st.dialog("✏️ Modifier la pesée")
def dialog_modifier_pesee(row_idx: int) -> None:
    df  = st.session_state["df_weighings"]
    row = df.iloc[row_idx]
    material_classes = st.session_state.get("material_classes", [])

    st.markdown(f"Vous modifiez la pesée **n° {row_idx + 1}**.")

    current_samples_str = str(row.get("N° échantillon", "1"))
    try:
        current_samples = [int(x.strip()) for x in current_samples_str.split(",") if x.strip().isdigit()]
    except Exception:
        current_samples = [1]

    new_samples = st.multiselect(
        "Numéro(s) d'échantillon",
        options=list(range(1, st.session_state["saved_nb_sample"] + 1)),
        default=current_samples,
    )

    current_material = row["Classe de matériau"]
    try:
        mat_index = material_classes.index(current_material)
    except ValueError:
        mat_index = 0

    new_material = st.selectbox("Classe de matériau", material_classes, index=mat_index)

    current_container = row["Contenant utilisé"] if row["Contenant utilisé"] else "Pas de contenant"
    container_options = ["Pas de contenant"] + st.session_state["df_containers"]["Contenant"].tolist()
    try:
        cont_index = container_options.index(current_container)
    except ValueError:
        cont_index = 0

    new_container = st.selectbox("Contenant utilisé", container_options, index=cont_index)
    try:
        current_gross = nonnegative_weight(row["Poids brut"])
    except ValueError:
        current_gross = 0.0
    new_gross = st.number_input("Poids brut (kg)", min_value=0.0,
                                value=current_gross, step=0.1, format="%.3f")

    st.divider()
    col_save, col_cancel = st.columns(2)

    with col_save:
        if st.button("💾 Enregistrer", type="primary", width="stretch"):
            if not new_samples:
                st.error("⚠️ Veuillez choisir au moins un échantillon.")
                return

            try:
                valid_gross = nonnegative_weight(new_gross)
            except ValueError:
                st.error(t("dialog_edit_invalid_weight"))
                return
            try:
                tare_weight = nonnegative_weight(
                    get_container_weight(new_container) if new_container != "Pas de contenant" else 0.0
                )
            except ValueError:
                st.error(t("dialog_edit_invalid_tare"))
                return
            try:
                new_net = calculate_net_weight(valid_gross, tare_weight)
            except ValueError:
                st.error(t("dialog_edit_negative", net=valid_gross - tare_weight))
                return

            new_sample_label = ", ".join(map(str, sorted(new_samples)))
            st.session_state["df_weighings"].at[row_idx, "N° échantillon"]    = new_sample_label
            st.session_state["df_weighings"].at[row_idx, "Classe de matériau"] = new_material
            st.session_state["df_weighings"].at[row_idx, "Contenant utilisé"] = (
                "" if new_container == "Pas de contenant" else new_container
            )
            st.session_state["df_weighings"].at[row_idx, "Poids brut"] = valid_gross
            st.session_state["df_weighings"].at[row_idx, "Tare"] = tare_weight
            st.session_state["df_weighings"].at[row_idx, "Poids net"]  = new_net
            st.toast("Pesée mise à jour !", icon="✅")
            save_session()
            st.rerun()

    with col_cancel:
        if st.button("❌ Annuler", width="stretch"):
            st.rerun()
