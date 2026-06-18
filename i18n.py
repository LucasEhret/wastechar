"""
i18n.py — Translations for WasteChar (FR / EN)

Usage:
    from i18n import t, set_lang, LANGUAGES

    # Set language once (e.g. from a selectbox in the sidebar)
    set_lang("EN")

    # Use anywhere
    st.title(t("app_title"))
    st.button(t("btn_save"))
    st.metric(t("meta_total_weight"), f"{total:.2f} kg")

    # Placeholders
    st.warning(t("weighing_negative_net", net=-0.5, tare=1.2))

Adding a new key:
    Add it under the same key in both FR and EN blocks below.
    The linter at the bottom of this file will warn if a key is missing in any language.
"""

import streamlit as st

LANGUAGES = ["FR", "EN"]
DEFAULT_LANG = "FR"

_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── FR ────────────────────────────────────────────────────────────────────
    "FR": {

        # App-level
        "app_title":            "Caractérisation — {facility}",
        "app_version":          "Version : {version}",
        "dev_mode_warning":     "🛠️ DEV MODE — Dropbox désactivé.",

        # Navigation tabs
        "nav_metadata":         "Métadonnées ➡️",
        "nav_containers":       "Contenants ➡️",
        "nav_weighing":         "Résultats de pesée ➡️",
        "nav_summary":          "Résumé",

        # Common buttons
        "btn_save":             "💾 Sauvegarder",
        "btn_back":             "⬅️ Retour",
        "btn_next_containers":  "Étape suivante : Configurer les Contenants ➡️",
        "btn_next_weighing":    "Étape suivante : Saisir les Pesées ➡️",
        "btn_next_summary":     "Étape suivante : Consulter le Résumé ➡️",
        "btn_confirm":          "Confirmer",
        "btn_cancel":           "❌ Annuler",
        "btn_add":              "✅ Ajouter",
        "btn_delete":           "✕",
        "btn_edit":             "✏️",
        "btn_download":         "⬇️ Télécharger (Excel + PDF + photos)",
        "btn_dropbox":          "☁️ Sauvegarder sur Dropbox",
        "btn_new_session":      "🔄 Nouvelle session",
        "btn_new_entry":        "🆕 Nouvelle saisie",
        "btn_logout":           "🚪 Se déconnecter",
        "btn_timing_app":       "⏱️ Mesures de temps",

        # Sidebar
        "sidebar_config_title": "📌 Configuration active",
        "sidebar_operator":     "Opérateur",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Capteur",
        "sidebar_workflow":     "Workflow",
        "sidebar_weighings":    "Pesées enregistrées",
        "sidebar_export_title": "💾 Sauvegarde",
        "sidebar_no_data":      "📦 L'export s'activera ici dès qu'une pesée sera enregistrée.",
        "sidebar_new_session_help": "Réinitialiser pour un nouveau test",
        "sidebar_guide_title":  "📖 Guide d'utilisation rapide",
        "sidebar_guide_body":   """
**1️⃣ Métadonnées** — Workflow, informations, heures de passage sous le capteur.

**2️⃣ Contenants** — Tares des bacs ou cartons. Passez si pesée directe.

**3️⃣ Résultats de pesée** — Saisissez les poids bruts classe par classe.

**4️⃣ Résumé** — Tableau de bord et export.
""",
        "sidebar_preview_as":   "Voir en tant que :",
        "sidebar_version":      "Version : {version}",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guide — Métadonnées",
        "meta_workflow_title":  "### ⚙️ Type de workflow",
        "meta_workflow_label":  "Type de workflow",
        "meta_order_label":     "Ordre de passage",
        "meta_order_a_caption": "Capteur ➡️ Collecte ➡️ Pesée",
        "meta_order_b_caption": "Collecte ➡️ Pesée ➡️ Capteur",
        "meta_info_title":      "### ℹ️ Informations générales",
        "meta_operator_name":   "Nom *",
        "meta_operator_ph":     "Entrez votre nom",
        "meta_sensor":          "Nom du capteur",
        "meta_date":            "Date de prélèvement",
        "meta_nb_samples":      "Nombre d'échantillons",
        "meta_times_title":     "### 🕒 Heures de passage sous le capteur WasteFlow",
        "meta_skip_toggle":     "Ne pas renseigner d'heures de collecte maintenant",
        "meta_skip_caption":    "Les heures de collecte ne seront pas renseignées.",
        "meta_sample_label":    "📦 Échantillon {n}",
        "meta_start_time":      "Heure de début *",
        "meta_end_time":        "Heure de fin *",
        "meta_recap_title":     "📋 Récapitulatif des plages horaires",
        "meta_recap_empty":     "Aucune plage horaire enregistrée.",
        "meta_recap_sample":    "Échantillon",
        "meta_recap_date":      "Date",
        "meta_recap_start":     "Début",
        "meta_recap_end":       "Fin",
        "meta_saved_toast":     "Métadonnées sauvegardées ✓",
        "meta_error_start":     "Échantillon {n} : format d'heure de début invalide ('{raw}'). Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Échantillon {n} : format d'heure de fin invalide ('{raw}'). Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Échantillon {n} : l'heure de fin doit être postérieure à l'heure de début.",

        # Tab 2 — Containers
        "cont_guide_title":     "⁉️ Guide — Contenants",
        "cont_add_title":       "### 📥 Ajout de contenant",
        "cont_list_title":      "### 📋 Contenants enregistrés",
        "cont_name_label":      "Identificateur du contenant",
        "cont_name_ph":         "Ex: Carton A, Bac Bleu 1...",
        "cont_weight_label":    "Poids à vide (kg)",
        "cont_add_btn":         "✅ Ajouter le contenant",
        "cont_empty_info":      "Aucun contenant enregistré. Tare = 0.000 kg par défaut.",
        "cont_tare_caption":    "Tare : `{tare:.3f} kg`",
        "cont_delete_help":     "Supprimer ce contenant",
        "cont_error_invalid":   "Le poids doit être un nombre valide.",
        "cont_error_empty":     "Veuillez renseigner un identifiant de contenant.",
        "cont_error_exists":    "Ce contenant existe déjà.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guide — Résultats de pesée",
        "weigh_form_title":     "### 📥 Entrée de pesée",
        "weigh_sample_label":   "Numéro(s) d'échantillon",
        "weigh_sample_ph":      "Choisir l'échantillon...",
        "weigh_class_label":    "Classe de matériau",
        "weigh_class_ph":       "Choisir...",
        "weigh_container_label":"Contenant utilisé",
        "weigh_no_container":   "Pas de contenant",
        "weigh_image_label":    "Photo du matériau (optionnel)",
        "weigh_gross_label":    "POIDS BRUT (kg)",
        "weigh_gross_ph":       "Ex: 12.5 14.2 — séparés par un espace",
        "weigh_add_btn":        "✅ Ajouter la pesée",
        "weigh_added_toast":    "Pesée ajoutée !",
        "weigh_obs_title":      "### Observations",
        "weigh_obs_ph":         "Ajoutez ici toute remarque sur la session.",
        "weigh_history_title":  "📋 Historique des pesées ({n})",
        "weigh_history_empty":  "Aucune pesée enregistrée.",
        "weigh_edit_help":      "Modifier",
        "weigh_delete_help":    "Supprimer",
        "weigh_disable_warning":"⚠️ Renseignez d'abord les heures de prélèvement dans l'onglet **Métadonnées**.",
        "weigh_error_format":   "Veuillez vérifier la saisie des poids bruts. Séparez les poids par des espaces, avec virgule ou point décimal.",
        "weigh_error_no_sample":"Veuillez choisir au moins un échantillon.",
        "weigh_error_no_class": "Veuillez choisir une classe de matériau.",
        "weigh_error_negative": "Le poids net calculé est négatif ({net:.3f} kg). Vérifiez le contenant sélectionné et les poids saisis.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Modifier la pesée",
        "dialog_edit_intro":    "Vous modifiez la pesée **n° {n}**.",
        "dialog_edit_save":     "💾 Enregistrer",
        "dialog_edit_no_sample":"⚠️ Veuillez choisir au moins un échantillon.",
        "dialog_edit_negative": "⚠️ Poids net négatif ({net:.3f} kg). Vérifiez le poids brut ou la tare.",
        "dialog_edit_toast":    "Pesée mise à jour !",

        # Tab 4 — Summary
        "summ_guide_title":     "⁉️ Guide — Résumé",
        "summ_dashboard_title": "📊 Tableau de bord",
        "summ_total_metric":    "Masse totale enregistrée",
        "summ_chart_title":     "Répartition par classe de matériau",
        "summ_sample_detail":   "📋 Détail par échantillon",
        "summ_sample_label":    "Échantillon {id}",
        "summ_missing_warning": "⚠️ **{n} classe(s) sans pesée :**",
        "summ_export_title":    "📤 Clôture de la session",
        "summ_no_data":         "Aucune pesée enregistrée pour le moment.",

        # Summary table columns
        "summ_col_class":       "Classe de matériau",
        "summ_col_net":         "Poids net",
        "summ_col_pct":         "Pourcentage de la masse totale",

        # Dialog — new session
        "dialog_new_title":     "Nouvelle saisie",
        "dialog_new_warning":   "Cette action effacera toutes les données de la session en cours. Cette opération est irréversible.",

        # Dropbox
        "dropbox_uploading":    "Envoi sur Dropbox...",
        "dropbox_success":      "Sauvegardé sur Dropbox !",
        "dropbox_error_key":    "Dropbox — clé de configuration manquante : {e}",
        "dropbox_error_auth":   "Dropbox — échec de l'authentification : {e}",
        "dropbox_error_token":  "Dropbox — token expiré ou invalide : {e}",
        "dropbox_error_api":    "Dropbox — erreur API ({path}) : {e}",
        "dropbox_error_other":  "Dropbox — erreur inattendue : {e}",

        # Auth
        "auth_wrong":           "Identifiant ou mot de passe incorrect.",
        "auth_prompt":          "Veuillez vous connecter pour accéder au formulaire.",
        "auth_connected_as":    "👤 Connecté en tant que **{name}**",
    },

    # ── EN ────────────────────────────────────────────────────────────────────
    "EN": {

        # App-level
        "app_title":            "Characterization — {facility}",
        "app_version":          "Version: {version}",
        "dev_mode_warning":     "🛠️ DEV MODE — Dropbox disabled.",

        # Navigation tabs
        "nav_metadata":         "Metadata ➡️",
        "nav_containers":       "Containers ➡️",
        "nav_weighing":         "Weighing results ➡️",
        "nav_summary":          "Summary",

        # Common buttons
        "btn_save":             "💾 Save",
        "btn_back":             "⬅️ Back",
        "btn_next_containers":  "Next step: Configure Containers ➡️",
        "btn_next_weighing":    "Next step: Enter Weighings ➡️",
        "btn_next_summary":     "Next step: View Summary ➡️",
        "btn_confirm":          "Confirm",
        "btn_cancel":           "❌ Cancel",
        "btn_add":              "✅ Add",
        "btn_delete":           "✕",
        "btn_edit":             "✏️",
        "btn_download":         "⬇️ Download (Excel + PDF + photos)",
        "btn_dropbox":          "☁️ Save to Dropbox",
        "btn_new_session":      "🔄 New session",
        "btn_new_entry":        "🆕 New entry",
        "btn_logout":           "🚪 Log out",
        "btn_timing_app":       "⏱️ Time measurements",

        # Sidebar
        "sidebar_config_title": "📌 Active configuration",
        "sidebar_operator":     "Operator",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Sensor",
        "sidebar_workflow":     "Workflow",
        "sidebar_weighings":    "Recorded weighings",
        "sidebar_export_title": "💾 Save",
        "sidebar_no_data":      "📦 Export will appear here once a weighing is recorded.",
        "sidebar_new_session_help": "Reset for a new test",
        "sidebar_guide_title":  "📖 Quick user guide",
        "sidebar_guide_body":   """
**1️⃣ Metadata** — Workflow, operator info, sensor passage times.

**2️⃣ Containers** — Tare weights for boxes or bins. Skip if weighing directly.

**3️⃣ Weighing results** — Enter gross weights class by class.

**4️⃣ Summary** — Dashboard and export.
""",
        "sidebar_preview_as":   "View as:",
        "sidebar_version":      "Version: {version}",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guide — Metadata",
        "meta_workflow_title":  "### ⚙️ Workflow type",
        "meta_workflow_label":  "Workflow type",
        "meta_order_label":     "Passage order",
        "meta_order_a_caption": "Sensor ➡️ Collection ➡️ Weighing",
        "meta_order_b_caption": "Collection ➡️ Weighing ➡️ Sensor",
        "meta_info_title":      "### ℹ️ General information",
        "meta_operator_name":   "Name *",
        "meta_operator_ph":     "Enter your name",
        "meta_sensor":          "Sensor name",
        "meta_date":            "Sampling date",
        "meta_nb_samples":      "Number of samples",
        "meta_times_title":     "### 🕒 Passage times under the WasteFlow sensor",
        "meta_skip_toggle":     "Do not enter collection times now",
        "meta_skip_caption":    "Collection times will not be recorded.",
        "meta_sample_label":    "📦 Sample {n}",
        "meta_start_time":      "Start time *",
        "meta_end_time":        "End time *",
        "meta_recap_title":     "📋 Collection time summary",
        "meta_recap_empty":     "No time slots recorded.",
        "meta_recap_sample":    "Sample",
        "meta_recap_date":      "Date",
        "meta_recap_start":     "Start",
        "meta_recap_end":       "End",
        "meta_saved_toast":     "Metadata saved ✓",
        "meta_error_start":     "Sample {n}: invalid start time format ('{raw}'). Accepted formats: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Sample {n}: invalid end time format ('{raw}'). Accepted formats: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Sample {n}: end time must be later than start time.",

        # Tab 2 — Containers
        "cont_guide_title":     "⁉️ Guide — Containers",
        "cont_add_title":       "### 📥 Add container",
        "cont_list_title":      "### 📋 Registered containers",
        "cont_name_label":      "Container identifier",
        "cont_name_ph":         "E.g. Box A, Blue Bin 1...",
        "cont_weight_label":    "Empty weight (kg)",
        "cont_add_btn":         "✅ Add container",
        "cont_empty_info":      "No containers registered. Tare = 0.000 kg by default.",
        "cont_tare_caption":    "Tare: `{tare:.3f} kg`",
        "cont_delete_help":     "Delete this container",
        "cont_error_invalid":   "Weight must be a valid number.",
        "cont_error_empty":     "Please enter a container identifier.",
        "cont_error_exists":    "This container already exists.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guide — Weighing results",
        "weigh_form_title":     "### 📥 Weighing entry",
        "weigh_sample_label":   "Sample number(s)",
        "weigh_sample_ph":      "Choose sample...",
        "weigh_class_label":    "Material class",
        "weigh_class_ph":       "Choose...",
        "weigh_container_label":"Container used",
        "weigh_no_container":   "No container",
        "weigh_image_label":    "Material photo (optional)",
        "weigh_gross_label":    "GROSS WEIGHT (kg)",
        "weigh_gross_ph":       "E.g. 12.5 14.2 — separated by spaces",
        "weigh_add_btn":        "✅ Add weighing",
        "weigh_added_toast":    "Weighing added!",
        "weigh_obs_title":      "### Observations",
        "weigh_obs_ph":         "Add any remarks about this session here.",
        "weigh_history_title":  "📋 Weighing history ({n})",
        "weigh_history_empty":  "No weighings recorded.",
        "weigh_edit_help":      "Edit",
        "weigh_delete_help":    "Delete",
        "weigh_disable_warning":"⚠️ Please fill in collection times in the **Metadata** tab first.",
        "weigh_error_format":   "Please check the gross weight input. Separate values with spaces, using commas or decimal points.",
        "weigh_error_no_sample":"Please select at least one sample.",
        "weigh_error_no_class": "Please select a material class.",
        "weigh_error_negative": "Calculated net weight is negative ({net:.3f} kg). Check the container and entered weights.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Edit weighing",
        "dialog_edit_intro":    "You are editing weighing **n° {n}**.",
        "dialog_edit_save":     "💾 Save",
        "dialog_edit_no_sample":"⚠️ Please select at least one sample.",
        "dialog_edit_negative": "⚠️ Negative net weight ({net:.3f} kg). Check gross weight or tare.",
        "dialog_edit_toast":    "Weighing updated!",

        # Tab 4 — Summary
        "summ_guide_title":     "⁉️ Guide — Summary",
        "summ_dashboard_title": "📊 Dashboard",
        "summ_total_metric":    "Total recorded mass",
        "summ_chart_title":     "Distribution by material class",
        "summ_sample_detail":   "📋 Detail by sample",
        "summ_sample_label":    "Sample {id}",
        "summ_missing_warning": "⚠️ **{n} class(es) with no weighing:**",
        "summ_export_title":    "📤 Close session",
        "summ_no_data":         "No weighings recorded yet.",

        # Summary table columns
        "summ_col_class":       "Material class",
        "summ_col_net":         "Net weight",
        "summ_col_pct":         "% of total mass",

        # Dialog — new session
        "dialog_new_title":     "New entry",
        "dialog_new_warning":   "This will erase all data from the current session. This operation is irreversible.",

        # Dropbox
        "dropbox_uploading":    "Uploading to Dropbox...",
        "dropbox_success":      "Saved to Dropbox!",
        "dropbox_error_key":    "Dropbox — missing configuration key: {e}",
        "dropbox_error_auth":   "Dropbox — authentication failed: {e}",
        "dropbox_error_token":  "Dropbox — token expired or invalid: {e}",
        "dropbox_error_api":    "Dropbox — API error ({path}): {e}",
        "dropbox_error_other":  "Dropbox — unexpected error: {e}",

        # Auth
        "auth_wrong":           "Incorrect username or password.",
        "auth_prompt":          "Please log in to access the form.",
        "auth_connected_as":    "👤 Logged in as **{name}**",
    },
}


