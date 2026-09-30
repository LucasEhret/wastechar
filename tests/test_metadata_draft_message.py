import datetime as dt
import unittest
from unittest.mock import patch

import pandas as pd

from report_validation import metadata_errors
from ui import save_status


class MetadataDraftMessageTests(unittest.TestCase):
    def test_save_status_uses_account_time_zone(self):
        state = {
            "lang": "EN",
            "_save_status": "saved",
            "_last_saved_at": "2026-01-01T23:30:00+00:00",
            "user_timezone": "Europe/Zurich",
            "saved_operator_name": "Alice",
            "saved_sensor_name": "Sensor",
            "saved_test_date": dt.date(2026, 1, 1),
            "saved_nb_sample": 1,
            "_skip_collect_times_value": True,
        }
        with (
            patch.object(save_status.st, "session_state", state),
            patch.object(save_status.st, "success") as success,
        ):
            save_status.render_save_status()
        self.assertIn("00:30:00 CET", success.call_args.args[0])

    def test_sidebar_names_the_missing_time_field(self):
        state = {
            "lang": "EN",
            "_save_status": "saved",
            "saved_operator_name": "Alice",
            "saved_sensor_name": "Sensor",
            "saved_test_date": dt.date(2026, 9, 30),
            "saved_nb_sample": 1,
            "_skip_collect_times_value": False,
            "df_collect_times": pd.DataFrame([{
                "Echantillon": 1,
                "Heure de début": "",
                "Heure de fin": "11:00:00",
            }]),
        }
        with (
            patch.object(save_status.st, "session_state", state),
            patch.object(save_status.st, "success"),
            patch.object(save_status.st, "warning") as warning,
        ):
            errors = metadata_errors(state)
            save_status.render_save_status()

        self.assertEqual(len(errors), 1)
        self.assertIn("start time is missing", errors[0])
        self.assertIn("start time is missing", warning.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
