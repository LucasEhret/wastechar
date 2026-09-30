"""Table weighing drafts and their recorded counterparts."""

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from helpers import get_container_weight
from i18n import t
from session import save_session
from weights import net_weight as calculate_net_weight, nonnegative_weight
from weighing_identity import WEIGHING_ID_COLUMN, new_weighing_id


TABLE_CLASS_COLUMN = "__table_class"
NO_CONTAINER = "Pas de contenant"


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
    recorded = st.session_state["df_weighings"]
    if TABLE_CLASS_COLUMN not in recorded.columns:
        return None
    matching = recorded.loc[recorded[TABLE_CLASS_COLUMN].fillna("") == material_class]
    if matching.empty:
        return None
    return matching.iloc[-1]


def duplicate_table_classes() -> list[str]:
    recorded = st.session_state["df_weighings"]
    if TABLE_CLASS_COLUMN not in recorded.columns:
        return []
    counts = recorded[TABLE_CLASS_COLUMN].dropna()
    counts = counts[counts != ""].value_counts()
    return counts[counts > 1].index.tolist()


def _record_for_id(weighing_id: str) -> pd.Series | None:
    recorded = st.session_state["df_weighings"]
    if WEIGHING_ID_COLUMN not in recorded.columns:
        return None
    matching = recorded.loc[recorded[WEIGHING_ID_COLUMN] == weighing_id]
    if len(matching) != 1:
        return None
    return matching.iloc[0]


def make_table_draft(material_classes: list[str], nb_sample: int, is_single: bool) -> pd.DataFrame:
    """Populate table rows from saved table weighings, including after refresh."""
    rows = []
    for material_class in material_classes:
        saved = _record_for_class(material_class)
        if saved is None:
            sample, container, gross = (1 if is_single else None), NO_CONTAINER, None
        else:
            record = saved
            try:
                sample = int(record["N° échantillon"])
            except (TypeError, ValueError):
                sample = None
            if sample not in range(1, nb_sample + 1):
                sample = None
            container = record["Contenant utilisé"] or NO_CONTAINER
            gross = float(record["Poids brut"])
        rows.append({
            "Classe de matériau": material_class,
            "Contenant utilisé": container,
            "N° échantillon": 1 if is_single else sample,
            "Poids brut": gross,
            WEIGHING_ID_COLUMN: record[WEIGHING_ID_COLUMN] if saved is not None else None,
        })
    return pd.DataFrame(rows)


def preview_table(edited_df: pd.DataFrame) -> TablePreview:
    """Validate the whole draft before any weighing is changed."""
    valid_samples = set(range(1, st.session_state["saved_nb_sample"] + 1))
    valid_containers = set(st.session_state["df_containers"]["Contenant"])
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
            if saved is None or saved[TABLE_CLASS_COLUMN] != material_class:
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
            sample = int(sample_raw)
            if sample != sample_raw or sample not in valid_samples:
                raise ValueError
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
                str(record["N° échantillon"]) == str(sample)
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
            "N° échantillon": str(sample),
            "Classe de matériau": material_class,
            "Contenant utilisé": container_name,
            "Poids brut": gross,
            "Tare": tare,
            "Poids net": net,
            TABLE_CLASS_COLUMN: material_class,
        }))

    return TablePreview(changes, filled_count, net_total)


def save_table(edited_df: pd.DataFrame) -> None:
    try:
        preview = preview_table(edited_df)
    except ValueError as exc:
        st.session_state["weighing_error"] = str(exc)
        return

    if not preview.changes:
        st.session_state["weighing_error"] = ""
        return

    recorded = st.session_state["df_weighings"].copy()
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
                st.session_state["weighing_error"] = t("weigh_table_error_stale", material=change.values["Classe de matériau"])
                return
            for key, value in change.values.items():
                recorded.at[matches[0], key] = value

    st.session_state["df_weighings"] = recorded
    st.session_state["weighing_error"] = ""
    st.session_state["weighing_table"] = make_table_draft(
        st.session_state.get("material_classes", edited_df["Classe de matériau"].tolist()),
        st.session_state["saved_nb_sample"],
        st.session_state.get("saved_workflow", 0) == 0,
    )
    st.session_state["weighing_table_editor_version"] = (
        st.session_state.get("weighing_table_editor_version", 0) + 1
    )
    if save_session():
        st.toast(t("weigh_table_saved_count", added=added, corrected=len(preview.changes) - added), icon="⚖️")
