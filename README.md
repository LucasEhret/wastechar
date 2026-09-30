# WasteChar — Characterization Test Entry Form

A Streamlit application for waste sorting facility operators to record material characterization tests. Captures weighings per material class, computes net masses after tare subtraction, and exports results as Excel + PDF + photos. Supports FR/EN/ES, per-facility material/sensor lists, and an admin preview mode for cross-facility testing.

---

## Project structure

```
wastechar/
├── app.py                      ← Entry point: auth, session init, navigation, tab routing
├── config.py                   ← Constants, APP_VERSION (from git), CSV loader
├── i18n.py                     ← FR/EN/ES translations, t()/set_lang()/get_lang()
├── helpers.py                  ← Pure utility functions (CSS injection, time parsing, weight lookup…)
├── session.py                  ← F5-protection: save/restore/clear session to the OS temp dir
├── data.py                     ← Action callbacks: add_weighing, save_metadata, summarize…
├── table_entry.py              ← Validate and save table rows as new or corrected weighings
├── export.py                   ← build_excel_export, build_zip_export, generate_pdf_report, Dropbox upload
├── dialogs.py                  ← st.dialog definitions (new session, edit weighing)
├── styles.css                  ← Custom CSS injected on every page load
├── ui/
│   ├── export_controls.py       ← Generate and download a ZIP in one click from Summary
│   ├── save_status.py           ← Sidebar save status and retry control
│   ├── sidebar.py               ← Sidebar: identity, report status, language, and preview settings
│   ├── tab_metadata.py          ← Tab 1: sampling, sensor passage, operator info, collection times
│   ├── tab_containers.py        ← Tab 2: container (tare) management
│   ├── tab_weighing.py          ← Tab 3: weighing entry (table & manual modes) and history
│   └── tab_summary.py           ← Tab 4: dashboard, charts, export & reset
├── "1. run_app.bat"             ← Windows double-click launcher (streamlit run app.py)
└── .streamlit/
    ├── config.toml              ← Theme (WasteFlow brand colors)
    ├── secrets.toml             ← Credentials (local only, never committed)
    ├── images/                  ← Logo, favicon, in-app tutorial screenshots
    └── ressources/
        ├── list_classes.csv     ← Material classes, one column per facility
        └── list_sensors.csv     ← Sensor names, one column per facility
```

---

## Prerequisites

- Python 3.11+
- A Dropbox app with a refresh token
- A Streamlit Cloud account (for deployment)

Install dependencies:

```bash
pip install -r requirements.txt
```

**`requirements.txt`** currently includes:

```
streamlit>=1.53
pandas
matplotlib
openpyxl
dropbox
streamlit-extras
fpdf2
streamlit-authenticator==0.3.3
tzdata
```

---

## Local setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd wastechar
```

### 2. Create `.streamlit/secrets.toml`

This file is **gitignored** and must never be committed. Create it manually:

```toml
DROPBOX_APP_KEY          = "your_app_key"
DROPBOX_APP_SECRET       = "your_app_secret"
DROPBOX_REFRESH_TOKEN    = "your_refresh_token"
DROPBOX_DESTINATION_PATH = "/WasteChar/exports/"

[cookie]
name         = "wastechar_auth"
key          = "a_long_random_secret_string"
expiry_days  = 1

[credentials.usernames.alice]
name     = "Alice"
password = "$2b$12$..."   # bcrypt hash — see below
facility = "Veolia Bonneuil"
timezone = "Europe/Paris"

[credentials.usernames.jean]
name     = "Jean"
password = "$2b$12$..."
facility = "TVL"
timezone = "Europe/Zurich"

