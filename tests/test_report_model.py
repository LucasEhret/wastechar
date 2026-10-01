import datetime as dt
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid
import zipfile

import pandas as pd

import export
from report import Report, REPORT_FIELDS
from report_storage import serialize_report, deserialize_report
import session
from ui import report_state
from ui.tab_weighing import _save_and_open_summary


class ReportModelTests(unittest.TestCase):
    def report(self):
        return Report(
            facility="Site", operator="Alice", sensor="Sensor",
            test_date=dt.date(2026, 10, 1), material_classes=["Paper"],
            skip_collection_times=True,
            weighings=pd.DataFrame([{
                "__weighing_id": uuid.uuid4().hex, "N° échantillon": "1",
                "Classe de matériau": "Paper", "Contenant utilisé": "",
                "Poids brut": 2.0, "Tare": 0.0, "Poids net": 2.0,
                "Image": b"original photo bytes",
            }]),
        )

    def test_defaults_and_snapshots_do_not_share_mutable_report_data(self):
        first, second = Report(), Report()
        first.material_classes.append("Paper")
        first.containers.loc[0] = ["Bin", 2.0]
        self.assertEqual(second.material_classes, [])
        self.assertTrue(second.containers.empty)
        original = self.report()
        snapshot = original.snapshot()
        original.weighings.loc[0, "Poids net"] = 99.0
        original.material_classes.append("Glass")
        self.assertEqual(snapshot.weighings.iloc[0]["Poids net"], 2.0)
        self.assertEqual(snapshot.material_classes, ["Paper"])

    def test_initialization_moves_committed_fields_out_of_widget_state(self):
        native = {**self.report().to_state(), "_operator_name": "Uncommitted name",
                  "global_comment": "Uncommitted comment", "step_index": 2}
        with patch.object(report_state.st, "session_state", native):
            report = report_state.initialize_report()
            self.assertEqual(report.operator, "Alice")
            self.assertEqual(report.comment, "")
            self.assertFalse(set(REPORT_FIELDS) & native.keys())
            report_state.app_state["saved_operator_name"] = "Bob"
            self.assertEqual(report.operator, "Bob")
            self.assertNotIn("saved_operator_name", native)
            del native["_operator_name"]
            self.assertEqual(report.operator, "Bob")
            self.assertIs(report_state.initialize_report(), report)
            self.assertEqual(native["step_index"], 2)

    def test_codec_round_trip_needs_no_widget_or_streamlit_state(self):
        report = self.report()
        now = dt.datetime(2026, 10, 1, 12, tzinfo=dt.timezone.utc)
        context = Report(facility="Site", sensor="Sensor", material_classes=["Paper"])
        with patch.object(report_state.st, "session_state", None):
            restored, saved_at = deserialize_report(serialize_report(report, "alice", now), context)
        self.assertEqual(restored.operator, "Alice")
        self.assertEqual(saved_at, now.isoformat())
        self.assertEqual(restored.weighings.iloc[0]["Image"], b"original photo bytes")
        self.assertEqual(restored.material_classes, ["Paper"])
        self.assertEqual(context.operator, "")

    def test_export_accepts_report_without_accessing_streamlit_state(self):
        report = self.report()
        with patch.object(report_state.st, "session_state", None):
            with zipfile.ZipFile(export.build_zip_export("model", state=report)) as archive:
                self.assertIn("model.xlsx", archive.namelist())
                self.assertTrue(archive.read("model.pdf").startswith(b"%PDF-"))

    def test_save_and_restore_replace_canonical_report_and_keep_widget_separation(self):
        report = self.report()
        native = {"_report": report, "authentication_status": True, "username": "alice"}
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(session, "TEMP_DIR", Path(directory)),
            patch.object(report_state.st, "session_state", native),
            patch.object(session.st, "query_params", {"session": uuid.uuid4().hex}),
        ):
            self.assertTrue(session.save_session())
            report.operator = "Changed"
            native["_operator_name"] = "Stale widget"
            session.restore_session()
            self.assertEqual(native["_save_status"], "saved")
            self.assertEqual(native["_report"].operator, "Alice")
            self.assertNotIn("_operator_name", native)
            self.assertFalse(set(REPORT_FIELDS) & native.keys())
            self.assertEqual(native["_report"].weighings.iloc[0]["Image"], b"original photo bytes")

    def test_next_saves_into_canonical_report_and_preserves_live_widget_values(self):
        report = self.report()
        native = {"_report": report, "step_index": 2, "global_comment": "New observation"}
        with (
            patch.object(report_state.st, "session_state", native),
            patch("ui.tab_weighing.save_session", return_value=True),
        ):
            self.assertTrue(_save_and_open_summary())
        self.assertEqual(report.comment, "New observation")
        self.assertEqual(native["step_index"], 3)
        self.assertFalse(set(REPORT_FIELDS) & native.keys())

    def test_detach_allows_identity_reset_without_reusing_previous_report(self):
        native = {"_report": self.report(), "lang": "EN"}
        with patch.object(report_state.st, "session_state", native):
            report_state.detach_report()
            native.update(Report(facility="Other site").to_state())
            fresh = report_state.initialize_report()
        self.assertEqual(fresh.facility, "Other site")
        self.assertTrue(fresh.weighings.empty)
        self.assertEqual(native["lang"], "EN")


if __name__ == "__main__":
    unittest.main()
