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

            correction = state["weighing_table"].copy()
            correction.loc[0, "Poids brut"] = 12.0
            table_entry.save_table(correction)
            table_entry.save_table(state["weighing_table"].copy())

        recorded = state["df_weighings"]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded.iloc[0][WEIGHING_ID_COLUMN], original_id)
        self.assertEqual(recorded.iloc[0]["Poids net"], 12.0)


if __name__ == "__main__":
    unittest.main()