[credentials.usernames.admin]
name     = "Admin"
password = "$2b$12$..."
facility = "WasteFlow"   # reserved name — grants admin preview mode, see below
timezone = "Europe/Zurich"
```

An administrator sets each account's `timezone` in this file (or in the Streamlit Cloud secrets dashboard). Use an IANA time zone such as `Europe/Paris` or `America/New_York`; daylight-saving changes are applied automatically. Accounts without this setting use `Europe/Zurich`. The setting belongs to the logged-in account, including when an admin previews another facility. Invalid time-zone names stop the app for that account instead of silently using the server clock.

To generate a bcrypt password hash:

```python
import bcrypt
print(bcrypt.hashpw("my_password".encode(), bcrypt.gensalt()).decode())
```

### 3. `APP_VERSION`

`APP_VERSION` is derived automatically at import time from `git describe --tags --always` (falling back to `dev-<short-sha>`, or `1.0.0-unknown` if git metadata isn't available) — no manual version bump needed.

### 4. Run locally

```bash
streamlit run app.py
```

On Windows you can also double-click **`1. run_app.bat`**.

---

## CSV configuration files

Both CSV files use **semicolons as separators** and have **one column per facility**. The column header must exactly match the `facility` value in `secrets.toml`.

### `list_classes.csv` — Material classes

```
WasteFlow;Veolia Bonneuil;TVL;Ecoembes
Combination;Bois <300mm;Acier;
Metal;Bois >300mm;Alu;
Plastic_LDPE;Papiers;Petit ALU;
```

### `list_sensors.csv` — Sensor names

```
WasteFlow;Veolia Bonneuil;TVL;Ecoembes
vebo-as1-mc3;vebo-as1-mc3;tvlo-carac-room;pera-n2-zrr1-replacement
tvlo-mc3-n26;;tvlo-mg2-os7;pera-n2-zrr1
```

Empty cells mean that class/sensor is not used at that facility. The `WasteFlow` column is the admin's own facility and is also the default target of the preview selector (see below), so it should be kept populated.

---

## Adding a new facility

1. Add a column to `list_classes.csv` and `list_sensors.csv` with the facility name as the header
2. Fill in the relevant rows for that facility
3. Add a user entry in `secrets.toml` (local) and in the Streamlit Cloud secrets dashboard (production), with `facility` matching the column header exactly

---

## Adding a new user

Generate a bcrypt hash for their password, then add to **both**:

- `.streamlit/secrets.toml` (local)
- Streamlit Cloud dashboard → App settings → Secrets (production)

```toml
[credentials.usernames.newuser]
name     = "New User"
password = "$2b$12$..."
facility = "Veolia Bonneuil"
```

---

## Admin / multi-facility preview mode

Any user whose `facility` is set to **`WasteFlow`** is treated as an admin (`app.py`, `_is_admin`). Admin accounts can:

- **Preview as** — switch the active `material_classes`/`sensor_list` to any facility column present in `list_sensors.csv`, without needing separate credentials per facility
- **Toggle Dropbox upload on Summary** — uncheck it to exercise the full export flow (Excel/PDF/zip) without pushing test files to production Dropbox. The choice persists when navigating between screens.

Non-admin users only ever see their own facility's data — this switcher is invisible to them.

---

## Multi-language support

The UI is fully translated via `i18n.py` (FR default, plus EN and ES). Users pick their language from the sidebar; the choice lives in `st.session_state["lang"]` for the duration of the session.

- `t("some_key", **placeholders)` looks up the string for the active language, falls back to French, then to the raw key if missing everywhere
- A consistency check runs at import time and emits a warning for any key present in one language but missing in another
- Adding a new string: add the key under the same name in all three language blocks in `i18n.py`

The sidebar also has a **"Show tutorials"** toggle (`show_tutorials` in session state) that shows/hides the ⁉️ guide panel at the top of each tab.

---

## Deployment on Streamlit Cloud

1. Push the repository to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`)
2. Create a new app on [share.streamlit.io](https://share.streamlit.io), pointing to `app.py`
3. In **App settings → Secrets**, paste the full content of your local `secrets.toml`

---

## Data flow

```
Operator logs in
    └── Facility resolved from credentials (or from the admin preview selector)
        └── Material classes + sensors loaded from CSV

Tab 1 — Metadata
    └── Sampling (Single / Multiple) + Sensor passage (Before / After weighing), operator name, date, sensor, number of samples
        └── Collection times per sample (or skip via "Do not enter collection times now")

Tab 2 — Containers
    └── Container name + tare weight (empty box mass)

Tab 3 — Weighing entry (Table mode by default, or Manual mode)
    └── Table  : one editable grid row per material class — save again to correct its weighing
    └── Manual : one-at-a-time form — sample(s), class, container, gross weight(s), optional photo
        └── Net weight = gross − tare
        └── Stored in df_weighings

Tab 4 — Summary
    └── Aggregated table + pie chart + per-sample breakdown + missing-class warnings
        └── Download the ZIP containing Excel + PDF report + photos in one click
            └── Auto-uploaded to Dropbox on download (unless the admin disabled it)
```

---

Gross and tare weights must be finite, non-negative numbers. An explicit 0 kg weighing is valid; gross weight below tare is rejected. Reports with only zero net weights show 0% totals and omit the pie chart.

---

## Export format

The ZIP is generated only when **Download** is clicked on the Summary tab. The download callable uses a snapshot of the current report; ordinary screen rendering does not generate exports. The downloaded ZIP contains:

Metadata can be saved as an incomplete draft, with missing collection times kept blank. A typed `00:00` is a valid midnight time. The Metadata tab's **Next** button requires complete metadata and a successful save. Weighing and export remain unavailable until the saved metadata is complete; export also checks the saved weighings and their sample numbers.

Weighings reference sample numbers; collection times are read from the current sample records when exporting. Editing a sample's times therefore updates the report without changing each weighing. The sample count cannot be reduced while weighings reference samples that would be removed.

Each weighing stores the tare used to calculate its net weight. Older sessions infer that tare from their recorded gross and net weights. A container used by any weighing cannot be deleted; remove or correct those weighings first.

Every weighing has a stable ID, including records restored from older sessions. Table entry uses that ID to correct a saved weighing in place; a 10 kg row changed to 12 kg remains one 12 kg weighing. Existing duplicate table rows are flagged for review in the weighing history.

```
Resultat_{Facility}_{Sensor}_{YYYYMMDD_HHMM±HHMM}.zip
├── Resultat_{...}.xlsx
│   ├── Global results   (one row per sample × class, % of grand total, TOTAL row)
│   ├── Sample N         (collection times + class table with % of sample total + TOTAL row, per sample)
│   └── Metadata         (facility, operator, date, sensor, sampling, sensor passage, version, timestamp…)
├── Resultat_{...}.pdf   (header, global indicators, collection times, pie chart)
└── images/
    └── {ClassName}.jpg  (one photo per material class, if uploaded via Manual mode)
```

---

## Session persistence (F5 protection)

On every data action (add weighing, add container, save metadata…) the session is serialized to a JSON file under `TEMP_DIR` (`config.py` — the OS temp directory + `wastechar_sessions/`, e.g. `%TEMP%\wastechar_sessions` on Windows), keyed to a UUID stored in the URL query parameter `?session=<uuid>`.

On page load, a session is restored only when its UUID token is valid and the saved username and facility match the authenticated user and active facility. Invalid or unauthorized URLs receive a fresh token. Legacy files without an owner/facility binding cannot be restored; this protects other users' reports while retaining refresh recovery for newly saved sessions.

The sidebar shows when the session data was last saved on the server. If a write fails, it shows an error and a retry button. Invalid metadata stays marked as unsaved until corrected. Photos are not included in the refresh backup; the sidebar warns about this when photos are present.

The session file is deleted when the operator clicks **🆕 Nouvelle saisie / New entry** to start a new test.

> ⚠️ Session files live in the server's temp directory and are lost if the Streamlit Cloud server restarts (cold start after long inactivity). For long-term backup, use the Dropbox export.

---

## Architecture notes

- **`st.session_state` as shared context.** `facility_name`, `material_classes`, `sensor_list`, `is_admin`, `all_facilities`, and `lang` are resolved in `app.py` after authentication and stored in session state. All modules read from session state rather than importing module-level globals, which correctly handles multi-user deployments where different users have different facilities in the same server process.

- **Dependency hierarchy** (no circular imports):
  ```
  config → i18n → helpers → session → data → export → dialogs → ui/* → app
  ```

- **`APP_VERSION`** is computed once at import time from git (`config._get_app_version`), so it stays accurate across environments without manual edits.

- **CSS** is centralized in `styles.css` and injected once per page load via `helpers.inject_css()`.
