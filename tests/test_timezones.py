import datetime as dt
import unittest
from unittest.mock import patch
import zipfile

import pandas as pd
from openpyxl import load_workbook

import export
from time_utils import account_timezone, in_account_timezone


class AccountTimeZoneTests(unittest.TestCase):
    def test_daylight_saving_and_invalid_zone(self):
        zone = account_timezone("Europe/Zurich")
        self.assertEqual(dt.datetime(2026, 1, 1, tzinfo=zone).utcoffset(), dt.timedelta(hours=1))
        self.assertEqual(dt.datetime(2026, 7, 1, tzinfo=zone).utcoffset(), dt.timedelta(hours=2))
        with self.assertRaises(ValueError):
            account_timezone("Not/AZone")
        with self.assertRaises(ValueError):
            in_account_timezone(dt.datetime(2026, 1, 1), "Europe/Zurich")

    def test_zip_name_and_excel_timestamp_use_account_zone(self):
        state = {
            "user_timezone": "Europe/Zurich",
            "facility_name": "Site",
            "df_weighings": pd.DataFrame([{
                "N° échantillon": "1", "Classe de matériau": "Paper",
                "Contenant utilisé": "", "Poids brut": 0.0,
                "Tare": 0.0, "Poids net": 0.0,
            }]),
            "df_collect_times": pd.DataFrame(columns=[
                "Echantillon", "Date", "Heure de début", "Heure de fin",
            ]),
            "saved_sensor_name": "Sensor",
            "saved_test_date": dt.date(2026, 1, 1),
            "saved_operator_name": "Alice",
            "saved_nb_sample": 1,
            "_skip_collect_times_value": True,
            "saved_workflow": 0,
            "saved_workflow_order": 0,
            "material_classes": ["Paper"],
        }
        cases = (
            (dt.datetime(2026, 1, 1, 23, 30, tzinfo=dt.timezone.utc),
             "20260102_0030+0100", "2026-01-02T00:30:00+01:00"),
            (dt.datetime(2026, 7, 1, 22, 30, tzinfo=dt.timezone.utc),
             "20260702_0030+0200", "2026-07-02T00:30:00+02:00"),
            (dt.datetime(2026, 10, 25, 0, 30, tzinfo=dt.timezone.utc),
             "20261025_0230+0200", "2026-10-25T02:30:00+02:00"),
            (dt.datetime(2026, 10, 25, 1, 30, tzinfo=dt.timezone.utc),
             "20261025_0230+0100", "2026-10-25T02:30:00+01:00"),
        )
        with patch.object(export.st, "session_state", state):
            for instant, filename_time, metadata_time in cases:
                with self.subTest(instant=instant):
                    with zipfile.ZipFile(export.build_zip_export(generated_at=instant)) as archive:
                        excel_name = next(name for name in archive.namelist() if name.endswith(".xlsx"))
                        self.assertIn(filename_time, excel_name)
                        metadata = dict(list(load_workbook(archive.open(excel_name), data_only=True)["Metadata"].values)[1:])
                        self.assertEqual(metadata["Export timestamp"], metadata_time)
                        self.assertEqual(metadata["Time zone"], "Europe/Zurich")


if __name__ == "__main__":
    unittest.main()