# ── HELPERS ───────────────────────────────────────────────────────────────────
def set_lang(lang: str) -> None:
    """Set the active language in session state."""
    if lang in LANGUAGES:
        st.session_state["lang"] = lang


def get_lang() -> str:
    """Return the active language, defaulting to FR."""
    return st.session_state.get("lang", DEFAULT_LANG)


def t(key: str, **kwargs) -> str:
    """Return the translation for key in the current language.

    Supports placeholders: t("meta_error_start", n=1, raw="25:00")
    Falls back to FR if key is missing in the current language.
    Falls back to the key itself if missing in both.
    """
    lang = get_lang()
    value = (
        _TRANSLATIONS.get(lang, {}).get(key)
        or _TRANSLATIONS.get(DEFAULT_LANG, {}).get(key)
        or key
    )
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value
    return value


# ── CONSISTENCY CHECK (runs once at import time in dev) ───────────────────────
def _check_translations() -> None:
    """Warn about keys present in one language but missing in another."""
    all_keys = set()
    for lang_dict in _TRANSLATIONS.values():
        all_keys |= set(lang_dict.keys())

    missing: dict[str, list[str]] = {}
    for lang, lang_dict in _TRANSLATIONS.items():
        missing_keys = sorted(all_keys - set(lang_dict.keys()))
        if missing_keys:
            missing[lang] = missing_keys

    if missing:
        import warnings
        for lang, keys in missing.items():
            warnings.warn(
                f"i18n: {len(keys)} key(s) missing in '{lang}': {keys}",
                stacklevel=2,
            )


_check_translations()
