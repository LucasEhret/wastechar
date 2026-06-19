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

        # App-level
        "page_title":           "Résultat de caractérisation",
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
        "sidebar_config_title": "### 📌 Configuration active",
        "sidebar_operator":     "Opérateur",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Capteur",
        "sidebar_workflow":     "Workflow",
        "sidebar_weighings":    "Pesées enregistrées",
        "sidebar_export_title": "### 💾 Sauvegarde",
        "sidebar_no_data":      "📦 L'export s'activera ici dès qu'une pesée sera enregistrée.",
        "sidebar_new_session_help": "Réinitialiser pour un nouveau test",
        "sidebar_guide_title":  "📖 Guide d'utilisation rapide",
        "sidebar_guide_intro":  "💡 Suivez les 4 étapes dans l'ordre via la barre de navigation en haut.",
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
        "meta_guide_body":      """
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
""",
        "meta_workflow_container_title": "### Comment est collectée la matière ?",
        "meta_workflow_title":  "### ⚙️ Type de workflow",
        "meta_workflow_label":  "Type de workflow",
        "meta_wf_standard":     "Standard",
        "meta_wf_multi":        "Multi-échantillon",
        "meta_wf_standard_caption": "Une seule collecte de matière",
        "meta_wf_multi_caption": "Plusieurs collectes de matière pour une seule caractérisation",
        "meta_order_label":     "Ordre de passage",
        "meta_wfo_order_a":     "Ordre A",
        "meta_wfo_order_b":     "Ordre B",
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
        "meta_recap_title":     "📋 **Récapitulatif des plages horaires**",
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
        "cont_guide_body":      """
Les contenants sont les bacs ou cartons utilisés pour peser les matériaux.
Leur poids à vide (tare) est automatiquement soustrait pour calculer le **poids net**.

**Comment ajouter un contenant :**
1. Saisissez un nom clair (ex : `Carton A`, `Bac Bleu 1`)
2. Pesez le contenant vide et entrez son poids en kg
3. Cliquez sur **✅ Ajouter le contenant**

> Si vous ne pesez pas dans un contenant, **laissez cet onglet vide** — le poids brut sera égal au poids net.
""",
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
        "weigh_guide_body":     """
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
""",
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
        "page_title":           "Characterization result",
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
        "sidebar_config_title": "### 📌 Active configuration",
        "sidebar_operator":     "Operator",
        "sidebar_date":         "Date",
        "sidebar_sensor":       "Sensor",
        "sidebar_workflow":     "Workflow",
        "sidebar_weighings":    "Recorded weighings",
        "sidebar_export_title": "### 💾 Save",
        "sidebar_no_data":      "📦 Export will appear here once a weighing is recorded.",
        "sidebar_new_session_help": "Reset for a new test",
        "sidebar_guide_title":  "📖 Quick user guide",
        "sidebar_guide_intro":  "💡 Follow the 4 steps in order using the navigation bar at the top.",
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
        "meta_guide_body":      """
Fill in the test information **before you start weighing**. Changes are saved automatically;
the **💾 Save** button forces a manual save.

---

#### 1. Workflow type

| Option | Description |
|---|---|
| **Order A** | Sensor measures **before** collection (Sensor ➡️ Collection ➡️ Weighing) |
| **Order B** | Sensor measures **after** weighing (Collection ➡️ Weighing ➡️ Sensor) |
| **Standard** | 1 sample only |
| **Multi-sample** | Multiple distinct collections (for a single characterization) |

#### 2. General information
Enter your name, date, sensor and number of samples.

#### 3. Passage times
For each sample, enter the start and end time of passage under the sensor.
Accepted formats: `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
""",
        "meta_workflow_container_title": "### How is the material collected?",
        "meta_workflow_title":  "### ⚙️ Workflow type",
        "meta_workflow_label":  "Workflow type",
        "meta_wf_standard":     "Standard",
        "meta_wf_multi":        "Multi-sample",
        "meta_wf_standard_caption": "A single material collection",
        "meta_wf_multi_caption": "Multiple material collections for a single characterization",
        "meta_order_label":     "Passage order",
        "meta_wfo_order_a":     "Order A",
        "meta_wfo_order_b":     "Order B",
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
        "meta_recap_title":     "📋 **Collection time summary**",
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
        "cont_guide_body":      """
Containers are the bins or boxes used to weigh materials.
Their empty weight (tare) is automatically subtracted to calculate the **net weight**.

**How to add a container:**
1. Enter a clear name (e.g. `Box A`, `Blue Bin 1`)
2. Weigh the empty container and enter its weight in kg
3. Click **✅ Add container**

> If you are not weighing in a container, **leave this tab empty** — the gross weight will equal the net weight.
""",
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
        "weigh_guide_body":     """
Enter weighings **one material class at a time**.

**For each weighing:**
1. **Sample number(s)** — Standard = locked to 1. Multi = free.
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

    # ── ES ────────────────────────────────────────────────────────────────────
    "ES": {

        # App-level
        "page_title":           "Resultado de caracterización",
        "app_title":            "Caracterización — {facility}",
        "app_version":          "Versión: {version}",
        "dev_mode_warning":     "🛠️ MODO DEV — Dropbox desactivado.",

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
        "btn_dropbox":          "☁️ Guardar en Dropbox",
        "btn_new_session":      "🔄 Nueva sesión",
        "btn_new_entry":        "🆕 Nueva entrada",
        "btn_logout":           "🚪 Cerrar sesión",
        "btn_timing_app":       "⏱️ Mediciones de tiempo",

        # Sidebar
        "sidebar_config_title": "### 📌 Configuración activa",
        "sidebar_operator":     "Operador",
        "sidebar_date":         "Fecha",
        "sidebar_sensor":       "Sensor",
        "sidebar_workflow":     "Flujo de trabajo",
        "sidebar_weighings":    "Pesajes registrados",
        "sidebar_export_title": "### 💾 Guardar",
        "sidebar_no_data":      "📦 La exportación estará disponible aquí cuando se registre un pesaje.",
        "sidebar_new_session_help": "Reiniciar para una nueva prueba",
        "sidebar_guide_title":  "📖 Guía de uso rápido",
        "sidebar_guide_intro":  "💡 Siga los 4 pasos en orden usando la barra de navegación de arriba.",
        "sidebar_guide_body":   """
