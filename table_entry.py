"""Table weighing drafts and their recorded counterparts."""

from ui.report_state import app_state

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from helpers import get_container_weight, sample_ids_from_label
from i18n import t
from session import save_session
from weights import net_weight as calculate_net_weight, nonnegative_weight
from weighing_identity import WEIGHING_ID_COLUMN, new_weighing_id, ensure_weighing_ids


TABLE_CLASS_COLUMN = "__table_class"
NO_CONTAINER = ""
EDITABLE_COLUMNS = ("N° échantillon", "Contenant utilisé", "Poids brut")


@dataclass
class TableChange:
    weighing_id: str | None
    values: dict


@dataclass
class TablePreview:
    changes: list[TableChange]
    filled_count: int
    net_total: float


def _record_for_class(material_class: str) -> pd.Series | None:
    recorded = app_state["df_weighings"]
    matching = recorded.loc[recorded["Classe de matériau"] == material_class]
    if matching.empty:
        return None
    if len(matching) != 1:
        raise ValueError(t("weigh_table_error_stale", material=material_class))
    return matching.iloc[0]


def _record_for_id(weighing_id: str) -> pd.Series | None:
    recorded = app_state["df_weighings"]
    if WEIGHING_ID_COLUMN not in recorded.columns:
        return None
    matching = recorded.loc[recorded[WEIGHING_ID_COLUMN] == weighing_id]
    if len(matching) != 1:
        return None
    return matching.iloc[0]


def make_table_draft(material_classes: list[str], nb_sample: int, is_single: bool) -> pd.DataFrame:
    """Show all saved weighings, with blank rows for unrecorded materials."""
    recorded = ensure_weighing_ids(app_state["df_weighings"])
    app_state["df_weighings"] = recorded
    materials = list(dict.fromkeys([
        *material_classes, *recorded["Classe de matériau"].dropna().tolist(),
    ]))
    rows = []
    for material_class in materials:
        matching = recorded.loc[recorded["Classe de matériau"] == material_class]
        if matching.empty:
            rows.append({
                "Classe de matériau": material_class, "Contenant utilisé": NO_CONTAINER,
                "N° échantillon": "1" if is_single else "", "Poids brut": None,
                WEIGHING_ID_COLUMN: None,
            })
        else:
            for _, record in matching.iterrows():
                rows.append({
                    "Classe de matériau": material_class,
                    "Contenant utilisé": record["Contenant utilisé"] or NO_CONTAINER,
                    "N° échantillon": str(record["N° échantillon"]),
                    "Poids brut": float(record["Poids brut"]),
                    WEIGHING_ID_COLUMN: record[WEIGHING_ID_COLUMN],
                })
    return pd.DataFrame(rows, columns=[
        "Classe de matériau", "Contenant utilisé", "N° échantillon", "Poids brut", WEIGHING_ID_COLUMN,
    ])


def _draft_key(row) -> str:
    weighing_id = row.get(WEIGHING_ID_COLUMN)
    return weighing_id if isinstance(weighing_id, str) and weighing_id else row["Classe de matériau"]


def apply_table_draft(saved_rows: pd.DataFrame, edits: dict) -> pd.DataFrame:
    """Overlay pending cell edits on rows derived from recorded weighings."""
    rows = saved_rows.copy()
    for index, row in rows.iterrows():
        draft_key = _draft_key(row)
        changes = edits.get(draft_key)
        if changes is None and (rows["Classe de matériau"] == row["Classe de matériau"]).sum() == 1:
            changes = edits.get(row["Classe de matériau"], {})
        for column, value in (changes or {}).items():
            if column in EDITABLE_COLUMNS:
                rows.at[index, column] = value
    return rows


def update_table_draft(saved_rows: pd.DataFrame, edited_rows: pd.DataFrame, edits: dict) -> dict:
    """Keep only cells that differ from the recorded weighing."""
    pending = dict(edits)
    for index, row in edited_rows.iterrows():
        baseline = saved_rows.loc[index]
        changes = {}
        for column in EDITABLE_COLUMNS:
            value, saved_value = row[column], baseline[column]
            if pd.isna(value) and pd.isna(saved_value):
                continue
            if pd.isna(value) or pd.isna(saved_value) or value != saved_value:
                changes[column] = value
        draft_key = _draft_key(row)
        if draft_key != row["Classe de matériau"] and (saved_rows["Classe de matériau"] == row["Classe de matériau"]).sum() == 1:
            pending.pop(row["Classe de matériau"], None)
        if changes:
            pending[draft_key] = changes
        else:
            pending.pop(draft_key, None)
    return pending


