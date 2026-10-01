import unittest
from unittest.mock import patch

import pandas as pd

import table_entry
from weighing_identity import WEIGHING_ID_COLUMN


class TableCorrectionTests(unittest.TestCase):
    def test_correcting_saved_weight_updates_the_same_weighing(self):
        state = {
            "saved_nb_sample": 1,
            "saved_workflow": 0,
            "material_classes": ["Paper"],
            "df_containers": pd.DataFrame(columns=["Contenant", "Poids à vide"]),
            "df_weighings": pd.DataFrame(columns=[
                WEIGHING_ID_COLUMN, "__table_class", "N° échantillon",
                "Classe de matériau", "Contenant utilisé", "Poids brut", "Tare", "Poids net",
            ]),
            "weighing_error": "",
        }
        with (
            patch.object(table_entry.st, "session_state", state),
            patch.object(table_entry, "save_session", return_value=True),
            patch.object(table_entry.st, "toast"),
        ):
            draft = table_entry.make_table_draft(["Paper"], 1, True)
            draft.loc[0, "Poids brut"] = 10.0
            table_entry.save_table(draft)
            original_id = state["df_weighings"].iloc[0][WEIGHING_ID_COLUMN]

            correction = table_entry.make_table_draft(["Paper"], 1, True)
            correction.loc[0, "Poids brut"] = 12.0
            table_entry.save_table(correction)
            table_entry.save_table(table_entry.make_table_draft(["Paper"], 1, True))

        recorded = state["df_weighings"]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded.iloc[0][WEIGHING_ID_COLUMN], original_id)
        self.assertEqual(recorded.iloc[0]["Poids net"], 12.0)

    def test_pending_edits_rebase_on_saved_rows_without_copying_all_weighings(self):
        saved = pd.DataFrame([
            {"Classe de matériau": "Paper", "N° échantillon": 1,
             "Contenant utilisé": "", "Poids brut": 10.0},
            {"Classe de matériau": "Glass", "N° échantillon": 1,
             "Contenant utilisé": "", "Poids brut": None},
        ])
        edited_paper = saved.loc[[0]].copy()
        edited_paper.loc[0, "Poids brut"] = 12.0
        pending = table_entry.update_table_draft(saved, edited_paper, {})

        edited_glass = saved.loc[[1]].copy()
        edited_glass.loc[1, "Poids brut"] = 0.0
        pending = table_entry.update_table_draft(saved, edited_glass, pending)
        rebased = table_entry.apply_table_draft(saved, pending)

        self.assertEqual(rebased["Poids brut"].tolist(), [12.0, 0.0])
        self.assertEqual(set(pending), {"Paper", "Glass"})
        self.assertEqual(set(pending["Paper"]), {"Poids brut"})

        pending = table_entry.update_table_draft(saved, rebased.loc[[0]].assign(**{"Poids brut": 10.0}), pending)
        self.assertNotIn("Paper", pending)
        self.assertEqual(pending["Glass"]["Poids brut"], 0.0)

    def test_saving_one_row_preserves_an_unfinished_container_choice(self):
        state = {
            "saved_nb_sample": 1,
            "saved_workflow": 0,
            "df_containers": pd.DataFrame([{"Contenant": "Bin", "Poids à vide": 2.0}]),
            "df_weighings": pd.DataFrame(columns=[
                WEIGHING_ID_COLUMN, "__table_class", "N° échantillon",
                "Classe de matériau", "Contenant utilisé", "Poids brut", "Tare", "Poids net",
            ]),
            "weighing_error": "",
        }
        with (
            patch.object(table_entry.st, "session_state", state),
            patch.object(table_entry, "save_session", return_value=True),
            patch.object(table_entry.st, "toast"),
        ):
            draft = table_entry.make_table_draft(["Paper", "Glass"], 1, True)
            draft.loc[0, "Poids brut"] = 10.0
            draft.loc[1, "Contenant utilisé"] = "Bin"
            table_entry.save_table(draft)

            rebased = table_entry.apply_table_draft(
                table_entry.make_table_draft(["Paper", "Glass"], 1, True),
                state["_table_draft"],
            )

        self.assertEqual(len(state["df_weighings"]), 1)
        self.assertEqual(rebased.loc[1, "Contenant utilisé"], "Bin")
        self.assertTrue(pd.isna(rebased.loc[1, "Poids brut"]))


if __name__ == "__main__":
    unittest.main()
