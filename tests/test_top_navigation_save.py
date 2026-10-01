import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import data
import table_entry
from ui import tab_weighing
from test_stable_controls import SETUP


SCRIPT = SETUP + '''
from ui.navigation import sync_navigation
from ui.tab_weighing import render_tab_weighing
st.session_state["seg_nav"] = st.session_state["step_index"]
st.segmented_control("Navigation", options=[0,1,2,3], key="seg_nav", on_change=sync_navigation)
if st.session_state["step_index"] == 2:
    render_tab_weighing()
else:
    st.write("Summary")
'''


class TopNavigationSaveTests(unittest.TestCase):
    def test_top_summary_saves_latest_manual_entry_before_widget_cleanup(self):
        with (
            patch.object(data, "save_session", return_value=True),
            patch.object(tab_weighing, "save_session", return_value=True),
        ):
            app = AppTest.from_string(SCRIPT).run()
            app.button_group[1].set_value(1).run()
            app.selectbox(key="material_class_0").set_value("Paper")
            app.text_input(key="gross_weight_0").set_value("5")
            app.button_group[0].set_value(3).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["step_index"], 3)
        self.assertEqual(app.session_state["_report"].weighings.iloc[0]["Poids net"], 5.0)

    def test_invalid_draft_or_failed_save_keeps_top_navigation_on_weighing(self):
        for weight, save_succeeds in ((-1.0, True), (10.0, False), (10.0, True)):
            with self.subTest(weight=weight, save_succeeds=save_succeeds), patch.object(
                table_entry, "save_session", return_value=save_succeeds
            ):
                app = AppTest.from_string(SCRIPT).run()
                app.session_state["_table_draft"] = {"Paper": {"Poids brut": weight}}
                app.run()
                app.button_group[0].set_value(3).run()
                self.assertFalse(app.exception)
                expected = 3 if weight >= 0 and save_succeeds else 2
                self.assertEqual(app.session_state["step_index"], expected)
                self.assertEqual(app.session_state["seg_nav"], expected)


if __name__ == "__main__":
    unittest.main()