def preview_table(edited_df: pd.DataFrame) -> TablePreview:
    """Validate the whole draft before any weighing is changed."""
    valid_samples = set(range(1, app_state["saved_nb_sample"] + 1))
    valid_containers = set(app_state["df_containers"]["Contenant"])
    changes = []
    filled_count = 0
    net_total = 0.0

    for _, row in edited_df.iterrows():
        material_class = row["Classe de matériau"]
        row_id = row.get(WEIGHING_ID_COLUMN)
        if not isinstance(row_id, str) or not row_id:
            row_id = None
        if row_id is not None:
            saved = _record_for_id(row_id)
            if saved is None or saved["Classe de matériau"] != material_class:
                raise ValueError(t("weigh_table_error_stale", material=material_class))
        else:
            saved = _record_for_class(material_class)
        gross_raw = row["Poids brut"]

        if pd.isna(gross_raw):
            if saved is not None:
                raise ValueError(t("weigh_table_error_clear", material=material_class))
            continue

        sample_raw = row["N° échantillon"]
        try:
            samples = sample_ids_from_label(sample_raw)
            if any(sample not in valid_samples for sample in samples):
                raise ValueError
            sample_label = ", ".join(map(str, sorted(samples)))
        except (TypeError, ValueError):
            raise ValueError(t("weigh_table_error_sample", material=material_class)) from None

        container = row["Contenant utilisé"]
        if pd.isna(container) or (container != NO_CONTAINER and container not in valid_containers):
            raise ValueError(t("weigh_table_error_container", material=material_class))

        try:
            gross = nonnegative_weight(gross_raw)
        except ValueError:
            raise ValueError(t("weigh_table_error_weight", material=material_class)) from None

        try:
            tare = nonnegative_weight(
                get_container_weight(container) if container != NO_CONTAINER else 0.0
            )
        except ValueError:
            raise ValueError(t("weigh_table_error_tare", material=material_class)) from None
        try:
            net = calculate_net_weight(gross, tare)
        except ValueError:
            raise ValueError(t("weigh_table_error_negative", material=material_class, net=gross - tare)) from None

        filled_count += 1
        net_total += net
        container_name = "" if container == NO_CONTAINER else container
        if saved is not None:
            record = saved
            row_id = record[WEIGHING_ID_COLUMN]
            if (
                str(record["N° échantillon"]) == sample_label
                and record["Contenant utilisé"] == container_name
                and float(record["Poids brut"]) == gross
                and float(record["Poids net"]) == net
                and record["Classe de matériau"] == material_class
            ):
                continue
        else:
            row_id = None

        changes.append(TableChange(weighing_id=row_id if row_id else None, values={
            WEIGHING_ID_COLUMN: row_id if row_id else new_weighing_id(),
            "N° échantillon": sample_label,
            "Classe de matériau": material_class,
            "Contenant utilisé": container_name,
            "Poids brut": gross,
            "Tare": tare,
            "Poids net": net,
            TABLE_CLASS_COLUMN: saved.get(TABLE_CLASS_COLUMN) if saved is not None else material_class,
        }))

    return TablePreview(changes, filled_count, net_total)


def save_table(edited_df: pd.DataFrame) -> bool:
    try:
        preview = preview_table(edited_df)
    except ValueError as exc:
        app_state["weighing_error"] = str(exc)
        return False

    if not preview.changes:
        app_state["weighing_error"] = ""
        return save_session()

    recorded = app_state["df_weighings"].copy()
    added = 0
    for change in preview.changes:
        if change.weighing_id is None:
            recorded = pd.concat(
                [recorded, pd.DataFrame([{**change.values, "Image": None}])],
                ignore_index=True,
            )
            added += 1
        else:
            matches = recorded.index[recorded[WEIGHING_ID_COLUMN] == change.weighing_id]
            if len(matches) != 1:
                app_state["weighing_error"] = t("weigh_table_error_stale", material=change.values["Classe de matériau"])
                return False
            for key, value in change.values.items():
                recorded.at[matches[0], key] = value

    app_state["df_weighings"] = recorded
    app_state["weighing_error"] = ""
    saved_rows = make_table_draft(
        edited_df["Classe de matériau"].tolist(),
        app_state["saved_nb_sample"],
        app_state.get("saved_workflow", 0) == 0,
    )
    app_state["_table_draft"] = update_table_draft(saved_rows, edited_df, {})
    if save_session():
        st.toast(t("weigh_table_saved_count", added=added, corrected=len(preview.changes) - added), icon="⚖️")
        return True
    return False
