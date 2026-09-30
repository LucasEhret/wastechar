import datetime as dt
import io
import unittest
from unittest.mock import patch

import pandas as pd

from ui import export_controls


class OneClickExportTests(unittest.TestCase):
    def _state(self):
        return {
            "lang": "EN",
            "is_admin": True,
            "dropbox_upload_enabled": False,
            "facility_name": "Site",
            "user_timezone": "Europe/Zurich",
            "df_weighings": pd.DataFrame([{
                "N° échantillon": "1", "Classe de matériau": "Paper",
                "Contenant utilisé": "", "Poids brut": 1.0,
                "Tare": 0.0, "Poids net": 1.0,
            }]),
            "df_collect_times": pd.DataFrame(columns=["Echantillon"]),
            "saved_sensor_name": "Sensor",
            "saved_test_date": dt.date(2026, 9, 30),
            "saved_operator_name": "Alice",
            "saved_nb_sample": 1,
            "_skip_collect_times_value": True,
            "saved_workflow": 0,
            "saved_workflow_order": 0,
            "material_classes": ["Paper"],
        }

    def test_render_does_not_generate_and_click_returns_zip(self):
        state = self._state()
        moment = dt.datetime(2026, 9, 30, 12, tzinfo=dt.timezone.utc)
        with (
            patch.object(export_controls.st, "session_state", state),
            patch.object(export_controls.st, "download_button") as button,
            patch.object(export_controls, "local_now", return_value=moment),
            patch.object(export_controls, "build_zip_export", return_value=io.BytesIO(b"ZIP")) as build,
        ):
            export_controls.render_export_controls()
            build.assert_not_called()
            self.assertTrue(callable(button.call_args.kwargs["data"]))
            self.assertEqual(button.call_args.kwargs["data"](), b"ZIP")
            build.assert_called_once()

    def test_one_click_also_attempts_dropbox_upload(self):
        state = self._state()
        state["is_admin"] = False
        secrets = {
            "DROPBOX_APP_KEY": "key",
            "DROPBOX_APP_SECRET": "secret",
            "DROPBOX_REFRESH_TOKEN": "token",
        }
        with (
            patch.object(export_controls.st, "session_state", state),
            patch.object(export_controls.st, "secrets", secrets),
            patch.object(export_controls.st, "download_button") as button,
            patch.object(export_controls, "build_zip_export", return_value=io.BytesIO(b"ZIP")),
            patch.object(export_controls, "upload_to_dropbox", return_value=True) as upload,
        ):
            export_controls.render_export_controls()
            self.assertEqual(button.call_args.kwargs["data"](), b"ZIP")
        upload.assert_called_once()
        self.assertEqual(state["_export_upload_status"]["result"], True)


if __name__ == "__main__":
    unittest.main()
