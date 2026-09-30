import datetime as dt
from dataclasses import dataclass
import pandas as pd
import streamlit as st

from helpers import (
    get_container_weight,
    parse_time_str,
    sample_ids_from_label,
    _clean_time_widget_keys,
)
from i18n import t
from session import mark_session_unsaved, save_session
from report_validation import metadata_errors
from weights import gross_weights, net_weight as calculate_net_weight, nonnegative_weight
from weighing_identity import WEIGHING_ID_COLUMN, new_weighing_id


# ── METADATA ──────────────────────────────────────────────────────────────────
def init_metadata_widget_state() -> None:
    if "_operator_name" not in st.session_state:
        st.session_state["_operator_name"] = st.session_state["saved_operator_name"]
    if "_test_date" not in st.session_state:
        st.session_state["_test_date"] = st.session_state["saved_test_date"]
    if "_sensor_name" not in st.session_state:
        st.session_state["_sensor_name"] = st.session_state["saved_sensor_name"]
    if "_nb_sample" not in st.session_state:
        st.session_state["_nb_sample"] = st.session_state["saved_nb_sample"]

    nb_sample = int(st.session_state["_nb_sample"])
    existing  = st.session_state["df_collect_times"]

    for i in range(1, nb_sample + 1):
        saved_start, saved_end = "", ""
        if not existing.empty and "Echantillon" in existing.columns:
            row = existing.loc[existing["Echantillon"] == i]
            if not row.empty:
                s = row.iloc[0]["Heure de début"]
                e = row.iloc[0]["Heure de fin"]
                saved_start = s or ""
                saved_end   = e or ""
        for suffix, val in ((f"_start_{i}", saved_start), (f"_end_{i}", saved_end)):
            if suffix not in st.session_state:
                st.session_state[suffix] = val


@dataclass(frozen=True)
class MetadataSaveResult:
    saved: bool
    errors: tuple[str, ...]

    @property
    def can_progress(self) -> bool:
        return self.saved and not self.errors


def save_metadata() -> MetadataSaveResult:
    nb_sample = st.session_state["_nb_sample"]
    if nb_sample < st.session_state.get("saved_nb_sample", 1):
        try:
            referenced = {
                sample
                for label in st.session_state["df_weighings"]["N° échantillon"]
                for sample in sample_ids_from_label(label)
            }
        except ValueError:
            referenced = {nb_sample + 1}
        if any(sample > nb_sample for sample in referenced):
            message = t("meta_referenced_samples")
            st.session_state["metadata_error"] = message
            mark_session_unsaved()
            return MetadataSaveResult(False, (message,))
    rows = []
    for i in range(1, nb_sample + 1):
        s_date    = st.session_state["_test_date"]
        start_raw = (st.session_state.get(f"_start_{i}") or "").strip()
        end_raw   = (st.session_state.get(f"_end_{i}")   or "").strip()

        try:
            t_s = parse_time_str(start_raw) if start_raw else None
        except ValueError:
            st.session_state["metadata_error"] = t("meta_error_start", n=i, raw=start_raw)
            mark_session_unsaved()
            return MetadataSaveResult(False, (st.session_state["metadata_error"],))
        try:
            t_e = parse_time_str(end_raw) if end_raw else None
        except ValueError:
            st.session_state["metadata_error"] = t("meta_error_end", n=i, raw=end_raw)
            mark_session_unsaved()
            return MetadataSaveResult(False, (st.session_state["metadata_error"],))

        rows.append({
            "Echantillon":    i,
            "Date":           s_date,
            "Heure de début": t_s.isoformat() if t_s is not None else "",
            "Heure de fin":   t_e.isoformat() if t_e is not None else "",
        })

    st.session_state["df_collect_times"]    = pd.DataFrame(rows)
    st.session_state["saved_sensor_name"]   = st.session_state["_sensor_name"]
    st.session_state["saved_nb_sample"]     = nb_sample
    st.session_state["saved_operator_name"] = st.session_state["_operator_name"]
    st.session_state["saved_test_date"]     = st.session_state["_test_date"]
    errors = tuple(metadata_errors(st.session_state))
    st.session_state["metadata_error"] = ""
    _clean_time_widget_keys(nb_sample)
    saved = save_session()
    return MetadataSaveResult(saved, errors)


def _on_skip_collect_times_change() -> None:
    val = st.session_state.get("skip_collect_times", False)
    st.session_state["_skip_collect_times_value"] = val
    st.session_state["metadata_error"] = ""
    if val:
        from config import WORKFLOW_MAP  # noqa: F401 — import here to avoid circular
        # Reset collect times when skipping
        st.session_state["df_collect_times"] = st.session_state["df_collect_times"].iloc[0:0]
    save_session()


# ── CONTAINERS ────────────────────────────────────────────────────────────────
def add_container() -> None:
    container_name = st.session_state["container_name"].strip()
    try:
        container_weight = nonnegative_weight(st.session_state["container_weight"])
    except ValueError:
        st.session_state["container_error"] = t("cont_error_invalid")
        return

    if not container_name:
        st.session_state["container_error"] = "Veuillez renseigner un identifiant de contenant."
        return
    if container_name in st.session_state["df_containers"]["Contenant"].tolist():
        st.session_state["container_error"] = "Ce contenant existe déjà."
        return

    new_data = pd.DataFrame({
        "Contenant":    [container_name],
        "Poids à vide": [container_weight],
    }).astype({"Contenant": str, "Poids à vide": float})

    if st.session_state["df_containers"].empty:
        st.session_state["df_containers"] = new_data
    else:
        st.session_state["df_containers"] = pd.concat(
            [st.session_state["df_containers"], new_data], ignore_index=True
        )
    st.session_state["container_name"]   = ""
    st.session_state["container_weight"] = 0.0
    st.session_state["container_error"]  = ""
    save_session()


