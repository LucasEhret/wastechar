import datetime as dt
import io
import tempfile
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import dropbox
import dropbox.exceptions
import dropbox.files
from fpdf import FPDF

from config import APP_VERSION, WORKFLOW_MAP, ORDER_MAP
from helpers import get_sample_collect_times, get_weighing_collect_times
from data import summarize_by_material
from weights import invalid_weighing_rows
from report_validation import report_errors
from time_utils import DEFAULT_TIMEZONE, in_account_timezone, local_now, local_today


def upload_to_dropbox(buffer: io.BytesIO, file_name: str) -> bool:
    try:
        dbx = dropbox.Dropbox(
            app_key=st.secrets["DROPBOX_APP_KEY"],
            app_secret=st.secrets["DROPBOX_APP_SECRET"],
            oauth2_refresh_token=st.secrets["DROPBOX_REFRESH_TOKEN"],
        )
    except KeyError as e:
        st.error(f"Dropbox — clé de configuration manquante : {e}")
        return False
    except Exception as e:
        st.error(f"Dropbox — échec de l'authentification : {e}")
        return False

    path      = st.secrets.get("DROPBOX_DESTINATION_PATH", "/")
    full_path = f"{path}{file_name}".replace("//", "/")
    try:
        dbx.files_upload(
            buffer.getvalue(),
            full_path,
            mode=dropbox.files.WriteMode.overwrite,  # type: ignore
        )
        return True
    except dropbox.exceptions.AuthError as e:
        st.error(f"Dropbox — token expiré ou invalide : {e}")
    except dropbox.exceptions.ApiError as e:
        st.error(f"Dropbox — erreur API ({full_path}) : {e}")
    except Exception as e:
        st.error(f"Dropbox — erreur inattendue : {e}")
    return False


