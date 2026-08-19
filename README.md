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
├── export.py                   ← build_excel_export, build_zip_export, generate_pdf_report, Dropbox upload
├── dialogs.py                  ← st.dialog definitions (new session, edit weighing)
├── styles.css                  ← Custom CSS injected on every page load
├── ui/
│   ├── sidebar.py               ← Sidebar: language, tutorials toggle, session info, export, nav links
│   ├── tab_metadata.py          ← Tab 1: workflow, operator info, collection times
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
streamlit
pandas
matplotlib
openpyxl
dropbox
streamlit-extras
fpdf2
streamlit-authenticator==0.3.3
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

[credentials.usernames.jean]
name     = "Jean"
password = "$2b$12$..."
facility = "TVL"

[credentials.usernames.admin]
name     = "Admin"
password = "$2b$12$..."
facility = "WasteFlow"   # reserved name — grants admin preview mode, see below
```

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

Any user whose `facility` is set to **`WasteFlow`** is treated as an admin (`app.py`, `_is_admin`). Admin accounts get an extra sidebar panel to:

- **Preview as** — switch the active `material_classes`/`sensor_list` to any facility column present in `list_sensors.csv`, without needing separate credentials per facility
- **Toggle Dropbox upload** — uncheck it to exercise the full export flow (Excel/PDF/zip) without pushing test files to production Dropbox (this checkbox is currently the only way to skip the Dropbox upload)

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
    └── Workflow type + order, operator name, date, sensor, number of samples
        └── Collection times per sample (or skip via "Do not enter collection times now")

Tab 2 — Containers
    └── Container name + tare weight (empty box mass)

Tab 3 — Weighing entry (Table mode by default, or Manual mode)
    └── Table  : one editable grid row per material class — sample, container, gross weight
    └── Manual : one-at-a-time form — sample(s), class, container, gross weight(s), optional photo
        └── Net weight = gross − tare
        └── Stored in df_weighings

Tab 4 — Summary
    └── Aggregated table + pie chart + per-sample breakdown + missing-class warnings
        └── Export: ZIP containing Excel + PDF report + photos
            └── Auto-uploaded to Dropbox on download (unless the admin disabled it)
```

---

## Export format

The downloaded ZIP contains:

```
Resultat_{Facility}_{Sensor}_{YYYYMMDD_HHMM}.zip
├── Resultat_{...}.xlsx
│   ├── Global results   (one row per sample × class, % of grand total, TOTAL row)
│   ├── Sample N         (collection times + class table with % of sample total + TOTAL row, per sample)
│   └── Metadata         (facility, operator, date, sensor, workflow, version, timestamp…)
├── Resultat_{...}.pdf   (header, global indicators, collection times, pie chart)
└── images/
    └── {ClassName}.jpg  (one photo per material class, if uploaded via Manual mode)
```

---

## Session persistence (F5 protection)

On every data action (add weighing, add container, save metadata…) the session is serialized to a JSON file under `TEMP_DIR` (`config.py` — the OS temp directory + `wastechar_sessions/`, e.g. `%TEMP%\wastechar_sessions` on Windows), keyed to a UUID stored in the URL query parameter `?session=<uuid>`.

On page load, if the URL contains a known session token and the corresponding file exists, the session is automatically restored. This protects against accidental page refresh during a test.

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
