import datetime as dt
import unittest
from unittest.mock import patch
import zipfile

import pandas as pd
import matplotlib

matplotlib.use("Agg", force=True)

import export


class PdfExportTests(unittest.TestCase):
    def _state(self, weight):
        return {
            "df_weighings": pd.DataFrame([{
                "N° échantillon": "1", "Classe de matériau": "Paper",
                "Contenant utilisé": "", "Poids brut": weight,
                "Tare": 0.0, "Poids net": weight,
            }]),
            "df_collect_times": pd.DataFrame([{
                "Echantillon": 1, "Date": dt.date(2026, 9, 30),
                "Heure de début": "10:00:00", "Heure de fin": "11:00:00",
            }]),
            "saved_sensor_name": "Sensor",
            "saved_test_date": dt.date(2026, 9, 30),
            "saved_operator_name": "Alice",
            "saved_nb_sample": 1,
            "_skip_collect_times_value": False,
            "saved_workflow": 0,
            "saved_workflow_order": 0,
            "material_classes": ["Paper"],
            "facility_name": "Site",
        }

    def test_zip_contains_a_pdf_for_positive_and_zero_weight(self):
        for weight in (1.0, 0.0):
            with self.subTest(weight=weight):
                with patch.object(export.st, "session_state", self._state(weight)):
                    with zipfile.ZipFile(export.build_zip_export("test")) as archive:
                        self.assertIn("test.pdf", archive.namelist())
                        self.assertTrue(archive.read("test.pdf").startswith(b"%PDF-"))

    def test_pdf_failure_does_not_return_a_partial_zip(self):
        with (
            patch.object(export.st, "session_state", self._state(1.0)),
            patch.object(export, "generate_pdf_report", side_effect=RuntimeError("PDF failed")),
        ):
            with self.assertRaisesRegex(RuntimeError, "PDF failed"):
                export.build_zip_export("test")


if __name__ == "__main__":
    unittest.main()
