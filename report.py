"""Report data independent of Streamlit, widget keys, and screen navigation."""

from collections.abc import Mapping
from dataclasses import dataclass, field
import datetime as dt

import pandas as pd

from time_utils import DEFAULT_TIMEZONE


CONTAINER_DTYPES = {"Contenant": str, "Poids à vide": float}
COLLECTION_DTYPES = {
    "Echantillon": int, "Date": object, "Heure de début": str, "Heure de fin": str,
}
WEIGHING_DTYPES = {
    "N° échantillon": str, "Classe de matériau": str, "Contenant utilisé": str,
    "Poids brut": float, "Tare": float, "Poids net": float,
    "__weighing_id": str, "__table_class": str,
}


def empty_table(schema: dict) -> pd.DataFrame:
    return pd.DataFrame({name: pd.Series(dtype=dtype) for name, dtype in schema.items()})


# Compatibility names are confined to this boundary while UI callbacks migrate.
REPORT_FIELDS = {
    "facility_name": "facility", "user_timezone": "timezone",
    "material_classes": "material_classes", "saved_operator_name": "operator",
    "saved_sensor_name": "sensor", "saved_test_date": "test_date",
    "saved_nb_sample": "sample_count", "saved_workflow": "workflow",
    "saved_workflow_order": "sensor_passage", "_global_comment_value": "comment",
    "_skip_collect_times_value": "skip_collection_times",
    "df_weighings": "weighings", "df_containers": "containers",
    "df_collect_times": "collection_times",
}


@dataclass
class Report(Mapping):
    language: str = "FR"
    facility: str = ""
    timezone: str = DEFAULT_TIMEZONE
    material_classes: list[str] = field(default_factory=list)
    operator: str = ""
    sensor: str = ""
    test_date: dt.date | None = None
    sample_count: int = 1
    workflow: int = 0
    sensor_passage: int = 0
    comment: str = ""
    skip_collection_times: bool = False
    weighings: pd.DataFrame = field(default_factory=lambda: empty_table(WEIGHING_DTYPES))
    containers: pd.DataFrame = field(default_factory=lambda: empty_table(CONTAINER_DTYPES))
    collection_times: pd.DataFrame = field(default_factory=lambda: empty_table(COLLECTION_DTYPES))

    def __getitem__(self, key):
        if key not in REPORT_FIELDS:
            raise KeyError(key)
        return getattr(self, REPORT_FIELDS[key])

    def __iter__(self):
        return iter(REPORT_FIELDS)

    def __len__(self):
        return len(REPORT_FIELDS)

    @classmethod
    def from_state(cls, source: Mapping) -> "Report":
        """Snapshot committed fields only; exclude widget values and UI flags."""
        values = {"language": source.language if isinstance(source, Report) else source.get("lang", "FR")}
        for key, attribute in REPORT_FIELDS.items():
            if key in source:
                value = source[key]
                if isinstance(value, pd.DataFrame):
                    value = value.copy(deep=True)
                elif isinstance(value, list):
                    value = value.copy()
                values[attribute] = value
        return cls(**values)

    def snapshot(self) -> "Report":
        return Report.from_state(self)

    def to_state(self) -> dict:
        """Project compatibility keys for migrations and legacy backups."""
        return dict(self)
