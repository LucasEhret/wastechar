import copy
import datetime as dt
import unittest
from unittest.mock import patch
from contextlib import nullcontext

import pandas as pd

from ui import tab_weighing
from ui import tab_containers
import data
import table_entry


class SaveBeforeSummaryTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "lang": "EN", "step_index": 2, "saved_operator_name": "Alice",
            "saved_sensor_name": "Sensor", "saved_test_date": dt.date(2026, 10, 1),
            "saved_nb_sample": 1, "saved_workflow": 0,
            "_skip_collect_times_value": True, "material_classes": ["Paper", "Glass"],
            "df_containers": pd.DataFrame(columns=["Contenant", "Poids à vide"]),
            "df_weighings": pd.DataFrame(columns=[
                "__weighing_id", "__table_class", "N° échantillon", "Classe de matériau",
                "Contenant utilisé", "Poids brut", "Tare", "Poids net",
            ]),
            "weighing_error": "", "global_comment": "Latest observation",
            "_global_comment_value": "Old observation", "image_uploader_key": 0,
            "weighing_version": 0, "sample_nb": [1], "container_used": "",
        }
        for patcher in (
            patch.object(tab_weighing.st, "session_state", self.state),
            patch.object(tab_weighing.st, "error"),
            patch.object(tab_weighing.st, "warning"),
            patch.object(tab_weighing.st, "toast"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def draft(self, weight=10.0):
        rows = table_entry.make_table_draft(["Paper", "Glass"], 1, True)
        rows.loc[0, "Poids brut"] = weight
        return rows

    def test_next_saves_latest_table_and_comment_before_navigation(self):
        captured = {}

        def persist():
            self.assertEqual(self.state["step_index"], 2)
            captured.update(copy.deepcopy(self.state))
            return True

        with patch.object(table_entry, "save_session", side_effect=persist):
            self.assertTrue(tab_weighing._save_and_open_summary(self.draft()))
        self.assertEqual(self.state["step_index"], 3)
        self.assertEqual(captured["df_weighings"].iloc[0]["Poids net"], 10.0)
        self.assertEqual(captured["_global_comment_value"], "Latest observation")

    def test_next_corrects_saved_weighing_without_duplicating_it(self):
        with patch.object(table_entry, "save_session", return_value=True):
            table_entry.save_table(self.draft())
            original_id = self.state["df_weighings"].iloc[0]["__weighing_id"]
            self.assertTrue(tab_weighing._save_and_open_summary(self.draft(12.0)))
        self.assertEqual(len(self.state["df_weighings"]), 1)
        self.assertEqual(self.state["df_weighings"].iloc[0]["__weighing_id"], original_id)
        self.assertEqual(self.state["df_weighings"].iloc[0]["Poids net"], 12.0)

    def test_invalid_draft_blocks_navigation_without_changing_records(self):
        original = self.state["df_weighings"].copy()
        with patch.object(table_entry, "save_session") as persist:
            self.assertFalse(tab_weighing._save_and_open_summary(self.draft(-1.0)))
        persist.assert_not_called()
        self.assertEqual(self.state["step_index"], 2)
        self.assertTrue(self.state["weighing_error"])
        pd.testing.assert_frame_equal(self.state["df_weighings"], original)

    def test_failed_save_blocks_navigation_and_retry_does_not_duplicate(self):
        draft = self.draft()
        with patch.object(table_entry, "save_session", side_effect=[False, True]):
            self.assertFalse(tab_weighing._save_and_open_summary(draft))
            self.assertEqual(self.state["step_index"], 2)
            self.assertTrue(tab_weighing._save_and_open_summary(draft))
        self.assertEqual(self.state["step_index"], 3)
        self.assertEqual(len(self.state["df_weighings"]), 1)

    def test_unchanged_table_still_persists_comment_before_navigation(self):
        with patch.object(table_entry, "save_session", return_value=False) as persist:
            self.assertFalse(tab_weighing._save_and_open_summary(self.draft(float("nan"))))
        persist.assert_called_once()
        self.assertEqual(self.state["step_index"], 2)

    def test_manual_next_saves_submitted_entry_and_pending_table_edits(self):
        self.state["gross_weight_0"] = "5"
        self.state["material_class_0"] = "Custom material"
        self.state["_table_draft"] = {"Paper": {"Poids brut": 10.0}}
        with (
            patch.object(data, "save_session", return_value=True),
            patch.object(table_entry, "save_session", return_value=True),
            patch.object(tab_weighing.st, "rerun") as rerun,
        ):
            self.assertTrue(tab_weighing._save_and_open_summary(manual=True))
        rerun.assert_not_called()
        self.assertEqual(self.state["step_index"], 3)
        self.assertEqual(self.state["df_weighings"]["Poids net"].sum(), 15.0)
        self.assertEqual(set(self.state["df_weighings"]["Classe de matériau"]), {"Paper", "Custom material"})

    def test_manual_incomplete_entry_blocks_navigation(self):
        self.state["material_class_0"] = "Custom material"
        with patch.object(data, "save_session") as persist:
            self.assertFalse(tab_weighing._save_and_open_summary(manual=True))
        persist.assert_not_called()
        self.assertEqual(self.state["step_index"], 2)
        self.assertTrue(self.state["df_weighings"].empty)

    def test_empty_manual_form_only_saves_current_report(self):
        with (
            patch.object(tab_weighing, "save_session", return_value=True) as persist,
            patch.object(tab_weighing, "add_weighing") as add,
        ):
            self.assertTrue(tab_weighing._save_and_open_summary(manual=True))
        persist.assert_called_once()
        add.assert_not_called()

    def test_containers_next_adds_pending_entry_and_blocks_on_save_failure(self):
        for succeeds in (False, True):
            with self.subTest(succeeds=succeeds):
                self.state["step_index"] = 1
                self.state["show_tutorials"] = False
                self.state["container_name"] = "New bin"
                self.state["container_weight"] = 2.0
                self.state["container_error"] = ""
                self.state["df_containers"] = self.state["df_containers"].iloc[0:0]
                with (
                    patch.object(tab_containers.st, "columns", side_effect=lambda *args, **kwargs: [nullcontext(), nullcontext()]),
                    patch.object(tab_containers.st, "container", side_effect=lambda *args, **kwargs: nullcontext()),
                    patch.object(tab_containers.st, "markdown"),
                    patch.object(tab_containers.st, "text_input"),
                    patch.object(tab_containers.st, "number_input"),
                    patch.object(tab_containers.st, "write"),
                    patch.object(tab_containers.st, "info"),
                    patch.object(tab_containers.st, "button", side_effect=[False, False, True]),
                    patch.object(tab_containers.st, "rerun") as rerun,
                    patch.object(data, "save_session", return_value=succeeds),
                ):
                    tab_containers.render_tab_containers()
                self.assertEqual(self.state["step_index"], 2 if succeeds else 1)
                self.assertEqual(self.state["df_containers"].iloc[0]["Contenant"], "New bin")
                self.assertEqual(rerun.call_count, int(succeeds))


if __name__ == "__main__":
    unittest.main()
