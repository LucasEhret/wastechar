import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

import pandas as pd

import session


class SessionRecoveryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.token = uuid.uuid4().hex
        self.path = self.root / f"{self.token}.json"
        self.weighing_id = uuid.uuid4().hex
        self.state = {
            "authentication_status": True, "username": "alice",
            "facility_name": "Site", "user_timezone": "Europe/Zurich",
            "sensor_list": ["Sensor"],
            "df_weighings": pd.DataFrame([{
                "__weighing_id": self.weighing_id, "N° échantillon": "1",
                "Classe de matériau": "Paper", "Contenant utilisé": "Bin",
                "Poids brut": 12.0, "Tare": 2.0, "Poids net": 10.0,
                "Image": b"\x89PNG\r\n\x1a\n\x00\xff",
            }]),
            "df_containers": pd.DataFrame([{"Contenant": "Bin", "Poids à vide": 2.0}]),
            "df_collect_times": pd.DataFrame([{
                "Echantillon": 1, "Date": dt.date(2026, 10, 1),
                "Heure de début": "10:00:00", "Heure de fin": "11:00:00",
            }]),
            "saved_operator_name": "Alice", "saved_sensor_name": "Sensor",
            "saved_nb_sample": 1, "saved_test_date": dt.date(2026, 10, 1),
            "saved_workflow": 0, "saved_workflow_order": 1,
            "_global_comment_value": "Keep this report", "_skip_collect_times_value": False,
        }
        self.params = {"session": self.token}
        for patcher in (
            patch.object(session, "TEMP_DIR", self.root),
            patch.object(session.st, "session_state", self.state),
            patch.object(session.st, "query_params", self.params),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def save(self):
        self.assertTrue(session.save_session())
        return json.loads(self.path.read_text(encoding="utf-8"))

    def overwrite(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def assert_failed_restore_preserves_report(self):
        original = copy.deepcopy(self.state)
        with self.assertLogs(session.logger, level="ERROR"):
            session.restore_session()
        self.assertEqual(self.state["_save_status"], "restore_failed")
        self.assertEqual(set(original), set(self.state))
        for key, value in original.items():
            if isinstance(value, pd.DataFrame):
                pd.testing.assert_frame_equal(self.state[key], value)
            elif key != "_save_status":
                self.assertEqual(self.state[key], value)

    def test_round_trip_restores_photos_metadata_and_empty_tables(self):
        expected = copy.deepcopy(self.state)
        data = self.save()
        self.assertEqual(data["schema_version"], session.SESSION_SCHEMA_VERSION)
        self.state["saved_operator_name"] = "Changed"
        self.state["df_weighings"] = self.state["df_weighings"].iloc[0:0]
        self.state["_start_1"] = "stale"
        self.state["_table_draft"] = {"Paper": {"Poids brut": 99.0}}
        session.restore_session()
        self.assertEqual(self.state["saved_operator_name"], "Alice")
        self.assertEqual(self.state["_last_saved_at"], data["saved_at"])
        pd.testing.assert_frame_equal(self.state["df_weighings"], expected["df_weighings"])
        pd.testing.assert_frame_equal(self.state["df_collect_times"], expected["df_collect_times"])
        self.assertNotIn("_start_1", self.state)
        self.assertNotIn("_table_draft", self.state)
        for key in ("df_weighings", "df_containers", "df_collect_times"):
            self.state[key] = self.state[key].iloc[0:0]
        self.save()
        self.state["df_weighings"] = expected["df_weighings"]
        session.restore_session()
        for key in ("df_weighings", "df_containers", "df_collect_times"):
            self.assertTrue(self.state[key].empty)

    def test_failed_replace_preserves_previous_backup_and_cleans_temporary_file(self):
        self.save()
        previous = self.path.read_bytes()
        self.state["saved_operator_name"] = "Updated"
        with patch.object(session.os, "replace", side_effect=OSError("disk error")):
            with self.assertLogs(session.logger, level="ERROR"):
                self.assertFalse(session.save_session())
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(self.state["_save_status"], "save_failed")
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_failed_flush_preserves_previous_backup(self):
        self.save()
        previous = self.path.read_bytes()
        with patch.object(session.os, "fsync", side_effect=OSError("disk full")):
            with self.assertLogs(session.logger, level="ERROR"):
                self.assertFalse(session.save_session())
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_corrupt_late_metadata_does_not_partially_restore_tables(self):
        data = self.save()
        self.state["df_weighings"].loc[0, "Poids net"] = 99.0
        self.state["_start_1"] = "keep widget"
        data["metadata"]["date"] = "bad-date"
        self.overwrite(data)
        self.assert_failed_restore_preserves_report()

    def test_corrupt_photo_does_not_partially_restore_report(self):
        data = self.save()
        data["photos"][self.weighing_id] = "not-base64!"
        self.overwrite(data)
        self.assert_failed_restore_preserves_report()

    def test_unknown_schema_is_rejected_without_changing_report(self):
        data = self.save()
        data["schema_version"] = 999
        self.overwrite(data)
        self.assert_failed_restore_preserves_report()

    def test_missing_column_is_rejected_without_changing_report(self):
        data = self.save()
        rows = json.loads(data["df_containers"])
        del rows[0]["Poids à vide"]
        data["df_containers"] = json.dumps(rows)
        self.overwrite(data)
        self.assert_failed_restore_preserves_report()

    def test_legacy_bound_session_migrates_ids_tare_and_workflow_labels(self):
        data = self.save()
        del data["schema_version"]
        del data["photos"]
        del data["saved_at"]
        rows = json.loads(data["df_weighings"])
        del rows[0]["Tare"]
        del rows[0]["__weighing_id"]
        data["df_weighings"] = json.dumps(rows)
        data["metadata"]["workflow"] = "Single"
        data["metadata"]["workflow_order"] = "After weighing"
        self.overwrite(data)
        session.restore_session()
        self.assertEqual(self.state["_save_status"], "saved")
        weighing = self.state["df_weighings"].iloc[0]
        self.assertEqual(weighing["Tare"], 2.0)
        self.assertEqual(uuid.UUID(weighing["__weighing_id"]).hex, weighing["__weighing_id"])
        self.assertEqual(self.state["saved_workflow"], 0)
        self.assertEqual(self.state["saved_workflow_order"], 1)

    def test_other_identity_cannot_restore_overwrite_or_delete_backup(self):
        self.save()
        previous = self.path.read_bytes()
        for key, value in (("username", "bob"), ("facility_name", "Other site")):
            original = self.state[key]
            self.state[key] = value
            self.assert_failed_restore_preserves_report()
            with self.assertLogs(session.logger, level="ERROR"):
                self.assertFalse(session.save_session())
            session.clear_session()
            self.assertEqual(self.path.read_bytes(), previous)
            session.prepare_session_token()
            self.assertNotEqual(self.params["session"], self.token)
            self.params["session"] = self.token
            self.state[key] = original


if __name__ == "__main__":
    unittest.main()
