"""
i18n.py — Translations for WasteChar (FR / EN / ES)

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

LANGUAGES = ["FR", "EN", "ES"]
DEFAULT_LANG = "FR"

_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── FR ────────────────────────────────────────────────────────────────────
    "FR": {

        # PDF report
        "pdf_title": "Rapport de caractérisation",
        "pdf_header_site": "Site : {facility}  |  Opérateur : {operator}  |  Date : {date}",
        "pdf_header_sensor": "Capteur : {sensor}  |  Échantillonnage : {sampling}",
        "pdf_header_passage": "Passage du capteur : {passage}",
        "pdf_footer": "WasteFlow App {version}  |  Exporté le {date} à {time}",
        "pdf_overview": "Indicateurs globaux",
        "pdf_count": "Nombre total de pesées enregistrées : {count}",
        "pdf_gross": "Masse brute totale : {weight:.3f} kg",
        "pdf_net": "Masse nette totale triée : {weight:.3f} kg",
        "pdf_present": "Classes présentes",
        "pdf_absent": "Classes sans données",
        "pdf_none": "Aucune",
        "pdf_comment": "Commentaire général",
        "pdf_collection": "Plages horaires de collecte",
        "pdf_sample": "Échantillon",
        "pdf_date": "Date",
        "pdf_start": "Heure de début",
        "pdf_end": "Heure de fin",
        "pdf_distribution": "Répartition par classe de matériau",
        "pdf_material": "Classe de matériau",
        "pdf_net_column": "Poids net (kg)",
        "pdf_percentage": "% de la masse totale",
        "pdf_total": "TOTAL",
        "pdf_chart": "Comparaison par classe de matériau",
        "pdf_axis": "Masse nette (kg)",

        # App-level
        "page_title":           "Résultat de caractérisation",
        "app_title":            "Caractérisation — {facility}",
        "app_version":          "Version : {version}",

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
        "btn_dropbox":          "Sauvegarder sur Dropbox",
        "btn_new_session":      "Nouvelle session",
        "btn_new_entry":        "Nouvelle saisie",
        "btn_logout":           "Se déconnecter",
        "btn_timing_app":       "⏱Mesures de temps",

        # Sidebar
        "sidebar_config_title": "### Configuration active",
        "sidebar_operator":     "Opérateur",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Capteur",
        "sidebar_workflow":     "Échantillonnage / passage du capteur",
        "sidebar_weighings":    "Pesées enregistrées",
        "sidebar_export_title": "### 💾 Sauvegarde",
        "sidebar_no_data":      "L'export s'activera ici dès qu'une pesée sera enregistrée.",
        "sidebar_new_session_help": "Réinitialiser pour un nouveau test",
        "sidebar_guide_title":  "Guide d'utilisation rapide",
        "sidebar_guide_intro":  "Suivez les 4 étapes dans l'ordre via la barre de navigation en haut.",
        "sidebar_guide_body":   """
**1️⃣ Métadonnées** — Échantillonnage, passage du capteur, informations et horaires.

**2️⃣ Contenants** — Tares des bacs ou cartons. Passez si pesée directe.

**3️⃣ Résultats de pesée** — Saisissez les poids bruts classe par classe.

**4️⃣ Résumé** — Tableau de bord et export.
""",
        "sidebar_preview_as":   "Voir en tant que :",
        "sidebar_version":      "Version : {version}",
        "sidebar_dropbox_upload": "📤 Envoyer sur Dropbox",
        "sidebar_show_tutorials": "Afficher les tutoriels",
        "sidebar_language": "Langue",
        "sidebar_timezone": "Fuseau horaire : {timezone}",
        "sidebar_report_title": "**Saisie en cours**",
        "sidebar_no_report": "Aucune saisie en cours.",
        "sidebar_report_details": "{date} · {sensor}",
        "sidebar_weighings_count": "{n} pesée(s) enregistrée(s)",
        "sidebar_save_saved_at": "✅ Saisie sauvegardée temporairement sur le serveur à {time}",
        "sidebar_save_saved": "✅ Saisie sauvegardée temporairement sur le serveur",
        "sidebar_save_new": "Aucune sauvegarde pour le moment",
        "sidebar_save_unsaved": "Modifications non sauvegardées",
        "sidebar_save_failed": "Échec de la sauvegarde. Les données peuvent être perdues si la page est actualisée.",
        "sidebar_save_retry": "Réessayer la sauvegarde",
        "sidebar_restore_failed": "Impossible de restaurer la session sauvegardée.",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guide — Métadonnées",
        "meta_guide_body":      """
Renseignez les informations du test **avant de commencer à peser**. Les modifications
sont sauvegardées automatiquement ; le bouton **💾 Sauvegarder** force une sauvegarde manuelle.

---

#### 1. Échantillonnage et passage du capteur

| Option | Description |
|---|---|
| **Échantillonnage : unique** | 1 seul échantillon |
| **Échantillonnage : multiple** | Plusieurs prélèvements distincts |
| **Capteur : avant la pesée** | Capteur ➡️ Collecte ➡️ Pesée |
| **Capteur : après la pesée** | Collecte ➡️ Pesée ➡️ Capteur |

#### 2. Informations générales
Renseignez votre nom, la date, le capteur et le nombre d'échantillons.