**1️⃣ Metadatos** — Flujo de trabajo, información del operador, tiempos de paso por el sensor.

**2️⃣ Contenedores** — Pesos de tara de cajas o bidones. Omita si pesa directamente.

**3️⃣ Resultados de pesaje** — Introduzca los pesos brutos clase por clase.

**4️⃣ Resumen** — Panel de control y exportación.
""",
        "sidebar_preview_as":   "Ver como:",
        "sidebar_version":      "Versión: {version}",

        # Tab 1 — Metadata
        "meta_guide_title":     "⁉️ Guía — Metadatos",
        "meta_guide_body":      """
Rellene la información de la prueba **antes de empezar a pesar**. Los cambios se guardan automáticamente;
el botón **💾 Guardar** fuerza un guardado manual.

---

#### 1. Tipo de flujo de trabajo

| Opción | Descripción |
|---|---|
| **Orden A** | El sensor mide **antes** de la recogida (Sensor ➡️ Recogida ➡️ Pesaje) |
| **Orden B** | El sensor mide **después** del pesaje (Recogida ➡️ Pesaje ➡️ Sensor) |
| **Estándar** | 1 solo muestreo |
| **Multi-muestra** | Varias recogidas distintas (para una sola caracterización) |

#### 2. Información general
Introduzca su nombre, la fecha, el sensor y el número de muestras.

