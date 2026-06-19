import uuid
import datetime as dt

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from config import (
    APP_VERSION, DEV_MODE, TEMP_DIR,
    MATERIALS_FILE, SENSORS_FILE,
    WORKFLOW_MAP, ORDER_MAP,
    load_column_from_csv,
)
from session import save_session, restore_session, clear_session
from helpers import inject_css
from ui.sidebar import render_sidebar
from ui.tab_metadata import render_tab_metadata
from ui.tab_containers import render_tab_containers
from ui.tab_weighing import render_tab_weighing
from ui.tab_summary import render_tab_summary
from i18n import t


# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=t("page_title"),
    page_icon=".streamlit/images/eye-wasteflow.png",
    layout="centered",
)

inject_css()


# ── AUTHENTICATION ────────────────────────────────────────────────────────────
_credentials = {
    "usernames": {
        uname: {"name": data["name"], "password": data["password"]}
        for uname, data in st.secrets["credentials"]["usernames"].items()
    }
}

authenticator = stauth.Authenticate(
    _credentials,
    st.secrets["cookie"]["name"],
    st.secrets["cookie"]["key"],
    cookie_expiry_days=st.secrets["cookie"]["expiry_days"],
)

authenticator.login(location="main")

if st.session_state.get("authentication_status") is False:
    st.error(t("auth_wrong"))
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.info(t("auth_prompt"))
    st.stop()

# Resolve facility and lists from logged-in user
_username     = st.session_state["username"]
_facility     = st.secrets["credentials"]["usernames"][_username]["facility"]
_is_admin     = _facility == "WasteFlow"
_all_facils: list[str] = []

if _is_admin:
    import pandas as _pd
    _all_facils = _pd.read_csv(SENSORS_FILE, encoding="utf-8", sep=";", nrows=0).columns.tolist()
    if "_preview_facility" not in st.session_state:
        st.session_state["_preview_facility"] = "WasteFlow"
    _facility = st.session_state["_preview_facility"]

# Store in session state so all modules can access
st.session_state["facility_name"]   = _facility
st.session_state["is_admin"]        = _is_admin
st.session_state["all_facilities"]  = _all_facils
st.session_state["material_classes"] = load_column_from_csv(MATERIALS_FILE, _facility)
st.session_state["sensor_list"]      = load_column_from_csv(SENSORS_FILE,   _facility)


# ── DEFAULTS ──────────────────────────────────────────────────────────────────
sensor_list = st.session_state["sensor_list"]

DEFAULTS: dict = {
    "metadata_error":      "",
    "container_error":     "",
    "weighing_error":      "",
    "saved_operator_name": "",
    "saved_test_date":     dt.date.today(),
    "saved_sensor_name":   sensor_list[0] if sensor_list else "",
    "saved_nb_sample":     1,
    "image_uploader_key":  0,
    "skip_collect_times":  False,
    "global_comment":      "",
    "saved_workflow":      0,
    "weighing_version":    0,
    "saved_workflow_order": 0,
    "df_containers": pd.DataFrame({
        "Contenant":    pd.Series(dtype="str"),
        "Poids à vide": pd.Series(dtype="float"),
    }),
    "df_collect_times": pd.DataFrame({
        "Echantillon":    pd.Series(dtype="int"),
        "Date":           pd.Series(dtype="object"),
        "Heure de début": pd.Series(dtype="str"),
        "Heure de fin":   pd.Series(dtype="str"),
    }),
    "df_weighings": pd.DataFrame({
        "N° échantillon":     pd.Series(dtype="str"),
        "Début":              pd.Series(dtype="object"),
        "Fin":                pd.Series(dtype="object"),
        "Classe de matériau": pd.Series(dtype="str"),
        "Contenant utilisé":  pd.Series(dtype="str"),
        "Poids brut":         pd.Series(dtype="float"),
        "Poids net":          pd.Series(dtype="float"),
    }),
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── SESSION PERSISTENCE ───────────────────────────────────────────────────────
if "session" not in st.query_params:
    st.query_params["session"] = uuid.uuid4().hex

if "session_restored" not in st.session_state:
    restore_session()
    st.session_state["session_restored"] = True


# ── TITLE & NAVIGATION ────────────────────────────────────────────────────────
st.title(t("app_title", facility=_facility))

TABS = [t("nav_metadata"),t("nav_containers"),t("nav_weighing"),t("nav_summary"),]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0

def _sync_nav():
    st.session_state.step_index = TABS.index(st.session_state.seg_nav)

st.session_state["seg_nav"] = TABS[st.session_state.step_index]
st.segmented_control(
    "Navigation",
    options=TABS,
    key="seg_nav",
    label_visibility="collapsed",
    on_change=_sync_nav,
    width="stretch"
)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
render_sidebar(authenticator)


# ── TAB ROUTING ───────────────────────────────────────────────────────────────
step = st.session_state.step_index

if step == 0:
    render_tab_metadata()
elif step == 1:
    render_tab_containers()
elif step == 2:
    render_tab_weighing()
elif step == 3:
    render_tab_summary()