#### 3. Heures de passage
Pour chaque échantillon, indiquez l'heure de début et de fin de passage sous le capteur.
Formats acceptés : `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
""",
        "meta_workflow_container_title": "### Échantillonnage et passage du capteur",
        "meta_workflow_title":  "### Échantillonnage",
        "meta_workflow_label":  "Échantillonnage",
        "meta_wf_standard":     "Unique",
        "meta_wf_multi":        "Multiple",
        "meta_wf_standard_caption": "Une seule collecte de matière",
        "meta_wf_multi_caption": "Plusieurs collectes de matière pour une seule caractérisation",
        "meta_order_label":     "Passage sous capteur",
        "meta_wfo_order_a":     "Avant la pesée",
        "meta_wfo_order_b":     "Après la pesée",
        "meta_order_a_caption": "Capteur ➡️ Collecte ➡️ Pesée",
        "meta_order_b_caption": "Collecte ➡️ Pesée ➡️ Capteur",
        "meta_info_title":      "### Informations générales",
        "meta_operator_name":   "Nom *",
        "meta_operator_ph":     "Entrez votre nom",
        "meta_sensor":          "Nom du capteur",
        "meta_date":            "Date de prélèvement",
        "meta_nb_samples":      "Nombre d'échantillons",
        "meta_times_title":     "### Heures de passage sous le capteur WasteFlow",
        "meta_skip_toggle":     "Ne pas renseigner d'heures de collecte maintenant",
        "meta_skip_caption":    "Les heures de collecte ne seront pas renseignées.",
        "meta_sample_label":    "Échantillon {n}",
        "meta_start_time":      "Heure de début *",
        "meta_end_time":        "Heure de fin *",
        "meta_recap_title":     "**Récapitulatif des plages horaires**",
        "meta_recap_empty":     "Aucune plage horaire enregistrée.",
        "meta_recap_sample":    "Échantillon",
        "meta_recap_date":      "Date",
        "meta_recap_start":     "Début",
        "meta_recap_end":       "Fin",
        "meta_saved_toast":     "Métadonnées sauvegardées ✓",
        "meta_error_start":     "Échantillon {n} : format d'heure de début invalide ('{raw}'). Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Échantillon {n} : format d'heure de fin invalide ('{raw}'). Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Échantillon {n} : l'heure de fin doit être postérieure à l'heure de début.",
        "meta_missing_operator": "Nom de l'opérateur manquant.",
        "meta_missing_sensor": "Capteur manquant.",
        "meta_missing_date": "Date du test manquante.",
        "meta_invalid_sample_count": "Nombre d'échantillons invalide.",
        "meta_missing_times": "Échantillon {n} : heures de début et de fin manquantes.",
        "meta_missing_start": "Échantillon {n} : heure de début manquante.",
        "meta_missing_end": "Échantillon {n} : heure de fin manquante.",
        "meta_invalid_times": "Échantillon {n} : heures de collecte invalides.",
        "meta_referenced_samples": "Impossible de réduire le nombre d'échantillons : des pesées utilisent encore les échantillons supprimés.",
        "meta_draft_warning": "Brouillon incomplet. Corrigez ces champs avant de continuer :",
        "report_missing_weighings": "Aucune pesée enregistrée.",
        "report_invalid_weighings": "Une ou plusieurs pesées ont un poids invalide.",
        "report_invalid_samples": "Une ou plusieurs pesées indiquent un échantillon invalide.",
        "export_draft_warning": "Export indisponible tant que le rapport est incomplet :",

        # Tab 2 — Containers
        "cont_guide_title":     "⁉️ Guide — Contenants",
        "cont_guide_body":      """
Les contenants sont les bacs ou cartons utilisés pour peser les matériaux.
Leur poids à vide (tare) est automatiquement soustrait pour calculer le **poids net**.

**Comment ajouter un contenant :**
1. Saisissez un nom clair (ex : `Carton A`, `Bac Bleu 1`)
2. Pesez le contenant vide et entrez son poids en kg
3. Cliquez sur **✅ Ajouter le contenant**

> Si vous ne pesez pas dans un contenant, **laissez cet onglet vide** — le poids brut sera égal au poids net.
""",
        "cont_add_title":       "### Ajout de contenant",
        "cont_list_title":      "### Contenants enregistrés",
        "cont_name_label":      "Identificateur du contenant",
        "cont_name_ph":         "Ex: Carton A, Bac Bleu 1...",
        "cont_weight_label":    "Poids à vide (kg)",
        "cont_add_btn":         "✅ Ajouter le contenant",
        "cont_empty_info":      "Aucun contenant enregistré. Tare = 0.000 kg par défaut.",
        "cont_tare_caption":    "Tare : `{tare:.3f} kg`",
        "cont_delete_help":     "Supprimer ce contenant",
        "cont_used_cannot_delete": "Suppression bloquée : {n} pesée(s) utilisent ce contenant.",
        "cont_error_invalid":   "La tare doit être un nombre fini et positif ou nul (0 autorisé).",
        "cont_error_empty":     "Veuillez renseigner un identifiant de contenant.",
        "cont_error_exists":    "Ce contenant existe déjà.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guide — Résultats de pesée",
        "weigh_guide_body":     """
Saisissez les pesées **une classe de matériau à la fois**.

**Pour chaque pesée :**
1. **Numéro(s) d'échantillon** — Échantillonnage unique = figé à 1. Multiple = libre.
2. **Classe de matériau** — Choisissez dans la liste ou saisissez une nouvelle valeur.
3. **Contenant utilisé** — Ou *Pas de contenant* pour une pesée directe.
4. **Poids brut (kg)** — Plusieurs poids séparés par des espaces (ex : `12.5 8.3`).
5. Cliquez sur ✅ **Ajouter la pesée**.

---

#### Corriger une erreur
Cliquez sur **✕** pour supprimer une ligne ou **✏️** pour la modifier.

> Si le bouton **Ajouter la pesée** est grisé, vérifiez que les heures de
prélèvement sont renseignées dans **Métadonnées** (ou activez le mode sans heures).
""",
        "weigh_mode_label":     "Mode de saisie",
        "weigh_mode_table":     "Tableau",
        "weigh_pending_next_save": "Modifications non enregistrées : le bouton Étape suivante les enregistrera avant d’ouvrir le résumé.",
        "weigh_mode_manual":    "Manuel",
        "weigh_table_title":    "### Saisie par tableau",
        "weigh_table_intro": "Les modes Tableau et Manuel montrent les mêmes pesées. Chaque pesée enregistrée a sa propre ligne, y compris les matériaux personnalisés. Modifier une ligne corrige la pesée existante. Les lignes sans poids sont ignorées. En mode multi-échantillon, indiquez les numéros séparés par des virgules. Utilisez Manuel pour ajouter une autre pesée ou une photo. Supprimez les pesées via l’historique.",
        "weigh_table_other_entries": "Les pesées saisies en mode Manuel ou avant cette mise à jour restent dans l'historique ; ce tableau ne les remplace pas.",
        "weigh_table_filter": "Rechercher un matériau",
        "weigh_table_filter_placeholder": "Nom du matériau...",
        "weigh_table_shown": "{shown} matériau(x) affiché(s) sur {total}",
        "weigh_table_no_match": "Aucun matériau ne correspond à cette recherche.",
        "weigh_table_net_label": "Poids net (kg)",
        "weigh_table_no_classes": "Aucune classe de matériau configurée pour cette installation.",
        "weigh_table_save_btn": "💾 Enregistrer les lignes modifiées",
        "weigh_table_preview": "{filled} ligne(s) remplie(s) · {added} à ajouter · {corrected} à corriger · Net dans le tableau : {net:.3f} kg",
        "weigh_table_recorded_badge": "Saisie par tableau",
        "weigh_table_edit_here": "Modifier dans le tableau",
        "weigh_table_saved_count": "{added} pesée(s) ajoutée(s), {corrected} corrigée(s).",
        "weigh_table_error_duplicate": "Plusieurs pesées du tableau existent pour « {material} ». Supprimez le doublon dans l'historique.",
        "weigh_table_error_stale": "La pesée de « {material} » a changé. Rechargez le tableau avant d'enregistrer.",
        "weigh_table_error_clear": "« {material} » est déjà enregistrée. Pour la supprimer, utilisez l'historique.",
        "weigh_table_error_sample": "Choisissez un échantillon valide pour « {material} ».",
        "weigh_table_error_container": "Choisissez un contenant valide pour « {material} ».",
        "weigh_table_error_weight": "Saisissez un poids brut fini et positif ou nul pour « {material} » (0 autorisé).",
        "weigh_table_error_tare": "Tare invalide pour « {material} ». Corrigez le contenant.",
        "weigh_table_error_negative": "Poids net négatif ({net:.3f} kg) pour « {material} ». Vérifiez la tare.",
        "weigh_table_saved_toast": "Pesées enregistrées !",
        "weigh_table_error_empty": "Veuillez saisir au moins un poids brut.",
        "weigh_table_error_no_sample": "Veuillez choisir un numéro d'échantillon pour chaque ligne pesée.",
        "weigh_hist_samples":   "Échantillon(s)",
        "weigh_hist_tare":      "Tarage",
        "weigh_hist_gross":     "Brut",
        "weigh_hist_net":       "Net",
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
        "weigh_history_title":  "Historique des pesées ({n})",
        "weigh_history_empty":  "Aucune pesée enregistrée.",
        "weigh_edit_help":      "Modifier",
        "weigh_delete_help":    "Supprimer",
        "weigh_disable_warning":"⚠️ Renseignez d'abord les heures de prélèvement dans l'onglet **Métadonnées**.",
        "weigh_error_format":   "Saisissez des poids finis et positifs ou nuls (0 autorisé), séparés par des espaces. Virgule ou point décimal accepté.",
        "weigh_error_invalid_tare": "Tare invalide. Corrigez le contenant avant d'enregistrer la pesée.",
        "weigh_error_no_sample":"Veuillez choisir au moins un échantillon.",
        "weigh_error_no_class": "Veuillez choisir une classe de matériau.",
        "weigh_error_negative": "Le poids net calculé est négatif ({net:.3f} kg). Vérifiez le contenant sélectionné et les poids saisis.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Modifier la pesée",
        "dialog_edit_intro":    "Vous modifiez la pesée **n° {n}**.",
        "dialog_edit_save":     "💾 Enregistrer",
        "dialog_edit_no_sample":"⚠️ Veuillez choisir au moins un échantillon.",
        "dialog_edit_negative": "⚠️ Poids net négatif ({net:.3f} kg). Vérifiez le poids brut ou la tare.",
        "dialog_edit_invalid_weight": "⚠️ Le poids brut doit être fini et positif ou nul (0 autorisé).",
        "dialog_edit_invalid_tare": "⚠️ La tare du contenant est invalide.",
        "dialog_edit_toast":    "Pesée mise à jour !",

        # Tab 4 — Summary
        "summ_guide_title":     "⁉️ Guide — Résumé",
        "summ_guide_body":      """
Cet onglet affiche un tableau de bord complet une fois les pesées saisies.

**Ce que vous trouverez ici :**
- La **masse totale** et le tableau récapitulatif par classe de matériau
- Un **graphique** de la répartition
- Un résumé détaillé **par échantillon**

**Exporter :** Cliquez sur **⬇️ Télécharger** pour un ZIP contenant Excel, PDF et photos.
Le fichier est aussi envoyé automatiquement sur Dropbox.
""",
        "summ_guide_tip":       "✅ Téléchargez toujours le fichier avant de lancer une nouvelle saisie.",
        "summ_dashboard_title": "Tableau de bord",
        "summ_total_metric":    "Masse totale enregistrée",
        "summ_chart_title":     "Répartition par classe de matériau",
        "summ_zero_distribution": "Masse nette totale : 0 kg. Aucune répartition à afficher ; les pesées à zéro restent enregistrées.",
        "summ_invalid_weights": "{n} pesée(s) ont un poids invalide. Corrigez-les dans l'historique des pesées avant d'exporter.",
        "summ_sample_detail":   "Détail par échantillon",
        "summ_sample_label":    "Échantillon {id}",
        "summ_missing_warning": "⚠️ **{n} classe(s) sans pesée :**",
        "summ_export_title":    "📤 Clôture de la session",
        "summ_dropbox_upload": "Envoyer le ZIP sur Dropbox au téléchargement",
        "summ_upload_on_download": "Le téléchargement enverra aussi le ZIP sur Dropbox.",
        "summ_download_only": "Le ZIP sera uniquement téléchargé.",
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
        "dropbox_upload_failed": "Le téléchargement est disponible, mais l'envoi sur Dropbox a échoué.",
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

        # PDF report
        "pdf_title": "Characterization report",
        "pdf_header_site": "Facility: {facility}  |  Operator: {operator}  |  Date: {date}",
        "pdf_header_sensor": "Sensor: {sensor}  |  Sampling: {sampling}",
        "pdf_header_passage": "Sensor passage: {passage}",
        "pdf_footer": "WasteFlow App {version}  |  Exported on {date} at {time}",
        "pdf_overview": "Global indicators",
        "pdf_count": "Total recorded weighings: {count}",
        "pdf_gross": "Total gross mass: {weight:.3f} kg",
        "pdf_net": "Total sorted net mass: {weight:.3f} kg",
        "pdf_present": "Recorded material classes",
        "pdf_absent": "Classes without data",
        "pdf_none": "None",
        "pdf_comment": "General comment",
        "pdf_collection": "Collection time ranges",
        "pdf_sample": "Sample",
        "pdf_date": "Date",
        "pdf_start": "Start time",
        "pdf_end": "End time",
        "pdf_distribution": "Distribution by material class",
        "pdf_material": "Material class",
        "pdf_net_column": "Net weight (kg)",
        "pdf_percentage": "% of total mass",
        "pdf_total": "TOTAL",
        "pdf_chart": "Comparison by material class",
        "pdf_axis": "Net mass (kg)",

        # App-level
        "page_title":           "Characterization result",
        "app_title":            "Characterization — {facility}",
        "app_version":          "Version: {version}",

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
        "btn_dropbox":          "Save to Dropbox",
        "btn_new_session":      "New session",
        "btn_new_entry":        "New entry",
        "btn_logout":           "Log out",
        "btn_timing_app":       "⏱Time measurements",

        # Sidebar
        "sidebar_config_title": "### Active configuration",
        "sidebar_operator":     "Operator",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Sensor",
        "sidebar_workflow":     "Sampling / Sensor passage",
        "sidebar_weighings":    "Recorded weighings",
        "sidebar_export_title": "### 💾 Save",
        "sidebar_no_data":      "Export will appear here once a weighing is recorded.",
        "sidebar_new_session_help": "Reset for a new test",
        "sidebar_guide_title":  "Quick user guide",
        "sidebar_guide_intro":  "Follow the 4 steps in order using the navigation bar at the top.",
        "sidebar_guide_body":   """
**1️⃣ Metadata** — Sampling, sensor passage, operator info, and collection times.

**2️⃣ Containers** — Tare weights for boxes or bins. Skip if weighing directly.

**3️⃣ Weighing results** — Enter gross weights class by class.

**4️⃣ Summary** — Dashboard and export.
""",
        "sidebar_preview_as":   "View as:",
        "sidebar_version":      "Version: {version}",
        "sidebar_dropbox_upload": "📤 Upload to Dropbox",
        "sidebar_show_tutorials": "Show tutorials",
        "sidebar_language": "Language",
        "sidebar_timezone": "Time zone: {timezone}",
        "sidebar_report_title": "**Current report**",
        "sidebar_no_report": "No report in progress.",
        "sidebar_report_details": "{date} · {sensor}",
        "sidebar_weighings_count": "{n} recorded weighing(s)",
        "sidebar_save_saved_at": "✅ Entries temporarily saved on the server at {time}",
        "sidebar_save_saved": "✅ Entries temporarily saved on the server",
        "sidebar_save_new": "No save yet",
        "sidebar_save_unsaved": "Unsaved changes",
        "sidebar_save_failed": "Save failed. Data may be lost if the page is refreshed.",
        "sidebar_save_retry": "Retry saving",
        "sidebar_restore_failed": "Could not restore the saved session.",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guide — Metadata",
        "meta_guide_body":      """
Fill in the test information **before you start weighing**. Changes are saved automatically;
the **💾 Save** button forces a manual save.

---

#### 1. Sampling and sensor passage

| Option | Description |
|---|---|
| **Sampling: Single** | One sample |
| **Sampling: Multiple** | Multiple distinct collections |
| **Sensor passage: Before weighing** | Sensor ➡️ Collection ➡️ Weighing |
| **Sensor passage: After weighing** | Collection ➡️ Weighing ➡️ Sensor |

#### 2. General information
Enter your name, date, sensor and number of samples.

#### 3. Passage times
For each sample, enter the start and end time of passage under the sensor.
Accepted formats: `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
""",
        "meta_workflow_container_title": "### Sampling and sensor passage",
        "meta_workflow_title":  "### Sampling",
        "meta_workflow_label":  "Sampling",
        "meta_wf_standard":     "Single",
        "meta_wf_multi":        "Multiple",
        "meta_wf_standard_caption": "A single material collection",
        "meta_wf_multi_caption": "Multiple material collections for a single characterization",
        "meta_order_label":     "Sensor passage",
        "meta_wfo_order_a":     "Before weighing",
        "meta_wfo_order_b":     "After weighing",
        "meta_order_a_caption": "Sensor ➡️ Collection ➡️ Weighing",
        "meta_order_b_caption": "Collection ➡️ Weighing ➡️ Sensor",
        "meta_info_title":      "### General information",
        "meta_operator_name":   "Name *",
        "meta_operator_ph":     "Enter your name",
        "meta_sensor":          "Sensor name",
        "meta_date":            "Sampling date",
        "meta_nb_samples":      "Number of samples",
        "meta_times_title":     "### Passage times under the WasteFlow sensor",
        "meta_skip_toggle":     "Do not enter collection times now",
        "meta_skip_caption":    "Collection times will not be recorded.",
        "meta_sample_label":    "Sample {n}",
        "meta_start_time":      "Start time *",
        "meta_end_time":        "End time *",
        "meta_recap_title":     "**Collection time summary**",
        "meta_recap_empty":     "No time slots recorded.",
        "meta_recap_sample":    "Sample",
        "meta_recap_date":      "Date",
        "meta_recap_start":     "Start",
        "meta_recap_end":       "End",
        "meta_saved_toast":     "Metadata saved ✓",
        "meta_error_start":     "Sample {n}: invalid start time format ('{raw}'). Accepted formats: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Sample {n}: invalid end time format ('{raw}'). Accepted formats: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Sample {n}: end time must be later than start time.",
        "meta_missing_operator": "Operator name is missing.",
        "meta_missing_sensor": "Sensor is missing.",
        "meta_missing_date": "Test date is missing.",
        "meta_invalid_sample_count": "Invalid sample count.",
        "meta_missing_times": "Sample {n}: start and end times are missing.",
        "meta_missing_start": "Sample {n}: start time is missing.",
        "meta_missing_end": "Sample {n}: end time is missing.",
        "meta_invalid_times": "Sample {n}: invalid collection times.",
        "meta_referenced_samples": "Cannot reduce the sample count: weighings still refer to the removed samples.",
        "meta_draft_warning": "Incomplete draft. Correct these fields before continuing:",
        "report_missing_weighings": "No weighings recorded.",
        "report_invalid_weighings": "One or more weighings have an invalid weight.",
        "report_invalid_samples": "One or more weighings refer to an invalid sample.",
        "export_draft_warning": "Export is unavailable while the report is incomplete:",

        # Tab 2 — Containers
        "cont_guide_title":     "⁉️ Guide — Containers",
        "cont_guide_body":      """
