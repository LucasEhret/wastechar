from contextlib import nullcontext
import inspect
import unittest
from unittest.mock import patch

import pandas as pd

import dialogs


class EditMaterialTests(unittest.TestCase):
    def edit_weight(self, configured, current, selected=None):
        state = {
            "material_classes": configured.copy(), "saved_nb_sample": 1,
            "df_containers": pd.DataFrame(columns=["Contenant", "Poids à vide"]),
            "df_weighings": pd.DataFrame([{
                "N° échantillon": "1", "Classe de matériau": current,
                "Contenant utilisé": "", "Poids brut": 10.0,
                "Tare": 0.0, "Poids net": 10.0,
            }]),
        }
        material_options = []

        def selectbox(label, options, index, **kwargs):
            if label == "Classe de matériau":
                material_options.extend(options)
                self.assertEqual(options[index], current)
                return selected if selected is not None else options[index]
            return options[index]

        with (
            patch.object(dialogs.st, "session_state", state),
            patch.object(dialogs.st, "markdown"),
            patch.object(dialogs.st, "multiselect", return_value=[1]),
            patch.object(dialogs.st, "selectbox", side_effect=selectbox),
            patch.object(dialogs.st, "number_input", return_value=12.0),
            patch.object(dialogs.st, "divider"),
            patch.object(dialogs.st, "columns", return_value=[nullcontext(), nullcontext()]),
            patch.object(dialogs.st, "button", side_effect=[True, False]),
            patch.object(dialogs.st, "toast"),
            patch.object(dialogs.st, "rerun"),
            patch.object(dialogs, "save_session", return_value=True) as save,
        ):
            inspect.unwrap(dialogs.dialog_modifier_pesee)(0)
        save.assert_called_once()
        self.assertEqual(state["material_classes"], configured)
        self.assertEqual(state["df_weighings"].loc[0, "Poids net"], 12.0)
        return state["df_weighings"].loc[0, "Classe de matériau"], material_options

    def test_weight_edit_preserves_current_material(self):
        for configured, current in (
            (["Paper", "Glass"], "Custom plastic"),
            ([], "Custom plastic"),
            (["Paper", "Glass"], "Glass"),
        ):
            with self.subTest(configured=configured, current=current):
                material, options = self.edit_weight(configured, current)
                self.assertEqual(material, current)
                self.assertEqual(options.count(current), 1)

    def test_operator_can_explicitly_change_custom_material(self):
        material, _ = self.edit_weight(["Paper", "Glass"], "Custom plastic", selected="Glass")
        self.assertEqual(material, "Glass")


if __name__ == "__main__":
    unittest.main()
