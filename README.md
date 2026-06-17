# WasteChar — Characterization Test Entry Form

A Streamlit application for waste sorting facility operators to record material characterization tests. Captures weighings per material class, computes net masses after tare subtraction, and exports results as Excel + PDF + photos.

---

## Project structure

```
wastechar/
├── app.py                      ← Entry point: auth, session init, navigation, tab routing
├── config.py                   ← Constants, APP_VERSION, CSV loader
├── helpers.py                  ← Pure utility functions (time parsing, weight lookup…)
├── session.py                  ← F5-protection: save/restore/clear session to /tmp/
├── data.py                     ← Action callbacks: add_weighing, save_metadata, summarize…
├── export.py                   ← build_excel_export, build_zip_export, generate_pdf_report, Dropbox upload
├── dialogs.py                  ← st.dialog definitions (new session, edit weighing)
├── ui/
│   ├── sidebar.py              ← Sidebar: session info, export, navigation links
│   ├── tab_metadata.py         ← Tab 1: workflow, operator info, collection times
│   ├── tab_containers.py       ← Tab 2: container (tare) management
│   ├── tab_weighing.py         ← Tab 3: weighing entry form and history
│   └── tab_summary.py          ← Tab 4: dashboard, charts, export & reset
└── .streamlit/
    ├── config.toml             ← Theme (WasteFlow brand colors)
    ├── secrets.toml            ← Credentials (local only, never committed)
    └── ressources/
        ├── list_classes.csv    ← Material classes, one column per facility
        └── list_sensors.csv    ← Sensor names, one column per facility
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

**`requirements.txt`** should include at minimum:

```
streamlit
streamlit-authenticator==0.3.3
streamlit-extras
pandas
openpyxl
matplotlib
fpdf2
dropbox
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
DROPBOX_APP_KEY        = "your_app_key"
DROPBOX_APP_SECRET     = "your_app_secret"
DROPBOX_REFRESH_TOKEN  = "your_refresh_token"
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
```

To generate a bcrypt password hash:

```python
import bcrypt
print(bcrypt.hashpw("my_password".encode(), bcrypt.gensalt()).decode())
```

### 3. Configure `DEV_MODE`

In `config.py`, set `DEV_MODE = True` while developing locally. This disables all Dropbox uploads so you can run the app without network access.

```python
DEV_MODE = True   # ← local development
DEV_MODE = False  # ← production
```

### 4. Run locally

```bash
streamlit run app.py
```

---

## CSV configuration files

Both CSV files use **semicolons as separators** and have **one column per facility**. The column header must exactly match the `facility` value in `secrets.toml`.

### `list_classes.csv` — Material classes

```
Veolia Bonneuil;TVL;Ecoembes
Acier;Acier;Acero
Aluminium;Aluminium;Aluminio
Carton;;Cartón
PET bouteille;PET bouteille;
```

Empty cells mean that class is not used at that facility.

### `list_sensors.csv` — Sensor names

```
Veolia Bonneuil;TVL;Ecoembes
vebo-as1-mc3;tvlo-mc3-n26;pera-n2-zrr1
;tvlo-mg2-os7;
```

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

## Deployment on Streamlit Cloud

1. Push the repository to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`)
2. Create a new app on [share.streamlit.io](https://share.streamlit.io), pointing to `app.py`
3. In **App settings → Secrets**, paste the full content of your local `secrets.toml`
4. Set `DEV_MODE = False` in `config.py` before pushing

---

## Data flow

```
Operator logs in
    └── Facility resolved from credentials
        └── Material classes + sensors loaded from CSV

Tab 1 — Metadata
    └── Workflow type, operator name, date, sensor, collection times

Tab 2 — Containers
    └── Container name + tare weight (empty box mass)

Tab 3 — Weighing entry
    └── Sample(s) + material class + container + gross weight(s)
        └── Net weight = gross − tare
        └── Stored in df_weighings

Tab 4 — Summary
    └── Aggregated table + pie chart + per-sample breakdown
        └── Export: ZIP containing Excel + PDF report + photos
            └── Auto-uploaded to Dropbox on download
```

---

## Export format

The downloaded ZIP contains:

```
Resultat_{Facility}_{Sensor}_{YYYYMMDD_HHMM}.zip
├── Resultat_{...}.xlsx
│   ├── Global results   (one row per sample × class, % of grand total, TOTAL row)
│   ├── Sample N         (collection times + class table + TOTAL row, per sample)
│   └── Metadata         (operator, date, sensor, workflow, version, timestamp…)
├── Resultat_{...}.pdf   (header, global indicators, collection times, pie chart)
└── images/
    └── {ClassName}.jpg  (one photo per material class, if uploaded)
```

---

## Session persistence (F5 protection)

On every data action (add weighing, add container, save metadata…) the session is serialized to a JSON file in the system temp directory, keyed to a UUID stored in the URL query parameter `?session=<uuid>`.

On page load, if the URL contains a known session token and the corresponding file exists, the session is automatically restored. This protects against accidental page refresh during a test.

The session file is deleted when the operator clicks **🆕 Nouvelle saisie** to start a new test.

> ⚠️ Session files live in `/tmp/` and are lost if the Streamlit Cloud server restarts (cold start after long inactivity). For long-term backup, use the Dropbox export.

---

## Architecture notes

- **`st.session_state` as shared context.** `FACILITY_NAME`, `material_classes`, and `sensor_list` are resolved in `app.py` after authentication and stored in session state. All modules read from session state rather than importing module-level globals, which correctly handles multi-user deployments where different users have different facilities in the same server process.

- **Dependency hierarchy** (no circular imports):
  ```
  config → helpers → session → data → export → dialogs → ui/* → app
  ```

- **`DEV_MODE`** in `config.py` disables all Dropbox operations. No other code change is needed to switch between local and production.