Containers are the bins or boxes used to weigh materials.
Their empty weight (tare) is automatically subtracted to calculate the **net weight**.

**How to add a container:**
1. Enter a clear name (e.g. `Box A`, `Blue Bin 1`)
2. Weigh the empty container and enter its weight in kg
3. Click **✅ Add container**

> If you are not weighing in a container, **leave this tab empty** — the gross weight will equal the net weight.
""",
        "cont_add_title":       "### Add container",
        "cont_list_title":      "### Registered containers",
        "cont_name_label":      "Container identifier",
        "cont_name_ph":         "E.g. Box A, Blue Bin 1...",
        "cont_weight_label":    "Empty weight (kg)",
        "cont_add_btn":         "✅ Add container",
        "cont_empty_info":      "No containers registered. Tare = 0.000 kg by default.",
        "cont_tare_caption":    "Tare: `{tare:.3f} kg`",
        "cont_delete_help":     "Delete this container",
        "cont_used_cannot_delete": "Deletion blocked: {n} weighing(s) use this container.",
        "cont_error_invalid":   "Tare must be a finite non-negative number (0 is allowed).",
        "cont_error_empty":     "Please enter a container identifier.",
        "cont_error_exists":    "This container already exists.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guide — Weighing results",
        "weigh_guide_body":     """
