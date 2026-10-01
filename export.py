from ui.report_state import app_state
import datetime as dt
import io
import logging
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from charts import material_bar_chart
from matplotlib import get_data_path
from matplotlib.ft2font import FT2Font
from PIL import Image, UnidentifiedImageError
import pandas as pd
import streamlit as st
import dropbox
import dropbox.files
from fpdf import FPDF

from config import APP_VERSION
from i18n import translate
from helpers import get_sample_collect_times, get_weighing_collect_times
from data import summarize_by_material
from weights import invalid_weighing_rows
from report_validation import report_errors
from time_utils import DEFAULT_TIMEZONE, in_account_timezone, local_now, local_today
from weighing_identity import ensure_weighing_ids
from report import Report


logger = logging.getLogger(__name__)


def safe_export_name(value: str) -> str:
    """Keep a readable filename without paths or Windows-reserved characters."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip(" .")
    return name or "report"


def _photo_extension(data: bytes) -> str:
    """Detect the original image format without transcoding or changing its bytes."""
    try:
        with Image.open(io.BytesIO(data)) as photo:
            return {"JPEG": ".jpg", "PNG": ".png"}.get(photo.format, ".bin")
    except (UnidentifiedImageError, OSError, ValueError):
        # Preserve an unrecognised attachment rather than losing it or mislabelling it.
        return ".bin"


def upload_to_dropbox(buffer: io.BytesIO, file_name: str, settings=None) -> bool:
    """Upload without Streamlit commands so deferred downloads can call this safely."""
    try:
        settings = st.secrets if settings is None else settings
        dbx = dropbox.Dropbox(
            app_key=settings["DROPBOX_APP_KEY"],
            app_secret=settings["DROPBOX_APP_SECRET"],
            oauth2_refresh_token=settings["DROPBOX_REFRESH_TOKEN"],
        )
    except Exception:
        logger.exception("Could not initialize Dropbox upload")
        return False

    path      = settings.get("DROPBOX_DESTINATION_PATH", "/")
    full_path = f"{path}{file_name}".replace("//", "/")
    try:
        dbx.files_upload(
            buffer.getvalue(),
            full_path,
            mode=dropbox.files.WriteMode.overwrite,  # type: ignore
        )
        return True
    except Exception:
        logger.exception("Could not upload export to Dropbox")
    return False


def build_excel_export(generated_at: dt.datetime | None = None, state=None) -> io.BytesIO:
    state = Report.from_state(app_state) if state is None else (
        state if isinstance(state, Report) else Report.from_state(state)
    )
    if errors := report_errors(state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    generated_at = in_account_timezone(
        generated_at or local_now(state.timezone),
        state.timezone,
    )
    buf         = io.BytesIO()
    df          = state.weighings.copy()
    if invalid_weighing_rows(df):
        raise ValueError("Cannot export invalid weighing weights")
    sensor      = state.sensor
    date        = state.test_date
    facility    = state.facility

    df_agg = (
        df.groupby(["N° échantillon", "Classe de matériau"], as_index=False)
        .agg(Poids_net=("Poids net", "sum"))
    )
    df_agg[["Début", "Fin"]] = pd.DataFrame(
        [get_weighing_collect_times(label, state) for label in df_agg["N° échantillon"]],
        index=df_agg.index,
    )
    sample_totals = (
        df_agg.groupby("N° échantillon")["Poids_net"]
        .sum()
        .rename("Masse totale échantillon")
    )
    df_agg = df_agg.merge(sample_totals, left_on="N° échantillon", right_index=True, how="left")
    df_agg["% of sample total"] = (
        df_agg["Poids_net"] / df_agg["Masse totale échantillon"].where(
            df_agg["Masse totale échantillon"] > 0
        ) * 100
    ).fillna(0.0)

    grand_total = df_agg["Poids_net"].sum()
    df_agg["% of grand total"] = df_agg["Poids_net"] / grand_total * 100 if grand_total > 0 else 0.0
    df_agg["sensor name"] = sensor
    df_agg["date"]        = date

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:

        # Global sheet
        sheet1 = df_agg[[
            "sensor name", "date",
            "N° échantillon", "Début", "Fin",
            "Classe de matériau", "Poids_net", "% of grand total",
        ]].rename(columns={
            "N° échantillon":     "sample number",
            "Début":              "start time",
            "Fin":                "end time",
            "Classe de matériau": "Material class",
            "Poids_net":          "Net weight (kg)",
        })
        total_row = pd.DataFrame([{
            "sensor name": sensor, "date": date,
            "sample number": "TOTAL", "start time": "", "end time": "",
            "Material class": "", "Net weight (kg)": grand_total,
            "% of grand total": 100.0 if grand_total > 0 else 0.0,
        }])
        sheet1 = pd.concat([sheet1, total_row], ignore_index=True)
        sheet1.to_excel(writer, sheet_name="Global results", index=False)

        # Per-sample sheets
        for sample_id in sorted(df_agg["N° échantillon"].unique()):
            sample_id_list = [int(s.strip()) for s in str(sample_id).split(",")]
            time_rows = []
            for sid in sample_id_list:
                times = get_sample_collect_times(sid, state)
                time_rows.append({
                    "Echantillon": sid,
                    "Début": str(times["Début"]) if times else "",
                    "Fin":   str(times["Fin"])   if times else "",
                })
            times_df = pd.DataFrame(time_rows)

            df_sample = (
                df_agg[df_agg["N° échantillon"] == sample_id]
                [["Classe de matériau", "Poids_net", "% of sample total"]]
                .rename(columns={
                    "Classe de matériau": "Material class",
                    "Poids_net":          "Net weight (kg)",
                })
                .copy()
            )
            df_sample = pd.concat([df_sample, pd.DataFrame([{
                "Material class": "TOTAL",
                "Net weight (kg)": df_sample["Net weight (kg)"].sum(),
                "% of sample total": 100.0 if df_sample["Net weight (kg)"].sum() > 0 else 0.0,
            }])], ignore_index=True)

            sheet_name = f"Sample {sample_id}"[:31]
            times_df.to_excel( writer, sheet_name=sheet_name, index=False, startrow=0)
            df_sample.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(times_df) + 2)

        # Metadata sheet
        df_w        = state.weighings
        _wf_labels  = {0: "Single", 1: "Multiple"}
        _wfo_labels = {0: "Before weighing", 1: "After weighing"}
        pd.DataFrame([
            {"field": "Facility name",         "value": facility},
            {"field": "App Version",           "value": APP_VERSION},
            {"field": "Operator name",         "value": state.operator},
            {"field": "Test date",             "value": str(state.test_date)},
            {"field": "Sensor name",           "value": sensor},
            {"field": "Sampling",              "value": _wf_labels.get(state.workflow, "—")},  # type: ignore
            {"field": "Sensor passage",        "value": _wfo_labels.get(state.sensor_passage, "—")},  # type: ignore
            {"field": "Number of samples",     "value": state.sample_count},
            {"field": "Number of weighings",   "value": len(df_w)},
            {"field": "Total net weight (kg)", "value": round(df_w["Poids net"].sum(), 4) if not df_w.empty else 0},
            {"field": "Material classes used", "value": ", ".join(sorted(df_w["Classe de matériau"].unique())) if not df_w.empty else ""},
            {"field": "Containers used",       "value": ", ".join(sorted(df_w["Contenant utilisé"].replace("", pd.NA).dropna().unique())) if not df_w.empty else ""},
            {"field": "Global comment",        "value": state.comment},
            {"field": "Export timestamp",      "value": generated_at.isoformat(timespec="seconds")},
            {"field": "Time zone",             "value": state.timezone},
        ]).to_excel(writer, sheet_name="Metadata", index=False)

        # This workbook contains values only. Openpyxl otherwise interprets text
        # beginning with '=' as a formula, and strings such as '#N/A' as errors.
        for worksheet in writer.book.worksheets:
            for cells in worksheet.iter_rows():
                for cell in cells:
                    if isinstance(cell.value, str):
                        cell.data_type = "s"

    buf.seek(0)
    return buf


def generate_pdf_report(generated_at: dt.datetime | None = None, state=None) -> bytes:
    # PyFPDF caches font metrics alongside font files. Use a private directory so
    # neither PDF implementation needs write access to installed package assets.
    with tempfile.TemporaryDirectory(prefix="wastechar_pdf_") as directory:
        fonts = Path(get_data_path()) / "fonts" / "ttf"
        for filename in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf"):
            shutil.copyfile(fonts / filename, Path(directory) / filename)
        return _generate_pdf_report(generated_at, state, Path(directory))


def _generate_pdf_report(generated_at, state, font_directory: Path) -> bytes:
    state = Report.from_state(app_state) if state is None else (
        state if isinstance(state, Report) else Report.from_state(state)
    )
    if errors := report_errors(state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    generated_at = in_account_timezone(
        generated_at or local_now(state.timezone),
        state.timezone,
    )
    def tr(key, **kwargs):
        return translate(state.language, key, **kwargs)

    df_weighings   = state.weighings
    if invalid_weighing_rows(df_weighings):
        raise ValueError("Cannot export invalid weighing weights")
    facility       = state.facility
    sensor         = state.sensor or "-"
    _wf_label      = tr("meta_wf_standard" if state.workflow == 0 else "meta_wf_multi")  # type: ignore
    _wfo_label     = tr("meta_wfo_order_a" if state.sensor_passage == 0 else "meta_wfo_order_b")  # type: ignore
    operator       = state.operator or "-"
    global_comment = state.comment.strip()
    material_classes = state.material_classes

    date_val = state.test_date
    date_str = date_val.strftime('%d/%m/%Y') if hasattr(date_val, 'strftime') else str(date_val)

    total_pesees     = len(df_weighings)
    total_poids_brut = df_weighings["Poids brut"].sum() if not df_weighings.empty else 0.0
    total_poids_net  = df_weighings["Poids net"].sum()  if not df_weighings.empty else 0.0
    classes_present  = sorted(df_weighings["Classe de matériau"].unique().tolist()) if not df_weighings.empty else []
    classes_absent   = sorted(set(material_classes) - set(classes_present))
    df_summary       = summarize_by_material(df_weighings)

    class PDF(FPDF):
        def normalize_text(self, text):
            # Unsupported glyphs must not make the entire ZIP unavailable.
            # The Excel report retains the original text in full.
            text = "".join(char if ord(char) in supported_glyphs or char in "\n\r\t"
                           else "?" for char in text)
            return super().normalize_text(text)

        def footer(self):
            self.set_y(-12)
            self.set_font("DejaVu", "I", 8)
            self.set_text_color(140, 140, 140)
            self.cell(
                0, 6,
                txt=tr("pdf_footer", version=APP_VERSION, date=generated_at.strftime("%d/%m/%Y"), time=generated_at.strftime("%H:%M %Z")),
                align="C",
            )
            self.set_text_color(0, 0, 0)

    pdf = PDF(orientation="P", unit="mm", format="A4")
    font_styles = {"": "DejaVuSans.ttf", "B": "DejaVuSans-Bold.ttf", "I": "DejaVuSans-Oblique.ttf"}
    supported_glyphs = set.intersection(*(
        set(FT2Font(str(font_directory / filename)).get_charmap())
        for filename in font_styles.values()
    ))
    # Legacy PyFPDF's TrueType subsetting supports the basic multilingual plane.
    import fpdf
    if int(fpdf.__version__.split(".")[0]) < 2:
        supported_glyphs = {code for code in supported_glyphs if code <= 0xFFFF}
    for style, filename in font_styles.items():
        pdf.add_font("DejaVu", style, str(font_directory / filename), uni=True)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    sec = 0

    # Header
    pdf.set_font("DejaVu", "B", 18)
    pdf.cell(0, 12, txt=tr("pdf_title"), align="C")
    pdf.ln(12)
    pdf.set_font("DejaVu", "I", 11)
    pdf.cell(0, 6, txt=tr("pdf_header_site", facility=facility, operator=operator, date=date_str), align="C")
    pdf.ln(6)
    pdf.cell(0, 6, txt=tr("pdf_header_sensor", sensor=sensor, sampling=_wf_label), align="C")
    pdf.ln(6)
    pdf.cell(0, 6, txt=tr("pdf_header_passage", passage=_wfo_label), align="C")
    pdf.ln(12)

    # 1. Global indicators
    sec += 1
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, txt=f"{sec}. {tr('pdf_overview')}")
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("DejaVu", size=11)
    for line in [
        "- " + tr("pdf_count", count=total_pesees),
        "- " + tr("pdf_gross", weight=total_poids_brut),
        "- " + tr("pdf_net", weight=total_poids_net),
    ]:
        pdf.cell(0, 7, txt=line)
        pdf.ln(7)

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 7, txt="- " + tr("pdf_present") + " :")
    pdf.ln(7)
    pdf.set_font("DejaVu", size=10)
    pdf.multi_cell(0, 6, txt="  " + (", ".join(classes_present) if classes_present else tr("pdf_none")))
    pdf.set_x(pdf.l_margin)

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 7, txt="- " + tr("pdf_absent") + " :")
    pdf.ln(7)
    pdf.set_font("DejaVu", "I", 10)
    pdf.multi_cell(0, 6, txt="  " + (", ".join(classes_absent) if classes_absent else tr("pdf_none")))
    pdf.set_x(pdf.l_margin)

    if global_comment:
        pdf.ln(2)
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(0, 7, txt="- " + tr("pdf_comment") + " :")
        pdf.ln(7)
        pdf.set_font("DejaVu", "I", 10)
        pdf.multi_cell(0, 6, txt=f"  {global_comment}")
        pdf.set_x(pdf.l_margin)

    # 2. Collection times
    df_times = state.collection_times
    if not df_times.empty and not state.skip_collection_times:
        sec += 1
        pdf.ln(6)
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 10, txt=f"{sec}. {tr('pdf_collection')}")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 10)
        for header, w in [(tr("pdf_sample"), 30), (tr("pdf_date"), 40), (tr("pdf_start"), 60), (tr("pdf_end"), 60)]:
            pdf.cell(w, 8, txt=header, border=1, align="C")
        pdf.ln(8)
        pdf.set_font("DejaVu", size=10)
        for _, row in df_times.iterrows():
            dv = row["Date"]
            ds = dv.strftime('%d/%m/%Y') if hasattr(dv, 'strftime') else str(dv)
            pdf.cell(30, 7, txt=str(row["Echantillon"]),    border=1, align="C")
            pdf.cell(40, 7, txt=ds,                          border=1, align="C")
            pdf.cell(60, 7, txt=str(row["Heure de début"]), border=1, align="C")
            pdf.cell(60, 7, txt=str(row["Heure de fin"]),   border=1, align="C")
            pdf.ln(7)
        pdf.ln(4)

    # 3. Material distribution
    if not df_summary.empty:
        sec += 1
        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 10, txt=f"{sec}. {tr('pdf_distribution')}")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(95, 8, txt=tr("pdf_material"), border=1, align="C")
        pdf.cell(47, 8, txt=tr("pdf_net_column"), border=1, align="C")
        pdf.cell(48, 8, txt=tr("pdf_percentage"), border=1, align="C")
        pdf.ln(8)
        pdf.set_font("DejaVu", size=10)
        for _, row in df_summary.iterrows():
            pdf.cell(95, 7, txt=str(row["Classe de matériau"]), border=1)
            pdf.cell(47, 7, txt=f"{row['Poids net']:.3f}", border=1, align="R")
            pdf.cell(48, 7, txt=f"{row['Pourcentage de la masse totale']:.1f} %", border=1, align="R")
            pdf.ln(7)
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(95, 7, txt=tr("pdf_total"), border=1, align="C")
        pdf.cell(47, 7, txt=f"{total_poids_net:.3f}", border=1, align="R")
        pdf.cell(48, 7, txt="100.0 %" if total_poids_net > 0 else "0.0 %", border=1, align="R")
        pdf.ln(10)

        if total_poids_net > 0:
            # Split large comparisons across pages so every material stays legible.
            for offset in range(0, len(df_summary), 12):
                chart_rows = df_summary.iloc[offset:offset + 12]
                fig = material_bar_chart(chart_rows, tr("pdf_chart"), tr("pdf_axis"))
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=150)
                img_buf.seek(0)
                with Image.open(img_buf) as image:
                    image_height = 180 * image.height / image.width
                img_buf.seek(0)
                if pdf.get_y() + image_height > pdf.h - pdf.b_margin:
                    pdf.add_page()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpf:
                    tmpf.write(img_buf.getvalue())
                    tmpf_path = tmpf.name
                try:
                    pdf.image(tmpf_path, x=15, y=pdf.get_y(), w=180)
                    pdf.ln(image_height + 4)
                finally:
                    Path(tmpf_path).unlink(missing_ok=True)

    output = pdf.output(dest="S")
    # PyFPDF returns a Latin-1 string; fpdf2 returns bytes or bytearray.
    return output.encode("latin-1") if isinstance(output, str) else bytes(output)


def build_zip_export(base_name: str | None = None, generated_at: dt.datetime | None = None, state=None) -> io.BytesIO:
    state = Report.from_state(app_state) if state is None else (
        state if isinstance(state, Report) else Report.from_state(state)
    )
    if errors := report_errors(state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    if invalid_weighing_rows(state.weighings):
        raise ValueError("Cannot export invalid weighing weights")
    buf         = io.BytesIO()
    generated_at = in_account_timezone(
        generated_at or local_now(state.timezone),
        state.timezone,
    )
    timestamp   = generated_at.strftime("%Y%m%d_%H%M%z")
    facility    = state.facility
    sensor_name = state.sensor.replace(" ", "_")
    if base_name is None:
        base_name = f"Resultat_{facility}_{sensor_name}_{timestamp}"
    base_name = safe_export_name(base_name)

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        excel_buf = build_excel_export(generated_at, state)
        zf.writestr(f"{base_name}.xlsx", excel_buf.read())

        pdf_data = generate_pdf_report(generated_at, state)
        zf.writestr(f"{base_name}.pdf", pdf_data)

        df_w = state.weighings
        if "Image" in df_w.columns:
            for _, row in ensure_weighing_ids(df_w).iterrows():
                if isinstance(row["Image"], bytes):
                    class_safe = safe_export_name(row["Classe de matériau"].replace(" ", "_"))[:100]
                    filename = f"{class_safe}_{row['__weighing_id']}{_photo_extension(row['Image'])}"
                    zf.writestr(f"images/{filename}", row["Image"])

    buf.seek(0)
    return buf
