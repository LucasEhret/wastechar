import unittest
from unittest.mock import patch
import uuid

import pandas as pd

import table_entry
import data
from i18n import translate
from streamlit.testing.v1 import AppTest
from test_stable_controls import SETUP


class SharedWeighingModeTests(unittest.TestCase):
    def test_switching_from_manual_to_table_displays_the_same_saved_weighing(self):
        with patch.object(data, "save_session", return_value=True):
            app = AppTest.from_string(SETUP + "\nfrom ui.tab_weighing import render_tab_weighing\nrender_tab_weighing()\n").run()
            app.button_group[0].set_value(1).run()
            app.selectbox(key="material_class_0").set_value("Paper")
            app.text_input(key="gross_weight_0").set_value("5")
            next(button for button in app.button if button.label == translate("EN", "weigh_add_btn")).click().run()
            self.assertFalse(app.exception)
            weighing_id = app.session_state["_report"].weighings.iloc[0]["__weighing_id"]
            app.button_group[0].set_value(0).run()
            self.assertFalse(app.exception)
            grid = app.dataframe[0].value
            self.assertEqual(grid.loc[grid["Classe de matériau"] == "Paper", "Poids brut"].iloc[0], 5.0)
            self.assertEqual(len(app.session_state["_report"].weighings), 1)
            self.assertEqual(app.session_state["_report"].weighings.iloc[0]["__weighing_id"], weighing_id)

    def record(self, material="Paper", sample="1", gross=10.0):
        return {
            "__weighing_id": uuid.uuid4().hex, "N° échantillon": sample,
            "Classe de matériau": material, "Contenant utilisé": "",
            "Poids brut": gross, "Tare": 0.0, "Poids net": gross,
            "Image": b"original photo",
        }

    def state(self, records):
        return {
            "df_weighings": pd.DataFrame(records), "saved_nb_sample": 2,
            "saved_workflow": 1, "weighing_error": "",
            "df_containers": pd.DataFrame(columns=["Contenant", "Poids à vide"]),
        }

    def test_manual_and_custom_material_records_appear_and_save_without_duplicates(self):
        records = [self.record(), self.record("Custom material", sample="1, 2", gross=5.0)]
        state = self.state(records)
        with (
            patch.object(table_entry.st, "session_state", state),
            patch.object(table_entry, "save_session", return_value=True),
        ):
            draft = table_entry.make_table_draft(["Paper", "Glass"], 2, False)
            self.assertEqual(set(draft["Classe de matériau"]), {"Paper", "Glass", "Custom material"})
            custom = draft.loc[draft["Classe de matériau"] == "Custom material"].iloc[0]
            self.assertEqual(custom["N° échantillon"], "1, 2")
            self.assertEqual(custom["Poids brut"], 5.0)
            self.assertTrue(table_entry.save_table(draft))
        self.assertEqual(len(state["df_weighings"]), 2)
        self.assertEqual(state["df_weighings"]["Poids net"].sum(), 15.0)

    def test_table_edit_updates_the_manual_record_and_preserves_photo(self):
        record = self.record()
        state = self.state([record])
        with (
            patch.object(table_entry.st, "session_state", state),
            patch.object(table_entry, "save_session", return_value=True),
            patch.object(table_entry.st, "toast"),
        ):
            draft = table_entry.make_table_draft(["Paper"], 2, False)
            draft.loc[0, "Poids brut"] = 12.0
            self.assertTrue(table_entry.save_table(draft))
        saved = state["df_weighings"].iloc[0]
        self.assertEqual(len(state["df_weighings"]), 1)
        self.assertEqual(saved["__weighing_id"], record["__weighing_id"])
        self.assertEqual(saved["Image"], b"original photo")
        self.assertEqual(saved["Poids net"], 12.0)

    def test_multiple_weighings_of_same_material_have_independent_table_edits(self):
        records = [self.record(gross=10.0), self.record(sample="2", gross=20.0)]
        state = self.state(records)
        with (
            patch.object(table_entry.st, "session_state", state),
            patch.object(table_entry, "save_session", return_value=True),
            patch.object(table_entry.st, "toast"),
        ):
            baseline = table_entry.make_table_draft(["Paper"], 2, False)
            self.assertEqual(len(baseline), 2)
            edited = baseline.copy()
            edited.loc[0, "Poids brut"] = 12.0
            edits = table_entry.update_table_draft(baseline, edited, {})
            rebased = table_entry.apply_table_draft(baseline, edits)
            self.assertEqual(rebased["Poids brut"].tolist(), [12.0, 20.0])
            self.assertTrue(table_entry.save_table(rebased))
        self.assertEqual(state["df_weighings"]["Poids net"].tolist(), [12.0, 20.0])
        self.assertEqual(state["df_weighings"]["__weighing_id"].tolist(), [row["__weighing_id"] for row in records])


if __name__ == "__main__":
    unittest.main()
