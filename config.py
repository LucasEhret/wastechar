import subprocess
import tempfile
import datetime as dt
import pandas as pd
import streamlit as st
from pathlib import Path

# ── DEPLOYMENT ────────────────────────────────────────────────────────────────
DEV_MODE = False

# ── FILE PATHS ────────────────────────────────────────────────────────────────
MATERIALS_FILE = ".streamlit/ressources/list_classes.csv"
SENSORS_FILE   = ".streamlit/ressources/list_sensors.csv"

# ── WORKFLOW MAPS ─────────────────────────────────────────────────────────────
WORKFLOW_MAP = {0: "Standard", 1: "Multi-échantillon"}
ORDER_MAP    = {0: "A", 1: "B"}

# ── TEMP STORAGE ──────────────────────────────────────────────────────────────
TEMP_DIR = Path(tempfile.gettempdir()) / "wastechar_sessions"
TEMP_DIR.mkdir(exist_ok=True)

# ── APP VERSION ───────────────────────────────────────────────────────────────
def _get_app_version() -> str:
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--always"]
        ).strip().decode("utf-8")
    except Exception:
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"]
            ).strip().decode("utf-8")
            return f"dev-{sha}"
        except Exception:
            return "1.0.0-unknown"

APP_VERSION = f"1.0.0+{_get_app_version()}"


# ── CSV LOADER ────────────────────────────────────────────────────────────────
@st.cache_data
def load_column_from_csv(csv_file: str, facility: str) -> list[str]:
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";")
    if facility not in df.columns:
        st.error(
            f"Le fichier '{csv_file}' ne contient pas de colonne '{facility}'. "
            f"Colonnes disponibles : {', '.join(df.columns.tolist())}"
        )
        st.stop()
    return (
        df[facility]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .tolist()
    )
