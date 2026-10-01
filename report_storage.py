"""Versioned report persistence, independent of Streamlit and filesystem access."""

import base64
import datetime as dt
import io
import pandas as pd

from report import Report, CONTAINER_DTYPES, COLLECTION_DTYPES, WEIGHING_DTYPES
from weights import ensure_recorded_tare
from weighing_identity import ensure_weighing_ids
from time_utils import local_today

SESSION_SCHEMA_VERSION = 2


def serialize_report(report: Report, owner: str, saved_at: dt.datetime) -> dict:
    return {
        "schema_version": SESSION_SCHEMA_VERSION,
        "saved_at": saved_at.isoformat(),
        "owner": owner,
        "facility": report.facility,
        "df_weighings": (
            report.weighings
            .drop(columns=["Image"], errors="ignore")
            .to_json(orient="records")
        ),
        "df_containers": report.containers.to_json(orient="records"),
        "df_collect_times": (
            report.collection_times
            .astype({"Date": str}, errors="ignore")
            .to_json(orient="records")
        ),
        "metadata": {
            "workflow":           report.workflow,
            "workflow_order":     report.sensor_passage,
            "operator":           report.operator,
            "sensor":             report.sensor,
            "nb_sample":          report.sample_count,
            "date":               str(report.test_date),
            "global_comment":     report.comment,
            "skip_collect_times": report.skip_collection_times,
        },
        "photos": {
            row["__weighing_id"]: base64.b64encode(row["Image"]).decode("ascii")
            for _, row in report.weighings.iterrows()
            if isinstance(row.get("Image"), bytes)
        },
    }

def _restore_df(
    json_str: str,
    dtype_map: dict,
    date_cols: list | None = None,
) -> pd.DataFrame:
    df = pd.read_json(io.StringIO(json_str))
    if df.empty:
        df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in dtype_map.items()})
    for col, dtype in dtype_map.items():
        if col not in df.columns:
            raise ValueError(f"Missing session column: {col}")
        df[col] = df[col].astype(dtype)
    for col in (date_cols or []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date
    return df


def deserialize_report(data: dict, context: Report) -> tuple[Report, str | None]:
    version = data.get("schema_version", 1)
    if type(version) is not int or version not in (1, SESSION_SCHEMA_VERSION):
        raise ValueError("Unsupported session schema version")
    restored = context.to_state()
    restored["lang"] = context.language
    sensor_list = [context.sensor]

    df_w = _restore_df(
        data["df_weighings"],
        {key: dtype for key, dtype in WEIGHING_DTYPES.items()
         if key not in ("Tare", "__weighing_id", "__table_class")},
    )
    restored["df_weighings"] = ensure_weighing_ids(ensure_recorded_tare(
        df_w.drop(columns=["Début", "Fin"], errors="ignore")
    ))
    restored["df_weighings"]["Tare"] = restored["df_weighings"]["Tare"].astype(float)

    df_c = _restore_df(
        data["df_containers"],
        CONTAINER_DTYPES,
    )
    restored["df_containers"] = df_c

    df_t = _restore_df(
        data["df_collect_times"],
        COLLECTION_DTYPES,
        date_cols=["Date"],
    )
    restored["df_collect_times"] = df_t

    meta = data["metadata"]
    if version == 2 and type(meta.get("nb_sample")) is not int:
        raise ValueError("Invalid saved sample count")
    restored["saved_operator_name"] = meta.get("operator", "")
    restored["saved_sensor_name"]   = meta.get("sensor", sensor_list[0] if sensor_list else "")
    restored["saved_nb_sample"]     = int(meta.get("nb_sample", 1))
    restored["saved_test_date"]     = dt.date.fromisoformat(
        meta.get("date", str(local_today(context.timezone)))
    )
    restored["_global_comment_value"] = meta.get("global_comment", "")
    restored["skip_collect_times"]  = meta.get("skip_collect_times", False)
    restored["_skip_collect_times_value"] = restored["skip_collect_times"]

    wf = meta.get("workflow", 0)
    if isinstance(wf, str):
        wf = {
            "Standard": 0, "Estándar": 0, "Single": 0, "Unique": 0, "Único": 0,
            "Multi-échantillon": 1, "Multi-sample": 1,
            "Multi-muestra": 1, "Multiple": 1, "Múltiple": 1,
            "?chantillon unique": 0, "?chantillons multiples": 1,
        }.get(wf, 0)
    restored["saved_workflow"] = wf

    wfo = meta.get("workflow_order", 0)
    if isinstance(wfo, str):
        wfo = {
            "A": 0, "B": 1, "Standard": 0, "Estándar": 0,
            "Inverse": 1, "Contrarrestar": 1,
            "Before weighing": 0, "After weighing": 1,
            "Avant la pesée": 0, "Après la pesée": 1,
            "Antes del pesaje": 0, "Después del pesaje": 1,
        }.get(wfo, 0)
    restored["saved_workflow_order"] = wfo

    saved_at = None
    if version == 2:
        saved_at = dt.datetime.fromisoformat(data["saved_at"])
        if saved_at.tzinfo is None or saved_at.utcoffset() is None:
            raise ValueError("Saved timestamp must include a time zone")
        saved_at = saved_at.isoformat()
    photos = data.get("photos", {}) if version == 2 else {}
    if not isinstance(photos, dict):
        raise ValueError("Invalid session photos")
    weighings = restored["df_weighings"]
    known_ids = set(weighings["__weighing_id"])
    if set(photos) - known_ids:
        raise ValueError("Photo references an unknown weighing")
    decoded = {}
    for weighing_id, encoded in photos.items():
        if not isinstance(encoded, str):
            raise ValueError("Invalid session photo encoding")
        decoded[weighing_id] = base64.b64decode(encoded, validate=True)
    weighings["Image"] = weighings["__weighing_id"].map(decoded).astype(object)
    if type(restored["saved_nb_sample"]) is not int or not 1 <= restored["saved_nb_sample"] <= 100:
        raise ValueError("Invalid saved sample count")
    for key in ("saved_workflow", "saved_workflow_order"):
        if type(restored[key]) is not int or restored[key] not in (0, 1):
            raise ValueError("Invalid saved workflow")
    for key in ("saved_operator_name", "saved_sensor_name", "_global_comment_value"):
        if not isinstance(restored[key], str):
            raise ValueError("Invalid saved metadata text")
    if type(restored["skip_collect_times"]) is not bool:
        raise ValueError("Invalid saved collection-time setting")
    return Report.from_state(restored), saved_at
