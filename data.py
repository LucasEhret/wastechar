import datetime as dt
import pandas as pd
import streamlit as st

from helpers import (
    check_entry_typo,
    get_sample_collect_times,
    get_container_weight,
    parse_time_str,
    _clean_time_widget_keys,
)
from session import save_session


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
                saved_start = s if s != "00:00:00" else ""
                saved_end   = e if e != "00:00:00" else ""
        for suffix, val in ((f"_start_{i}", saved_start), (f"_end_{i}", saved_end)):
            if suffix not in st.session_state:
                st.session_state[suffix] = val


def save_metadata() -> None:
    nb_sample = st.session_state["_nb_sample"]
    rows = []
    for i in range(1, nb_sample + 1):
        s_date    = st.session_state["_test_date"]
        start_raw = (st.session_state.get(f"_start_{i}") or "").strip()
        end_raw   = (st.session_state.get(f"_end_{i}")   or "").strip()

        try:
            t_s = parse_time_str(start_raw) if start_raw else dt.time(0, 0, 0)
        except ValueError:
            st.session_state["metadata_error"] = (
                f"Échantillon {i} : format d'heure de début invalide ('{start_raw}'). "
                "Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss."
            )
            return
        try:
            t_e = parse_time_str(end_raw) if end_raw else dt.time(0, 0, 0)
        except ValueError:
            st.session_state["metadata_error"] = (
                f"Échantillon {i} : format d'heure de fin invalide ('{end_raw}'). "
                "Formats acceptés : hh:mm:ss, hhmmss, hh.mm.ss."
            )
            return

        rows.append({
            "Echantillon":    i,
            "Date":           s_date,
            "Heure de début": f"{t_s.hour:02d}:{t_s.minute:02d}:{t_s.second:02d}",
            "Heure de fin":   f"{t_e.hour:02d}:{t_e.minute:02d}:{t_e.second:02d}",
        })

    for row in rows:
        if row["Heure de début"] == "00:00:00" and row["Heure de fin"] == "00:00:00":
            continue
        if row["Heure de fin"] == "00:00:00":
            continue
        if row["Heure de fin"] <= row["Heure de début"]:
            st.session_state["metadata_error"] = (
                f"Échantillon {row['Echantillon']} : "
                "l'heure de fin doit être postérieure à l'heure de début."
            )
            return

    st.session_state["df_collect_times"]    = pd.DataFrame(rows)
    st.session_state["saved_sensor_name"]   = st.session_state["_sensor_name"]
    st.session_state["saved_nb_sample"]     = nb_sample
    st.session_state["saved_operator_name"] = st.session_state["_operator_name"]
    st.session_state["saved_test_date"]     = st.session_state["_test_date"]
    st.session_state["metadata_error"]      = ""
    _clean_time_widget_keys(nb_sample)
    save_session()
    st.session_state["_meta_nav_errors"] = _compute_meta_nav_errors()


def _on_skip_collect_times_change() -> None:
    val = st.session_state.get("skip_collect_times", False)
    st.session_state["_skip_collect_times_value"] = val
    if val:
        from config import WORKFLOW_MAP  # noqa: F401 — import here to avoid circular
        # Reset collect times when skipping
        st.session_state["df_collect_times"] = st.session_state["df_collect_times"].iloc[0:0]
    save_session()


def _compute_meta_nav_errors() -> set:
    errors: set = set()
    if not (st.session_state.get("_operator_name") or "").strip():
        errors.add("operator")
    if not st.session_state.get("skip_collect_times"):
        nb = int(st.session_state.get("_nb_sample", 1))
        for i in range(1, nb + 1):
            if not (st.session_state.get(f"_start_{i}") or "").strip():
                errors.add(f"start_{i}")
            if not (st.session_state.get(f"_end_{i}") or "").strip():
                errors.add(f"end_{i}")
    st.session_state["_meta_nav_errors"] = errors
    return errors


# ── CONTAINERS ────────────────────────────────────────────────────────────────
def add_container() -> None:
    container_name = st.session_state["container_name"].strip()
    try:
        container_weight = float(st.session_state["container_weight"])
    except ValueError:
        st.session_state["container_error"] = "Le poids doit être un nombre valide."
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


def remove_container(container_name: str) -> None:
    st.session_state["df_containers"] = (
        st.session_state["df_containers"]
        .loc[st.session_state["df_containers"]["Contenant"] != container_name]
        .reset_index(drop=True)
    )
    st.session_state["df_weighings"] = (
        st.session_state["df_weighings"]
        .loc[st.session_state["df_weighings"]["Contenant utilisé"] != container_name]
        .reset_index(drop=True)
    )
    st.session_state["container_error"] = ""
    save_session()
    st.rerun()


# ── WEIGHINGS ─────────────────────────────────────────────────────────────────
def add_weighing() -> None:
    v = st.session_state.get("weighing_version", 0)
    gross_weight_text = st.session_state.get(f"gross_weight_{v}", "").strip()

    if not check_entry_typo(gross_weight_text):
        st.session_state["weighing_error"] = (
            "Veuillez vérifier la saisie des poids bruts. "
            "Séparez les poids par des espaces, avec virgule ou point décimal."
        )
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
    times        = get_sample_collect_times(sample_ids[0])
    tare_weight  = get_container_weight(container_used) if container_used != "Pas de contenant" else 0.0
    weights      = [float(w.replace(",", ".")) for w in gross_weight_text.split()]

    img_key  = f"weighing_image_{st.session_state['image_uploader_key']}"
    img_data = st.session_state[img_key].read() if st.session_state.get(img_key) else None

    new_rows = []
    for gross_weight in weights:
        net_weight = gross_weight - tare_weight
        if net_weight < 0:
            st.session_state["weighing_error"] = (
                f"Le poids net calculé est négatif ({net_weight:.3f} kg). "
                "Vérifiez le contenant sélectionné et les poids saisis."
            )
            return
        new_rows.append({
            "N° échantillon":     sample_label,
            "Début":              times["Début"] if times else None,
            "Fin":                times["Fin"]   if times else None,
            "Classe de matériau": material_class,
            "Contenant utilisé":  "" if not container_used or container_used == "Pas de contenant" else container_used,
            "Poids brut":         gross_weight,
            "Poids net":          net_weight,
            "Image":              img_data,
        })

    new_df = pd.DataFrame(new_rows).astype({"Poids brut": float, "Poids net": float})
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
    st.session_state["df_weighings"] = (
        st.session_state["df_weighings"]
        .drop(index=idx)
        .reset_index(drop=True)
    )
    st.session_state["weighing_error"] = ""
    save_session()
    st.rerun()


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
