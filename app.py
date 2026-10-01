from ui.report_state import app_state, initialize_report, detach_report
from report import Report
import streamlit as st
import streamlit_authenticator as stauth

from config import (
    APP_VERSION, TEMP_DIR,
    MATERIALS_FILE, SENSORS_FILE,
    WORKFLOW_MAP, ORDER_MAP,
    load_column_from_csv,
)
from session import save_session, restore_session, clear_session, prepare_session_token
from helpers import inject_css
from ui.sidebar import render_sidebar
from ui.tab_metadata import render_tab_metadata
from ui.tab_containers import render_tab_containers
from ui.tab_weighing import render_tab_weighing
from ui.tab_summary import render_tab_summary
from ui.navigation import sync_navigation
from i18n import t
from time_utils import account_timezone, local_today


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

if app_state.get("authentication_status") is False:
    st.error(t("auth_wrong"))
    st.stop()
elif app_state.get("authentication_status") is None:
    st.info(t("auth_prompt"))
    st.stop()

# Resolve facility and lists from logged-in user
_username     = app_state["username"]
_account      = st.secrets["credentials"]["usernames"][_username]
_facility     = _account["facility"]
try:
    _timezone_name = account_timezone(_account.get("timezone")).key
except ValueError as exc:
    st.error(str(exc))
    st.stop()
_is_admin     = _facility == "WasteFlow"
_all_facils: list[str] = []

if _is_admin:
    import pandas as _pd
    _all_facils = _pd.read_csv(SENSORS_FILE, encoding="utf-8", sep=";", nrows=0).columns.tolist()
    if "_preview_facility" not in app_state:
        app_state["_preview_facility"] = "WasteFlow"
    _facility = app_state["_preview_facility"]

# Store in session state so all modules can access
app_state["facility_name"]   = _facility
app_state["user_timezone"]   = _timezone_name
app_state["is_admin"]        = _is_admin
app_state["all_facilities"]  = _all_facils
app_state["material_classes"] = load_column_from_csv(MATERIALS_FILE, _facility)
app_state["sensor_list"]      = load_column_from_csv(SENSORS_FILE,   _facility)


# ── DEFAULTS ──────────────────────────────────────────────────────────────────
sensor_list = app_state["sensor_list"]

DEFAULTS: dict = {
    **Report(
        facility=_facility, timezone=_timezone_name,
        material_classes=app_state["material_classes"],
        test_date=local_today(_timezone_name),
        sensor=sensor_list[0] if sensor_list else "",
    ).to_state(),
    "metadata_error": "", "container_error": "", "weighing_error": "",
    "image_uploader_key": 0, "show_tutorials": True, "weighing_version": 0,
}
_identity = (_username, _facility)
if app_state.get("_session_identity") not in (None, _identity):
    detach_report()
    for key in (*DEFAULTS, "session_restored", "_save_status", "_last_saved_at",
                "_operator_name", "_sensor_name", "_nb_sample",
                "_test_date", "workflow_type_seg", "workflow_order_seg", "skip_collect_times",
                "_skip_collect_times_value", "sample_nb", "container_used",
                "container_name", "container_weight", "weighing_table_filter", "_table_draft",
                "global_comment"):
        app_state.pop(key, None)
    for key in list(app_state):
        if key.startswith(("weighing_table_", "gross_weight_", "material_class_",
                           "weighing_image_", "_start_", "_end_")):
            app_state.pop(key, None)
app_state["_session_identity"] = _identity

for key, value in DEFAULTS.items():
    if key not in app_state:
        app_state[key] = value

initialize_report()

# The "skip collect times" toggle only renders on the Metadata tab, so Streamlit
# purges its widget-bound session_state key whenever another tab is shown. Re-seed
# it from the durable copy (kept in sync by _on_skip_collect_times_change) instead
# of resetting the user's choice back to False every time they navigate away.
if "skip_collect_times" not in app_state:
    app_state["skip_collect_times"] = app_state.get("_skip_collect_times_value", False)


# ── SESSION PERSISTENCE ───────────────────────────────────────────────────────
prepare_session_token()

if "session_restored" not in app_state:
    restore_session()
    app_state["session_restored"] = True


# ── TITLE & NAVIGATION ────────────────────────────────────────────────────────
st.title(t("app_title", facility=_facility))

TAB_LABELS = {0: t("nav_metadata"), 1: t("nav_containers"), 2: t("nav_weighing"), 3: t("nav_summary")}
TABS = list(TAB_LABELS)

if "step_index" not in app_state:
    app_state.step_index = 0

app_state["seg_nav"] = app_state.step_index
st.segmented_control(
    "Navigation",
    options=TABS,
    format_func=TAB_LABELS.__getitem__,
    key="seg_nav",
    label_visibility="collapsed",
    on_change=sync_navigation,
    width="stretch"
)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
render_sidebar(authenticator)


# ── TAB ROUTING ───────────────────────────────────────────────────────────────
step = app_state.step_index

if step == 0:
    render_tab_metadata()
elif step == 1:
    render_tab_containers()
elif step == 2:
    render_tab_weighing()
elif step == 3:
    render_tab_summary()
