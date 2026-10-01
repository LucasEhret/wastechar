import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import data


SETUP = '''
import datetime as dt
import streamlit as st
from report import Report
from ui.report_state import initialize_report
if "_report" not in st.session_state:
    st.session_state.update(Report(facility="Site", operator="Alice", sensor="Sensor",
        test_date=dt.date(2026,10,1), material_classes=["Paper"],
        skip_collection_times=True).to_state())
    initialize_report()
for key, value in {"lang":"EN", "show_tutorials":False, "sensor_list":["Sensor"],
    "weighing_error":"", "metadata_error":"", "weighing_version":0,
    "image_uploader_key":0, "weighing_mode_index":0, "step_index":2,
    "skip_collect_times":True}.items():
    if key not in st.session_state:
        st.session_state[key]=value
'''


class StableControlTests(unittest.TestCase):
    def test_weighing_mode_and_empty_container_survive_language_change_and_deselect(self):
        app = AppTest.from_string(SETUP + "\nfrom ui.tab_weighing import render_tab_weighing\nrender_tab_weighing()\n").run()
        self.assertFalse(app.exception)
        app.button_group[0].set_value(1).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["weighing_mode_seg"], 1)
        self.assertEqual(app.selectbox(key="container_used").value, "")
        app.session_state["lang"] = "ES"
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["weighing_mode_index"], 1)
        self.assertEqual(app.selectbox(key="container_used").value, "")
        app.button_group[0].set_value(None).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["weighing_mode_index"], 1)

    def test_metadata_controls_keep_stable_values_across_languages(self):
        with patch.object(data, "save_session", return_value=True):
            app = AppTest.from_string(SETUP + "\nfrom ui.tab_metadata import render_tab_metadata\nrender_tab_metadata()\n").run()
            self.assertFalse(app.exception)
            app.button_group[0].set_value(1).run()
            app.button_group[1].set_value(1).run()
            self.assertFalse(app.exception)
            app.session_state["lang"] = "FR"
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["workflow_type_seg"], 1)
            self.assertEqual(app.session_state["workflow_order_seg"], 1)
            self.assertEqual(app.session_state["_report"].workflow, 1)
            self.assertEqual(app.session_state["_report"].sensor_passage, 1)
            app.button_group[0].set_value(None).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["_report"].workflow, 1)


if __name__ == "__main__":
    unittest.main()
