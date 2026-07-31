from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
REGULAR_FONT = FONT_DIR / "DejaVuSans.ttf"
BOLD_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"
if REGULAR_FONT.exists() and BOLD_FONT.exists():
    pdfmetrics.registerFont(TTFont("CAP-Regular", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("CAP-Bold", str(BOLD_FONT)))
    FONT_REGULAR, FONT_BOLD = "CAP-Regular", "CAP-Bold"
else:
    FONT_REGULAR, FONT_BOLD = "Helvetica", "Helvetica-Bold"


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CapTitle", parent=base["Title"], fontName=FONT_BOLD,
            fontSize=22, leading=27, alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"), spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "CapSubtitle", parent=base["Normal"], fontName=FONT_REGULAR,
            fontSize=10, leading=14, alignment=TA_CENTER,
            textColor=colors.HexColor("#5F6368"), spaceAfter=16,
        ),
        "heading": ParagraphStyle(
            "CapHeading", parent=base["Heading2"], fontName=FONT_BOLD,
            fontSize=13, leading=16, spaceBefore=12, spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "CapBody", parent=base["BodyText"], fontName=FONT_REGULAR,
            fontSize=9.2, leading=13, textColor=colors.HexColor("#222222"),
        ),
        "label": ParagraphStyle(
            "CapLabel", parent=base["BodyText"], fontName=FONT_BOLD,
            fontSize=8.3, leading=11,
        ),
        "value": ParagraphStyle(
            "CapValue", parent=base["BodyText"], fontName=FONT_REGULAR,
            fontSize=8.3, leading=11,
        ),
    }