Enter weighings **one material class at a time**.

**For each weighing:**
1. **Sample number(s)** — Single sampling = locked to 1. Multiple = free.
2. **Material class** — Choose from the list or enter a new value.
3. **Container used** — Or *No container* for a direct weighing.
4. **Gross weight (kg)** — Multiple weights separated by spaces (e.g. `12.5 8.3`).
5. Click ✅ **Add weighing**.

---

#### Correcting a mistake
Click **✕** to delete a row or **✏️** to edit it.

> If the **Add weighing** button is greyed out, make sure collection times are
filled in under **Metadata** (or enable the no-times mode).
""",
        "weigh_mode_label":     "Entry mode",
        "weigh_mode_table":     "Table",
        "weigh_pending_next_save": "Unsaved changes: Next will save them before opening Summary.",
        "weigh_mode_manual":    "Manual",
        "weigh_table_title":    "### Table entry",
        "weigh_table_intro": "Table and Manual show the same weighings. Each recorded weighing has its own row, including custom materials. Editing a row corrects the existing weighing. Rows without weights are skipped. For multiple samples, enter sample numbers separated by commas. Use Manual to add another weighing or a photo. Delete weighings from History.",
        "weigh_table_other_entries": "Manual or earlier weighings remain in History; this table does not replace them.",
        "weigh_table_filter": "Find a material",
        "weigh_table_filter_placeholder": "Material name...",
        "weigh_table_shown": "Showing {shown} of {total} materials",
        "weigh_table_no_match": "No material matches this search.",
        "weigh_table_net_label": "Net weight (kg)",
        "weigh_table_no_classes": "No material class configured for this facility.",
        "weigh_table_save_btn": "💾 Save changed rows",
        "weigh_table_preview": "{filled} filled row(s) · {added} to add · {corrected} to correct · Net in table: {net:.3f} kg",
        "weigh_table_recorded_badge": "Entered in table",
        "weigh_table_edit_here": "Edit in table",
        "weigh_table_saved_count": "{added} weighing(s) added, {corrected} corrected.",
        "weigh_table_error_duplicate": "Multiple table weighings exist for “{material}”. Delete the duplicate from History.",
        "weigh_table_error_stale": "The weighing for “{material}” changed. Refresh the table before saving.",
        "weigh_table_error_clear": "“{material}” is already recorded. Delete it from History.",
        "weigh_table_error_sample": "Choose a valid sample for “{material}”.",
        "weigh_table_error_container": "Choose a valid container for “{material}”.",
        "weigh_table_error_weight": "Enter a finite non-negative gross weight for “{material}” (0 is allowed).",
        "weigh_table_error_tare": "Invalid tare for “{material}”. Correct the container.",
        "weigh_table_error_negative": "Negative net weight ({net:.3f} kg) for “{material}”. Check the tare.",
        "weigh_table_saved_toast": "Weighings saved!",
        "weigh_table_error_empty": "Please enter at least one gross weight.",
        "weigh_table_error_no_sample": "Please select a sample number for every weighed row.",
        "weigh_hist_samples":   "Sample(s)",
        "weigh_hist_tare":      "Tare",
        "weigh_hist_gross":     "Gross",
        "weigh_hist_net":       "Net",
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
        "weigh_history_title":  "Weighing history ({n})",
        "weigh_history_empty":  "No weighings recorded.",
        "weigh_edit_help":      "Edit",
        "weigh_delete_help":    "Delete",
        "weigh_disable_warning":"⚠️ Please fill in collection times in the **Metadata** tab first.",
        "weigh_error_format":   "Enter finite non-negative weights (0 is allowed), separated by spaces. Commas or decimal points are accepted.",
        "weigh_error_invalid_tare": "Invalid tare. Correct the container before saving the weighing.",
        "weigh_error_no_sample":"Please select at least one sample.",
        "weigh_error_no_class": "Please select a material class.",
        "weigh_error_negative": "Calculated net weight is negative ({net:.3f} kg). Check the container and entered weights.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Edit weighing",
        "dialog_edit_intro":    "You are editing weighing **n° {n}**.",
        "dialog_edit_save":     "💾 Save",
        "dialog_edit_no_sample":"⚠️ Please select at least one sample.",
        "dialog_edit_negative": "⚠️ Negative net weight ({net:.3f} kg). Check gross weight or tare.",
        "dialog_edit_invalid_weight": "⚠️ Gross weight must be finite and non-negative (0 is allowed).",
        "dialog_edit_invalid_tare": "⚠️ The container tare is invalid.",
        "dialog_edit_toast":    "Weighing updated!",

        # Tab 4 — Summary
        "summ_guide_title":     "⁉️ Guide — Summary",
        "summ_guide_body":      """