def remove_container(container_name: str) -> bool:
    used_count = int((
        st.session_state["df_weighings"]["Contenant utilisé"] == container_name
    ).sum())
    if used_count:
        st.session_state["container_error"] = t(
            "cont_used_cannot_delete", n=used_count
        )
        return False
    st.session_state["df_containers"] = (
        st.session_state["df_containers"]
        .loc[st.session_state["df_containers"]["Contenant"] != container_name]
        .reset_index(drop=True)
    )
    st.session_state["container_error"] = ""
    save_session()
    st.rerun()
    return True


# ── WEIGHINGS ─────────────────────────────────────────────────────────────────
def add_weighing() -> None:
    v = st.session_state.get("weighing_version", 0)
    gross_weight_text = st.session_state.get(f"gross_weight_{v}", "").strip()

    try:
        weights = gross_weights(gross_weight_text)
    except ValueError:
        st.session_state["weighing_error"] = t("weigh_error_format")
        return

    sample_ids     = st.session_state["sample_nb"]
    material_class = st.session_state.get(f"material_class_{v}")
    container_used = st.session_state["container_used"]

    if not sample_ids:
        st.session_state["weighing_error"] = "Veuillez choisir au moins un échantillon."
        return
    if material_class is None:
        st.session_state["weighing_error"] = "Veuillez choisir une classe de matériau."
        return

    sample_label = ", ".join(map(str, sorted(sample_ids)))
    try:
        tare_weight = nonnegative_weight(
            get_container_weight(container_used) if container_used != "Pas de contenant" else 0.0
        )
    except ValueError:
        st.session_state["weighing_error"] = t("weigh_error_invalid_tare")
        return

    img_key  = f"weighing_image_{st.session_state['image_uploader_key']}"
    img_data = st.session_state[img_key].read() if st.session_state.get(img_key) else None

    new_rows = []
    for gross_weight in weights:
        try:
            net_weight = calculate_net_weight(gross_weight, tare_weight)
        except ValueError:
            negative_net = gross_weight - tare_weight
            st.session_state["weighing_error"] = (
                t("weigh_error_negative", net=negative_net)
            )
            return
        new_rows.append({
            WEIGHING_ID_COLUMN:  new_weighing_id(),
            "N° échantillon":     sample_label,
            "Classe de matériau": material_class,
            "Contenant utilisé":  "" if not container_used or container_used == "Pas de contenant" else container_used,
            "Poids brut":         gross_weight,
            "Tare":               tare_weight,
            "Poids net":          net_weight,
            "Image":              img_data,
        })

    new_df = pd.DataFrame(new_rows).astype({"Poids brut": float, "Tare": float, "Poids net": float})
    if st.session_state["df_weighings"].empty:
        st.session_state["df_weighings"] = new_df
    else:
        st.session_state["df_weighings"] = pd.concat(
            [st.session_state["df_weighings"], new_df], ignore_index=True
        )

    st.toast("Pesée ajoutée !", icon="⚖️")
    st.session_state["weighing_version"] = v + 1
    st.session_state.pop(f"material_class_{v}", None)
    st.session_state.pop(f"gross_weight_{v}", None)
    st.session_state.pop("container_used", None)
    st.session_state["weighing_error"]    = ""
    st.session_state["image_uploader_key"] += 1
    save_session()
    st.rerun()


def delete_weighing(idx: int) -> None:
    row = st.session_state["df_weighings"].loc[idx]
    table_class = row.get("__table_class")
    if isinstance(table_class, str) and table_class:
        st.session_state.pop("weighing_table", None)
        st.session_state["weighing_table_editor_version"] = (
            st.session_state.get("weighing_table_editor_version", 0) + 1
        )

    st.session_state["df_weighings"] = (
        st.session_state["df_weighings"]
        .drop(index=idx)
        .reset_index(drop=True)
    )
    st.session_state["weighing_error"] = ""
    save_session()


# ── SUMMARY ───────────────────────────────────────────────────────────────────
def summarize_by_material(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=["Classe de matériau", "Poids net", "Pourcentage de la masse totale"]
        )
    summary = (
        df.groupby("Classe de matériau", as_index=False)[["Poids net"]]
        .sum()
        .sort_values("Poids net", ascending=False)
        .reset_index(drop=True)
    )
    total = summary["Poids net"].sum()
    summary["Pourcentage de la masse totale"] = (
        summary["Poids net"] / total * 100 if total > 0 else 0.0
    )
    return summary


def get_missing_classes() -> list[str]:
    """Returns configured classes that have no weighing recorded."""
    material_classes = st.session_state.get("material_classes", [])
    if st.session_state["df_weighings"].empty:
        return material_classes
    recorded = set(
        st.session_state["df_weighings"]["Classe de matériau"].dropna().unique()
    )
    return [c for c in material_classes if c not in recorded]