def _table(rows: list, widths: list) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F3F3")),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("BOX", (0, 0), (-1, -1), .3, colors.HexColor("#D9DCDD")),
        ("INNERGRID", (0, 0), (-1, -1), .25, colors.HexColor("#D9DCDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _feasibility_table(rows: list[dict], styles: dict) -> Table:
    ordered = sorted(rows, key=lambda row: {"vert": 0, "orange": 1, "rouge": 2}.get(row["status"], 3))
    data = [[
        Paragraph("Élément", styles["label"]),
        Paragraph("Constat", styles["label"]),
        Paragraph("Action", styles["label"]),
    ]]
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F3F3")),
        ("BOX", (0, 0), (-1, -1), .3, colors.HexColor("#D9DCDD")),
        ("INNERGRID", (0, 0), (-1, -1), .25, colors.HexColor("#D9DCDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    backgrounds = {
        "vert": colors.HexColor("#E8F5E9"),
        "orange": colors.HexColor("#FFF3E0"),
        "rouge": colors.HexColor("#FDECEC"),
    }
    for index, row in enumerate(ordered, start=1):
        data.append([
            Paragraph(escape(row["criterion"]), styles["value"]),
            Paragraph(escape(row["observation"]), styles["value"]),
            Paragraph(escape(row["action"]), styles["value"]),
        ])
        commands.append(("BACKGROUND", (0, index), (-1, index), backgrounds[row["status"]]))
    table = Table(data, colWidths=[38 * mm, 63 * mm, 63 * mm], repeatRows=1)
    table.setStyle(TableStyle(commands))
    return table


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title="Synthèse CAP", author="CAP",
    )
    styles = _styles()

    recommended = list(result.get("recommended_platforms", []))
    retained = result.get("retained_platform")
    if result.get("strategic_status") != "Choix validé":
        result_title = "Projet à revoir"
        result_subtitle = "Aucune plateforme recommandée"
    elif len(recommended) > 1:
        result_title = "Plateformes recommandées par CAP"
        result_subtitle = " et ".join(recommended)
    else:
        result_title = recommended[0] if recommended else "Aucune recommandation"
        result_subtitle = "Plateforme recommandée"

    persona = (answers.get("q2") or ["Non renseigné"])[0]
    if persona == "Autre":
        persona = answers.get("custom_profile") or persona
    objective = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6")
    objective_line = (
        f"{objective or ''} — {answers.get('indicator', '')} : "
        f"{answers.get('target', '')} à {answers.get('deadline', '')}"
    )

    story = [
        Paragraph("CAP", styles["title"]),
        Paragraph("Synthèse du diagnostic", styles["subtitle"]),
        Paragraph(escape(result_title), styles["title"]),
        Paragraph(escape(result_subtitle), styles["subtitle"]),
    ]
    if retained:
        story.append(Paragraph(f"Plateforme retenue par le cabinet : {escape(retained)}", styles["subtitle"]))

    story.append(Paragraph("Données de décision", styles["heading"]))
    source_text = ", ".join(answers.get("q5", [])) or "Base de référence CAP"
    decision_rows = [[Paragraph("Élément", styles["label"]), Paragraph("Réponse", styles["label"])] ,
        [Paragraph("Persona analysé", styles["label"]), Paragraph(escape(persona), styles["value"])],
        [Paragraph("Besoin prioritaire", styles["label"]), Paragraph(escape(answers.get("priority_need", "")), styles["value"])],
        [Paragraph("Réseaux connus", styles["label"]), Paragraph(escape(", ".join(answers.get("q4", []))), styles["value"])],
        [Paragraph("Réseau le plus souvent utilisé", styles["label"]), Paragraph(escape(answers.get("q4_priority") or "Non identifié"), styles["value"])],
        [Paragraph("Source de l’information", styles["label"]), Paragraph(escape(source_text), styles["value"])],
        [Paragraph("Objectif", styles["label"]), Paragraph(escape(objective_line), styles["value"])],
        [Paragraph("Formats retenus", styles["label"]), Paragraph(escape(", ".join(answers.get("q14", []))), styles["value"])],
    ]
    story.append(_table(decision_rows, [48 * mm, 102 * mm]))

    story.append(Paragraph("Résultat du diagnostic", styles["heading"]))
    status_rows = [[Paragraph("Contrôle", styles["label"]), Paragraph("Résultat", styles["label"])],
        [Paragraph("Données stratégiques", styles["label"]), Paragraph(escape(result.get("strategic_status", "")), styles["value"])],
    ]
    if result.get("strategic_status") == "Choix validé":
        status_rows.extend([
            [Paragraph("Recommandation CAP", styles["label"]), Paragraph(escape(" et ".join(recommended)), styles["value"])],
            [Paragraph("Critère de départage", styles["label"]), Paragraph(escape(result.get("tie_break") or "Égalité reconnue"), styles["value"])],
            [Paragraph("Faisabilité", styles["label"]), Paragraph(escape(result.get("feasibility_label", "")), styles["value"])],
        ])
        if retained:
            status_rows.append([Paragraph("Choix du cabinet", styles["label"]), Paragraph(escape(retained), styles["value"])])
    story.append(_table(status_rows, [58 * mm, 92 * mm]))

    if result.get("selection_reasons"):
        story.append(Paragraph("Pourquoi cette recommandation ?", styles["heading"]))
        for reason in result["selection_reasons"]:
            story.append(Paragraph(f"• {escape(reason)}", styles["body"]))
            story.append(Spacer(1, 3))

    if result.get("strategic_status") == "Choix validé":
        story.append(PageBreak())
        story.append(Paragraph("Contrôle de la faisabilité", styles["heading"]))
        story.append(_feasibility_table(result.get("feasibility_rows", []), styles))
        actions = result.get("launch_actions", [])
        if actions:
            story.append(Paragraph("Actions à réaliser", styles["heading"]))
            for index, action in enumerate(actions, start=1):
                story.append(Paragraph(f"{index}. {escape(action)}", styles["body"]))
                story.append(Spacer(1, 3))
    else:
        actions = result.get("decision_notes", [])
        if actions:
            story.append(Paragraph("Actions nécessaires", styles["heading"]))
            for index, action in enumerate(actions, start=1):
                story.append(Paragraph(f"{index}. {escape(action)}", styles["body"]))
                story.append(Spacer(1, 3))

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "Cette synthèse est une aide à la décision fondée sur les réponses du cabinet et la base de référence CAP.",
            styles["subtitle"],
        ),
    ])
    document.build(story)
    return buffer.getvalue()