This tab shows a complete dashboard once weighings have been entered.

**What you will find here:**
- The **total mass** and a summary table by material class
- A **chart** of the distribution
- A detailed summary **per sample**

**Export:** Click **⬇️ Download** for a ZIP containing Excel, PDF and photos.
The file is also automatically sent to Dropbox.
""",
        "summ_guide_tip":       "✅ Always download the file before starting a new entry.",
        "summ_dashboard_title": "Dashboard",
        "summ_total_metric":    "Total recorded mass",
        "summ_chart_title":     "Distribution by material class",
        "summ_zero_distribution": "Total net mass is 0 kg. There is no distribution to chart; zero weighings remain recorded.",
        "summ_invalid_weights": "{n} weighing(s) have invalid weights. Correct them in Weighing history before exporting.",
        "summ_sample_detail":   "Detail by sample",
        "summ_sample_label":    "Sample {id}",
        "summ_missing_warning": "⚠️ **{n} class(es) with no weighing:**",
        "summ_export_title":    "📤 Close session",
        "summ_dropbox_upload": "Upload the ZIP to Dropbox on download",
        "summ_upload_on_download": "Downloading will also upload the ZIP to Dropbox.",
        "summ_download_only": "The ZIP will only be downloaded.",
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
        "dropbox_upload_failed": "The download is available, but the Dropbox upload failed.",
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

    # ── ES ────────────────────────────────────────────────────────────────────
    "ES": {

        # PDF report
        "pdf_title": "Informe de caracterización",
        "pdf_header_site": "Centro: {facility}  |  Operador: {operator}  |  Fecha: {date}",
        "pdf_header_sensor": "Sensor: {sensor}  |  Muestreo: {sampling}",
        "pdf_header_passage": "Paso del sensor: {passage}",
        "pdf_footer": "WasteFlow App {version}  |  Exportado el {date} a las {time}",
        "pdf_overview": "Indicadores globales",
        "pdf_count": "Número total de pesajes registrados: {count}",
        "pdf_gross": "Masa bruta total: {weight:.3f} kg",
        "pdf_net": "Masa neta total clasificada: {weight:.3f} kg",
        "pdf_present": "Clases de materiales registradas",
        "pdf_absent": "Clases sin datos",
        "pdf_none": "Ninguna",
        "pdf_comment": "Comentario general",
        "pdf_collection": "Intervalos de recogida",
        "pdf_sample": "Muestra",
        "pdf_date": "Fecha",
        "pdf_start": "Hora de inicio",
        "pdf_end": "Hora de fin",
        "pdf_distribution": "Distribución por clase de material",
        "pdf_material": "Clase de material",
        "pdf_net_column": "Peso neto (kg)",
        "pdf_percentage": "% de la masa total",
        "pdf_total": "TOTAL",
        "pdf_chart": "Comparación por clase de material",
        "pdf_axis": "Masa neta (kg)",

        # App-level
        "page_title":           "Resultado de caracterización",
        "app_title":            "Caracterización — {facility}",
        "app_version":          "Versión: {version}",

        # Navigation tabs
        "nav_metadata":         "Metadatos ➡️",
        "nav_containers":       "Contenedores ➡️",
        "nav_weighing":         "Resultados de pesaje ➡️",
        "nav_summary":          "Resumen",

        # Common buttons
        "btn_save":             "💾 Guardar",
        "btn_back":             "⬅️ Volver",
        "btn_next_containers":  "Siguiente paso: Configurar los Contenedores ➡️",
        "btn_next_weighing":    "Siguiente paso: Introducir los Pesajes ➡️",
        "btn_next_summary":     "Siguiente paso: Ver el Resumen ➡️",
        "btn_confirm":          "Confirmar",
        "btn_cancel":           "❌ Cancelar",
        "btn_add":              "✅ Añadir",
        "btn_delete":           "✕",
        "btn_edit":             "✏️",
        "btn_download":         "⬇️ Descargar (Excel + PDF + fotos)",
        "btn_dropbox":          "Guardar en Dropbox",
        "btn_new_session":      "Nueva sesión",
        "btn_new_entry":        "Nueva entrada",
        "btn_logout":           "Cerrar sesión",
        "btn_timing_app":       "⏱Mediciones de tiempo",

        # Sidebar
        "sidebar_config_title": "### Configuración activa",
        "sidebar_operator":     "Operador",
        "sidebar_date":         "Fecha",
        "sidebar_sensor":       "Sensor",
        "sidebar_workflow":     "Muestreo / paso por el sensor",
        "sidebar_weighings":    "Pesajes registrados",
        "sidebar_export_title": "### 💾 Guardar",
        "sidebar_no_data":      "La exportación estará disponible aquí cuando se registre un pesaje.",
        "sidebar_new_session_help": "Reiniciar para una nueva prueba",
        "sidebar_guide_title":  "Guía de uso rápido",
        "sidebar_guide_intro":  "Siga los 4 pasos en orden usando la barra de navegación de arriba.",
        "sidebar_guide_body":   """
