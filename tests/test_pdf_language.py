import datetime as dt
import io
import unittest
from unittest.mock import patch

import pandas as pd
from pypdf import PdfReader

import export
from report import Report
from ui import export_controls


class PdfLanguageTests(unittest.TestCase):
    def report(self, language):
        date = dt.date(2026, 10, 1)
        return Report(
            language=language, facility="Site", operator="Alice", sensor="Sensor",
            test_date=date, comment="Original operator comment", material_classes=["Paper"],
            weighings=pd.DataFrame([{
                "N° échantillon": "1", "Classe de matériau": "Paper",
                "Contenant utilisé": "", "Poids brut": 1.0, "Tare": 0.0, "Poids net": 1.0,
            }]),
            collection_times=pd.DataFrame([{
                "Echantillon": 1, "Date": date,
                "Heure de début": "10:00:00", "Heure de fin": "11:00:00",
            }]),
        )

    def text(self, pdf):
        return "\n".join(page.extract_text() for page in PdfReader(io.BytesIO(pdf)).pages)

    def test_all_pdf_sections_and_chart_labels_use_report_language(self):
        cases = {
            "FR": ("Rapport de caractérisation", "Indicateurs globaux", "Plages horaires de collecte",
                   "Classe de matériau", "Exporté le", "Comparaison par classe de matériau", "Masse nette (kg)"),
            "EN": ("Characterization report", "Global indicators", "Collection time ranges",
                   "Material class", "Exported on", "Comparison by material class", "Net mass (kg)"),
            "ES": ("Informe de caracterización", "Indicadores globales", "Intervalos de recogida",
                   "Clase de material", "Exportado el", "Comparación por clase de material", "Masa neta (kg)"),
        }
        for language, expected in cases.items():
            with self.subTest(language=language), patch.object(
                export, "material_bar_chart", wraps=export.material_bar_chart
            ) as chart:
                text = self.text(export.generate_pdf_report(state=self.report(language)))
                for label in expected[:5]:
                    self.assertIn(label, text)
                self.assertIn("Original operator comment", text)
                self.assertEqual(chart.call_args.args[1:3], expected[5:7])
                if language != "FR":
                    self.assertNotIn("Passage du capteur", text)
                    self.assertNotIn("Commentaire général", text)

    def test_snapshot_keeps_selected_language_without_streamlit_access(self):
        native = {"_report": self.report("FR"), "lang": "ES"}
        with patch.object(export_controls.st, "session_state", native):
            snapshot = export_controls._report_snapshot()
            native["lang"] = "EN"
        self.assertEqual(snapshot.language, "ES")
        with patch.object(export_controls.st, "session_state", None):
            self.assertIn("Informe de caracterización", self.text(export.generate_pdf_report(state=snapshot)))


if __name__ == "__main__":
    unittest.main()