#### 3. Tiempos de paso
Para cada muestra, indique la hora de inicio y fin de paso bajo el sensor.
Formatos aceptados: `hh:mm:ss`, `hhmmss`, `hh.mm.ss`.
""",
        "meta_workflow_container_title": "### ¿Cómo se recoge el material?",
        "meta_workflow_title":  "### ⚙️ Tipo de flujo de trabajo",
        "meta_workflow_label":  "Tipo de flujo de trabajo",
        "meta_wf_standard":     "Estándar",
        "meta_wf_multi":        "Multi-muestra",
        "meta_wf_standard_caption": "Una sola recogida de material",
        "meta_wf_multi_caption": "Varias recogidas de material para una sola caracterización",
        "meta_order_label":     "Orden de paso",
        "meta_wfo_order_a":     "Orden A",
        "meta_wfo_order_b":     "Orden B",
        "meta_order_a_caption": "Sensor ➡️ Recogida ➡️ Pesaje",
        "meta_order_b_caption": "Recogida ➡️ Pesaje ➡️ Sensor",
        "meta_info_title":      "### ℹ️ Información general",
        "meta_operator_name":   "Nombre *",
        "meta_operator_ph":     "Introduzca su nombre",
        "meta_sensor":          "Nombre del sensor",
        "meta_date":            "Fecha de muestreo",
        "meta_nb_samples":      "Número de muestras",
        "meta_times_title":     "### 🕒 Tiempos de paso bajo el sensor WasteFlow",
        "meta_skip_toggle":     "No introducir tiempos de recogida ahora",
        "meta_skip_caption":    "Los tiempos de recogida no se registrarán.",
        "meta_sample_label":    "📦 Muestra {n}",
        "meta_start_time":      "Hora de inicio *",
        "meta_end_time":        "Hora de fin *",
        "meta_recap_title":     "📋 **Resumen de franjas horarias**",
        "meta_recap_empty":     "No hay franjas horarias registradas.",
        "meta_recap_sample":    "Muestra",
        "meta_recap_date":      "Fecha",
        "meta_recap_start":     "Inicio",
        "meta_recap_end":       "Fin",
        "meta_saved_toast":     "Metadatos guardados ✓",
        "meta_error_start":     "Muestra {n}: formato de hora de inicio no válido ('{raw}'). Formatos aceptados: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_end":       "Muestra {n}: formato de hora de fin no válido ('{raw}'). Formatos aceptados: hh:mm:ss, hhmmss, hh.mm.ss.",
        "meta_error_time_order":"Muestra {n}: la hora de fin debe ser posterior a la hora de inicio.",

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
        "cont_add_title":       "### 📥 Añadir contenedor",
        "cont_list_title":      "### 📋 Contenedores registrados",
        "cont_name_label":      "Identificador del contenedor",
        "cont_name_ph":         "P. ej. Caja A, Bidón Azul 1...",
        "cont_weight_label":    "Peso vacío (kg)",
        "cont_add_btn":         "✅ Añadir contenedor",
        "cont_empty_info":      "No hay contenedores registrados. Tara = 0.000 kg por defecto.",
        "cont_tare_caption":    "Tara: `{tare:.3f} kg`",
        "cont_delete_help":     "Eliminar este contenedor",
        "cont_error_invalid":   "El peso debe ser un número válido.",
        "cont_error_empty":     "Por favor, introduzca un identificador de contenedor.",
        "cont_error_exists":    "Este contenedor ya existe.",

        # Tab 3 — Weighing
        "weigh_guide_title":    "⁉️ Guía — Resultados de pesaje",
        "weigh_guide_body":     """
Introduzca los pesajes **una clase de material a la vez**.

**Para cada pesaje:**
1. **Número(s) de muestra** — Estándar = fijo en 1. Multi = libre.
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
        "weigh_history_title":  "📋 Historial de pesajes ({n})",
        "weigh_history_empty":  "No hay pesajes registrados.",
        "weigh_edit_help":      "Editar",
        "weigh_delete_help":    "Eliminar",
        "weigh_disable_warning":"⚠️ Primero rellene los tiempos de recogida en la pestaña **Metadatos**.",
        "weigh_error_format":   "Verifique la entrada de pesos brutos. Separe los valores con espacios, usando coma o punto decimal.",
        "weigh_error_no_sample":"Por favor, seleccione al menos una muestra.",
        "weigh_error_no_class": "Por favor, seleccione una clase de material.",
        "weigh_error_negative": "El peso neto calculado es negativo ({net:.3f} kg). Compruebe el contenedor y los pesos introducidos.",

        # Tab 3 — Edit dialog
        "dialog_edit_title":    "✏️ Editar pesaje",
        "dialog_edit_intro":    "Está editando el pesaje **n° {n}**.",
        "dialog_edit_save":     "💾 Guardar",
        "dialog_edit_no_sample":"⚠️ Por favor, seleccione al menos una muestra.",
        "dialog_edit_negative": "⚠️ Peso neto negativo ({net:.3f} kg). Compruebe el peso bruto o la tara.",
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
        "summ_dashboard_title": "📊 Panel de control",
        "summ_total_metric":    "Masa total registrada",
        "summ_chart_title":     "Distribución por clase de material",
        "summ_sample_detail":   "📋 Detalle por muestra",
        "summ_sample_label":    "Muestra {id}",
        "summ_missing_warning": "⚠️ **{n} clase(s) sin pesaje:**",
        "summ_export_title":    "📤 Cierre de sesión",
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