def build_excel_export(generated_at: dt.datetime | None = None) -> io.BytesIO:
    if errors := report_errors(st.session_state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    generated_at = in_account_timezone(
        generated_at or local_now(st.session_state.get("user_timezone")),
        st.session_state.get("user_timezone"),
    )
    buf         = io.BytesIO()
    df          = st.session_state["df_weighings"].copy()
    if invalid_weighing_rows(df):
        raise ValueError("Cannot export invalid weighing weights")
    sensor      = st.session_state["saved_sensor_name"]
    date        = st.session_state["saved_test_date"]
    facility    = st.session_state.get("facility_name", "")

    df_agg = (
        df.groupby(["N° échantillon", "Classe de matériau"], as_index=False)
        .agg(Poids_net=("Poids net", "sum"))
    )
    df_agg[["Début", "Fin"]] = pd.DataFrame(
        [get_weighing_collect_times(label) for label in df_agg["N° échantillon"]],
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
                times = get_sample_collect_times(sid)
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
        df_w        = st.session_state["df_weighings"]
        _wf_labels  = {0: "Single", 1: "Multiple"}
        _wfo_labels = {0: "Before weighing", 1: "After weighing"}
        pd.DataFrame([
            {"field": "Facility name",         "value": facility},
            {"field": "App Version",           "value": APP_VERSION},
            {"field": "Operator name",         "value": st.session_state["saved_operator_name"]},
            {"field": "Test date",             "value": str(st.session_state["saved_test_date"])},
            {"field": "Sensor name",           "value": sensor},
            {"field": "Sampling",              "value": _wf_labels.get(st.session_state.get("saved_workflow"), "—")},  # type: ignore
            {"field": "Sensor passage",        "value": _wfo_labels.get(st.session_state.get("saved_workflow_order"), "—")},  # type: ignore
            {"field": "Number of samples",     "value": st.session_state["saved_nb_sample"]},
            {"field": "Number of weighings",   "value": len(df_w)},
            {"field": "Total net weight (kg)", "value": round(df_w["Poids net"].sum(), 4) if not df_w.empty else 0},
            {"field": "Material classes used", "value": ", ".join(sorted(df_w["Classe de matériau"].unique())) if not df_w.empty else ""},
            {"field": "Containers used",       "value": ", ".join(sorted(df_w["Contenant utilisé"].replace("", pd.NA).dropna().unique())) if not df_w.empty else ""},
            {"field": "Global comment",        "value": st.session_state.get("_global_comment_value", "")},
            {"field": "Export timestamp",      "value": generated_at.isoformat(timespec="seconds")},
            {"field": "Time zone",             "value": st.session_state.get("user_timezone", DEFAULT_TIMEZONE)},
        ]).to_excel(writer, sheet_name="Metadata", index=False)

    buf.seek(0)
    return buf


def generate_pdf_report(generated_at: dt.datetime | None = None) -> bytes:
    if errors := report_errors(st.session_state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    generated_at = in_account_timezone(
        generated_at or local_now(st.session_state.get("user_timezone")),
        st.session_state.get("user_timezone"),
    )
    df_weighings   = st.session_state["df_weighings"]
    if invalid_weighing_rows(df_weighings):
        raise ValueError("Cannot export invalid weighing weights")
    facility       = st.session_state.get("facility_name", "")
    sensor         = st.session_state.get("saved_sensor_name", "-") or "-"
    _wf_label      = WORKFLOW_MAP.get(st.session_state.get("saved_workflow"), "-")  # type: ignore
    _wfo_label     = ORDER_MAP.get(st.session_state.get("saved_workflow_order"), "-")  # type: ignore
    operator       = st.session_state.get("saved_operator_name", "-") or "-"
    global_comment = st.session_state.get("_global_comment_value", "").strip()
    material_classes = st.session_state.get("material_classes", [])

    date_val = st.session_state.get("saved_test_date", local_today(st.session_state.get("user_timezone")))
    date_str = date_val.strftime('%d/%m/%Y') if hasattr(date_val, 'strftime') else str(date_val)

    total_pesees     = len(df_weighings)
    total_poids_brut = df_weighings["Poids brut"].sum() if not df_weighings.empty else 0.0
    total_poids_net  = df_weighings["Poids net"].sum()  if not df_weighings.empty else 0.0
    classes_present  = sorted(df_weighings["Classe de matériau"].unique().tolist()) if not df_weighings.empty else []
    classes_absent   = sorted(set(material_classes) - set(classes_present))
    df_summary       = summarize_by_material(df_weighings)

    class PDF(FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(140, 140, 140)
            self.cell(
                0, 6,
                txt=f"WasteFlow App {APP_VERSION}  |  Exporté le {generated_at.strftime('%d/%m/%Y à %H:%M %Z')}",
                align="C",
            )
            self.set_text_color(0, 0, 0)

    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    sec = 0

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, txt="Rapport de Caractérisation", align="C")
    pdf.ln(12)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 6, txt=f"Site : {facility}  |  Opérateur : {operator}  |  Date : {date_str}", align="C")
    pdf.ln(6)
    pdf.cell(0, 6, txt=f"Capteur : {sensor}  |  Échantillonnage : {_wf_label}", align="C")
    pdf.ln(6)
    pdf.cell(0, 6, txt=f"Passage du capteur : {_wfo_label}", align="C")
    pdf.ln(12)

    # 1. Global indicators
    sec += 1
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, txt=f"{sec}. Indicateurs Globaux")
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)
    for line in [
        f"- Nombre total de pesées enregistrées : {total_pesees}",
        f"- Masse brute totale : {total_poids_brut:.3f} kg",
        f"- Masse nette totale triée : {total_poids_net:.3f} kg",
    ]:
        pdf.cell(0, 7, txt=line)
        pdf.ln(7)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, txt="- Classes présentes :")
    pdf.ln(7)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, txt="  " + (", ".join(classes_present) if classes_present else "Aucune"))
    pdf.set_x(pdf.l_margin)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, txt="- Classes sans données :")
    pdf.ln(7)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 6, txt="  " + (", ".join(classes_absent) if classes_absent else "Aucune"))
    pdf.set_x(pdf.l_margin)

    if global_comment:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, txt="- Commentaire général :")
        pdf.ln(7)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, txt=f"  {global_comment}")
        pdf.set_x(pdf.l_margin)

    # 2. Collection times
    df_times = st.session_state.get("df_collect_times", pd.DataFrame())
    if not df_times.empty and not st.session_state.get("_skip_collect_times_value", False):
        sec += 1
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, txt=f"{sec}. Plages Horaires de Collecte")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        for header, w in [("Echantillon", 30), ("Date", 40), ("Heure de début", 60), ("Heure de fin", 60)]:
            pdf.cell(w, 8, txt=header, border=1, align="C")
        pdf.ln(8)
        pdf.set_font("Helvetica", size=10)
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
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, txt=f"{sec}. Répartition par Classe de Matériau")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(95, 8, txt="Classe de matériau", border=1, align="C")
        pdf.cell(47, 8, txt="Poids net (kg)", border=1, align="C")
        pdf.cell(48, 8, txt="% Masse totale", border=1, align="C")
        pdf.ln(8)
        pdf.set_font("Helvetica", size=10)
        for _, row in df_summary.iterrows():
            pdf.cell(95, 7, txt=str(row["Classe de matériau"]), border=1)
            pdf.cell(47, 7, txt=f"{row['Poids net']:.3f}", border=1, align="R")
            pdf.cell(48, 7, txt=f"{row['Pourcentage de la masse totale']:.1f} %", border=1, align="R")
            pdf.ln(7)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(95, 7, txt="TOTAL", border=1, align="C")
        pdf.cell(47, 7, txt=f"{total_poids_net:.3f}", border=1, align="R")
        pdf.cell(48, 7, txt="100.0 %" if total_poids_net > 0 else "0.0 %", border=1, align="R")
        pdf.ln(10)

        if total_poids_net > 0:
            plt.rcParams['axes.prop_cycle'] = plt.cycler(  # type: ignore
                color=['#00D494', '#0A3D2E', '#7A9E89', '#AC6F4E', '#DAB996', '#2B2420', "#D4E5DE", "#FFFFFF"]
            )
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(
                df_summary["Pourcentage de la masse totale"],
                labels=df_summary["Classe de matériau"],  # type: ignore
                autopct="%1.1f%%",
            )
            ax.set_title("Répartition par classe de matériau")
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=150)
            img_buf.seek(0)
            plt.close(fig)

            if pdf.get_y() + 95 > pdf.h - pdf.b_margin:
                pdf.add_page()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpf:
                tmpf.write(img_buf.getvalue())
                tmpf_path = tmpf.name
            pdf.image(tmpf_path, x=25, y=pdf.get_y(), w=160)
            pdf.ln(95)
            try:
                Path(tmpf_path).unlink(missing_ok=True)
            except Exception:
                pass

    output = pdf.output(dest="S")
    # PyFPDF returns a Latin-1 string; fpdf2 returns bytes or bytearray.
    return output.encode("latin-1") if isinstance(output, str) else bytes(output)