**1️⃣ Metadatos** — Muestreo, paso por el sensor, operador y horarios.

**2️⃣ Contenedores** — Pesos de tara de cajas o bidones. Omita si pesa directamente.

**3️⃣ Resultados de pesaje** — Introduzca los pesos brutos clase por clase.

**4️⃣ Resumen** — Panel de control y exportación.
""",
        "sidebar_preview_as":   "Ver como:",
        "sidebar_version":      "Versión: {version}",
        "sidebar_dropbox_upload": "Subir a Dropbox",
        "sidebar_show_tutorials": "Mostrar los tutoriales",
        "sidebar_language": "Idioma",
        "sidebar_timezone": "Zona horaria: {timezone}",
        "sidebar_report_title": "**Informe actual**",
        "sidebar_no_report": "No hay ningún informe en curso.",
        "sidebar_report_details": "{date} · {sensor}",
        "sidebar_weighings_count": "{n} pesaje(s) registrado(s)",
        "sidebar_save_saved_at": "✅ Datos guardados temporalmente en el servidor a las {time}",
        "sidebar_save_saved": "✅ Datos guardados temporalmente en el servidor",
        "sidebar_save_new": "Todavía no hay ninguna copia guardada",
        "sidebar_save_unsaved": "Cambios sin guardar",
        "sidebar_save_failed": "Error al guardar. Los datos pueden perderse si se actualiza la página.",
        "sidebar_save_retry": "Reintentar guardar",
        "sidebar_restore_failed": "No se pudo restaurar la sesión guardada.",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guía — Metadatos",
        "meta_guide_body":      """
Rellene la información de la prueba **antes de empezar a pesar**. Los cambios se guardan automáticamente;
el botón **💾 Guardar** fuerza un guardado manual.

---

#### 1. Muestreo y paso por el sensor

| Opción | Descripción |
|---|---|
| **Muestreo: único** | Una sola muestra |
| **Muestreo: múltiple** | Varias recogidas distintas |
| **Paso por el sensor: antes del pesaje** | Sensor ➡️ Recogida ➡️ Pesaje |
| **Paso por el sensor: después del pesaje** | Recogida ➡️ Pesaje ➡️ Sensor |

#### 2. Información general
Introduzca su nombre, la fecha, el sensor y el número de muestras.

#### 3. Tiempos de paso
Para cada muestra, indique la hora de inicio y fin de paso bajo el sensor.
Formatos aceptados: `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
""",
        "meta_workflow_container_title": "### Muestreo y paso por el sensor",
        "meta_workflow_title":  "### Muestreo",
        "meta_workflow_label":  "Muestreo",
        "meta_wf_standard":     "Único",
        "meta_wf_multi":        "Múltiple",
        "meta_wf_standard_caption": "Una sola recogida de material",
        "meta_wf_multi_caption": "Varias recogidas de material para una sola caracterización",
        "meta_order_label":     "Paso por el sensor",
        "meta_wfo_order_a":     "Antes del pesaje",
        "meta_wfo_order_b":     "Después del pesaje",
        "meta_order_a_caption": "Sensor ➡️ Recogida ➡️ Pesaje",
        "meta_order_b_caption": "Recogida ➡️ Pesaje ➡️ Sensor",
        "meta_info_title":      "### Información general",
        "meta_operator_name":   "Nombre *",
        "meta_operator_ph":     "Introduzca su nombre",
        "meta_sensor":          "Nombre del sensor",
        "meta_date":            "Fecha de muestreo",
        "meta_nb_samples":      "Número de muestras",
        "meta_times_title":     "### Tiempos de paso bajo el sensor WasteFlow",
        "meta_skip_toggle":     "No introducir tiempos de recogida ahora",
        "meta_skip_caption":    "Los tiempos de recogida no se registrarán.",
        "meta_sample_label":    "Muestra {n}",
        "meta_start_time":      "Hora de inicio *",
        "meta_end_time":        "Hora de fin *",
        "meta_recap_title":     "**Resumen de franjas horarias**",
        "meta_recap_empty":     "No hay franjas horarias registradas.",
        "meta_recap_sample":    "Muestra",
        "meta_recap_date":      "Fecha",
        "meta_recap_start":     "Inicio",
        "meta_recap_end":       "Fin",
        "meta_saved_toast":     "Metadatos guardados ✓",
        "meta_error_start":     "Muestra {n}: formato de hora de inicio no válido ('{raw}'). Formatos aceptados: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Muestra {n}: formato de hora de fin no válido ('{raw}'). Formatos aceptados: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Muestra {n}: la hora de fin debe ser posterior a la hora de inicio.",
        "meta_missing_operator": "Falta el nombre del operador.",
        "meta_missing_sensor": "Falta el sensor.",
        "meta_missing_date": "Falta la fecha de la prueba.",
        "meta_invalid_sample_count": "Número de muestras no válido.",
        "meta_missing_times": "Muestra {n}: faltan las horas de inicio y fin.",
        "meta_missing_start": "Muestra {n}: falta la hora de inicio.",
        "meta_missing_end": "Muestra {n}: falta la hora de fin.",
        "meta_invalid_times": "Muestra {n}: tiempos de recogida no válidos.",
        "meta_referenced_samples": "No se puede reducir el número de muestras: hay pesajes que aún usan las muestras eliminadas.",
        "meta_draft_warning": "Borrador incompleto. Corrija estos campos antes de continuar:",
        "report_missing_weighings": "No hay pesajes registrados.",
        "report_invalid_weighings": "Uno o varios pesajes tienen un peso no válido.",
        "report_invalid_samples": "Uno o varios pesajes indican una muestra no válida.",
        "export_draft_warning": "La exportación no está disponible mientras el informe esté incompleto:",

        # Tab 2 — Containers
        "cont_guide_title":     "⁉️ Guía — Contenedores",
        "cont_guide_body":      """
Los contenedores son los bidones o cajas utilizados para pesar los materiales.
Su peso vacío (tara) se resta automáticamente para calcular el **peso neto**.

**Cómo añadir un contenedor:**
1. Introduzca un nombre claro (p. ej. `Caja A`, `Bidón Azul 1`)
2. Pese el contenedor vacío e introduzca su peso en kg
3. Haga clic en **✅ Añadir contenedor**

> Si no pesa en un contenedor, **deje esta pestaña vacía** — el peso bruto será igual al peso neto.
""",
        "cont_add_title":       "### Añadir contenedor",
        "cont_list_title":      "### Contenedores registrados",
        "cont_name_label":      "Identificador del contenedor",
        "cont_name_ph":         "P. ej. Caja A, Bidón Azul 1...",
        "cont_weight_label":    "Peso vacío (kg)",
        "cont_add_btn":         "✅ Añadir contenedor",
        "cont_empty_info":      "No hay contenedores registrados. Tara = 0.000 kg por defecto.",
        "cont_tare_caption":    "Tara: `{tare:.3f} kg`",
        "cont_delete_help":     "Eliminar este contenedor",
        "cont_used_cannot_delete": "Eliminación bloqueada: {n} pesaje(s) usan este contenedor.",
        "cont_error_invalid":   "La tara debe ser un número finito no negativo (se permite 0).",
        "cont_error_empty":     "Por favor, introduzca un identificador de contenedor.",
        "cont_error_exists":    "Este contenedor ya existe.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guía — Resultados de pesaje",
        "weigh_guide_body":     """
Introduzca los pesajes **una clase de material a la vez**.

**Para cada pesaje:**
1. **Número(s) de muestra** — Muestreo único = fijo en 1. Múltiple = libre.
2. **Clase de material** — Elija de la lista o introduzca un nuevo valor.
3. **Contenedor utilizado** — O *Sin contenedor* para un pesaje directo.
4. **Peso bruto (kg)** — Varios pesos separados por espacios (p. ej. `12.5 8.3`).
5. Haga clic en ✅ **Añadir pesaje**.

---

#### Corregir un error
Haga clic en **✕** para eliminar una fila o **✏️** para editarla.

> Si el botón **Añadir pesaje** está desactivado, asegúrese de que los tiempos de
recogida estén rellenos en **Metadatos** (o active el modo sin tiempos).
""",
        "weigh_mode_label":     "Modo de entrada",
        "weigh_mode_table":     "Tabla",
        "weigh_pending_next_save": "Cambios sin guardar: Siguiente los guardará antes de abrir el resumen.",
        "weigh_mode_manual":    "Manual",
        "weigh_table_title":    "### Entrada por tabla",
        "weigh_table_intro": "Tabla y Manual muestran los mismos pesajes. Cada pesaje registrado tiene su propia fila, incluidos los materiales personalizados. Editar una fila corrige el pesaje existente. Las filas sin peso se omiten. Para varias muestras, introduzca los números separados por comas. Use Manual para añadir otro pesaje o una foto. Elimine los pesajes desde el historial.",
        "weigh_table_other_entries": "Los pesajes manuales o anteriores permanecen en el historial; esta tabla no los reemplaza.",
        "weigh_table_filter": "Buscar un material",
        "weigh_table_filter_placeholder": "Nombre del material...",
        "weigh_table_shown": "Se muestran {shown} de {total} materiales",
        "weigh_table_no_match": "Ningún material coincide con la búsqueda.",
        "weigh_table_net_label": "Peso neto (kg)",
        "weigh_table_no_classes": "No hay ninguna clase de material configurada para esta instalación.",
        "weigh_table_save_btn": "💾 Guardar filas modificadas",
        "weigh_table_preview": "{filled} fila(s) con datos · {added} por añadir · {corrected} por corregir · Neto en la tabla: {net:.3f} kg",
        "weigh_table_recorded_badge": "Introducido en la tabla",
        "weigh_table_edit_here": "Editar en la tabla",
        "weigh_table_saved_count": "{added} pesaje(s) añadido(s), {corrected} corregido(s).",
        "weigh_table_error_duplicate": "Hay varios pesajes de tabla para «{material}». Elimine el duplicado desde el historial.",
        "weigh_table_error_stale": "El pesaje de «{material}» cambió. Actualice la tabla antes de guardar.",
        "weigh_table_error_clear": "«{material}» ya está registrado. Elimínelo desde el historial.",
        "weigh_table_error_sample": "Elija una muestra válida para «{material}».",
        "weigh_table_error_container": "Elija un contenedor válido para «{material}».",
        "weigh_table_error_weight": "Introduzca un peso bruto finito no negativo para «{material}» (se permite 0).",
        "weigh_table_error_tare": "Tara no válida para «{material}». Corrija el contenedor.",
        "weigh_table_error_negative": "Peso neto negativo ({net:.3f} kg) para «{material}». Revise la tara.",
        "weigh_table_saved_toast": "¡Pesajes guardados!",
        "weigh_table_error_empty": "Por favor, introduzca al menos un peso bruto.",
        "weigh_table_error_no_sample": "Por favor, seleccione un número de muestra para cada línea pesada.",
        "weigh_hist_samples":   "Muestra(s)",
        "weigh_hist_tare":      "Tara",
        "weigh_hist_gross":     "Bruto",
        "weigh_hist_net":       "Neto",
        "weigh_form_title":     "### 📥 Entrada de pesaje",
        "weigh_sample_label":   "Número(s) de muestra",
        "weigh_sample_ph":      "Elegir muestra...",
        "weigh_class_label":    "Clase de material",
        "weigh_class_ph":       "Elegir...",
        "weigh_container_label":"Contenedor utilizado",
        "weigh_no_container":   "Sin contenedor",
        "weigh_image_label":    "Foto del material (opcional)",
        "weigh_gross_label":    "PESO BRUTO (kg)",
        "weigh_gross_ph":       "P. ej. 12.5 14.2 — separados por espacios",
        "weigh_add_btn":        "✅ Añadir pesaje",
        "weigh_added_toast":    "¡Pesaje añadido!",
        "weigh_obs_title":      "### Observaciones",
        "weigh_obs_ph":         "Añada aquí cualquier comentario sobre la sesión.",
        "weigh_history_title":  "Historial de pesajes ({n})",
        "weigh_history_empty":  "No hay pesajes registrados.",
        "weigh_edit_help":      "Editar",
        "weigh_delete_help":    "Eliminar",
        "weigh_disable_warning":"⚠️ Primero rellene los tiempos de recogida en la pestaña **Metadatos**.",
        "weigh_error_format":   "Introduzca pesos finitos no negativos (se permite 0), separados por espacios. Se acepta coma o punto decimal.",
        "weigh_error_invalid_tare": "Tara no válida. Corrija el contenedor antes de guardar el pesaje.",
        "weigh_error_no_sample":"Por favor, seleccione al menos una muestra.",
        "weigh_error_no_class": "Por favor, seleccione una clase de material.",
        "weigh_error_negative": "El peso neto calculado es negativo ({net:.3f} kg). Compruebe el contenedor y los pesos introducidos.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Editar pesaje",
        "dialog_edit_intro":    "Está editando el pesaje **n° {n}**.",
        "dialog_edit_save":     "💾 Guardar",
        "dialog_edit_no_sample":"⚠️ Por favor, seleccione al menos una muestra.",
        "dialog_edit_negative": "⚠️ Peso neto negativo ({net:.3f} kg). Compruebe el peso bruto o la tara.",
        "dialog_edit_invalid_weight": "⚠️ El peso bruto debe ser finito y no negativo (se permite 0).",
        "dialog_edit_invalid_tare": "⚠️ La tara del contenedor no es válida.",
        "dialog_edit_toast":    "¡Pesaje actualizado!",

        # Tab 4 — Summary
        "summ_guide_title":     "⁉️ Guía — Resumen",
        "summ_guide_body":      """
Esta pestaña muestra un panel de control completo una vez introducidos los pesajes.

**Lo que encontrará aquí:**
- La **masa total** y la tabla resumen por clase de material
- Un **gráfico** de la distribución
- Un resumen detallado **por muestra**

**Exportar:** Haga clic en **⬇️ Descargar** para obtener un ZIP con Excel, PDF y fotos.
El archivo también se envía automáticamente a Dropbox.
""",
        "summ_guide_tip":       "✅ Descargue siempre el archivo antes de iniciar una nueva entrada.",
        "summ_dashboard_title": "Panel de control",
        "summ_total_metric":    "Masa total registrada",
        "summ_chart_title":     "Distribución por clase de material",
        "summ_zero_distribution": "La masa neta total es 0 kg. No hay distribución que mostrar; los pesajes a cero siguen registrados.",
        "summ_invalid_weights": "{n} pesaje(s) tienen pesos no válidos. Corríjalos en el historial antes de exportar.",
        "summ_sample_detail":   "Detalle por muestra",
        "summ_sample_label":    "Muestra {id}",
        "summ_missing_warning": "⚠️ **{n} clase(s) sin pesaje:**",
        "summ_export_title":    "📤 Cierre de sesión",
        "summ_dropbox_upload": "Subir el ZIP a Dropbox al descargarlo",
        "summ_upload_on_download": "La descarga también subirá el ZIP a Dropbox.",
        "summ_download_only": "El ZIP solo se descargará.",
        "summ_no_data":         "No hay pesajes registrados por el momento.",

        # Summary table columns
        "summ_col_class":       "Clase de material",
        "summ_col_net":         "Peso neto",
        "summ_col_pct":         "% de la masa total",

        # Dialog — new session
        "dialog_new_title":     "Nueva entrada",
        "dialog_new_warning":   "Esta acción borrará todos los datos de la sesión actual. Esta operación es irreversible.",

        # Dropbox
        "dropbox_uploading":    "Subiendo a Dropbox...",
        "dropbox_success":      "¡Guardado en Dropbox!",
        "dropbox_upload_failed": "La descarga está disponible, pero falló el envío a Dropbox.",
        "dropbox_error_key":    "Dropbox — clave de configuración faltante: {e}",
        "dropbox_error_auth":   "Dropbox — error de autenticación: {e}",
        "dropbox_error_token":  "Dropbox — token expirado o no válido: {e}",
        "dropbox_error_api":    "Dropbox — error de API ({path}): {e}",
        "dropbox_error_other":  "Dropbox — error inesperado: {e}",

        # Auth
        "auth_wrong":           "Usuario o contraseña incorrectos.",
        "auth_prompt":          "Por favor, inicie sesión para acceder al formulario.",
        "auth_connected_as":    "👤 Conectado como **{name}**",
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
    return translate(get_lang(), key, **kwargs)


def translate(lang: str, key: str, **kwargs) -> str:
    """Translate using an explicit language, including in export threads."""
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