def build_zip_export(base_name: str | None = None, generated_at: dt.datetime | None = None) -> io.BytesIO:
    if errors := report_errors(st.session_state):
        raise ValueError("Cannot export incomplete report: " + "; ".join(errors))
    if invalid_weighing_rows(st.session_state["df_weighings"]):
        raise ValueError("Cannot export invalid weighing weights")
    buf         = io.BytesIO()
    generated_at = in_account_timezone(
        generated_at or local_now(st.session_state.get("user_timezone")),
        st.session_state.get("user_timezone"),
    )
    timestamp   = generated_at.strftime("%Y%m%d_%H%M%z")
    facility    = st.session_state.get("facility_name", "")
    sensor_name = st.session_state["saved_sensor_name"].replace(" ", "_")
    if base_name is None:
        base_name = f"Resultat_{facility}_{sensor_name}_{timestamp}"

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        excel_buf = build_excel_export(generated_at)
        zf.writestr(f"{base_name}.xlsx", excel_buf.read())

        pdf_data = generate_pdf_report(generated_at)
        zf.writestr(f"{base_name}.pdf", pdf_data)

        df_w = st.session_state["df_weighings"]
        if "Image" in df_w.columns:
            seen_classes: set = set()
            for _, row in df_w.iterrows():
                if isinstance(row["Image"], bytes) and row["Classe de matériau"] not in seen_classes:
                    seen_classes.add(row["Classe de matériau"])
                    class_safe = row["Classe de matériau"].replace(" ", "_").replace("/", "-")
                    zf.writestr(f"images/{class_safe}.jpg", row["Image"])

    buf.seek(0)
    return buf
