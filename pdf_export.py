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
from reportlab.graphics.shapes import Circle, Drawing, Path as DrawingPath, Polygon, String
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
REGULAR_FONT = FONT_DIR / "DejaVuSans.ttf"
BOLD_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"
if not (REGULAR_FONT.exists() and BOLD_FONT.exists()):
    SYSTEM_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
    REGULAR_FONT = SYSTEM_FONT_DIR / "DejaVuSans.ttf"
    BOLD_FONT = SYSTEM_FONT_DIR / "DejaVuSans-Bold.ttf"
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
        "action_eyebrow": ParagraphStyle(
            "CapActionEyebrow", parent=base["BodyText"], fontName=FONT_BOLD,
            fontSize=8.2, leading=10, textColor=colors.HexColor("#6B7280"),
        ),
        "action_number": ParagraphStyle(
            "CapActionNumber", parent=base["BodyText"], fontName=FONT_BOLD,
            fontSize=9, leading=12, textColor=colors.HexColor("#6B7280"),
        ),
    }


def _cap_logo() -> Drawing:
    """Version vectorielle du logo CAP pour conserver un rendu net dans le PDF."""
    drawing = Drawing(58, 58)
    black = colors.HexColor("#111111")
    drawing.add(Circle(29, 29, 17.5, fillColor=None, strokeColor=black, strokeWidth=2.2))

    upper = DrawingPath()
    upper.moveTo(9, 31)
    upper.curveTo(10, 47, 25, 56, 42, 50)
    upper.strokeColor = black
    upper.strokeWidth = 2.5
    upper.fillColor = None
    drawing.add(upper)
    drawing.add(Polygon([40, 55, 50, 49, 40, 45], fillColor=black, strokeColor=black))

    lower = DrawingPath()
    lower.moveTo(49, 27)
    lower.curveTo(47, 11, 31, 3, 15, 10)
    lower.strokeColor = black
    lower.strokeWidth = 2.5
    lower.fillColor = None
    drawing.add(lower)
    drawing.add(Polygon([17, 5, 7, 11, 17, 16], fillColor=black, strokeColor=black))

    drawing.add(String(
        29, 25.5, "CAP", fontName=FONT_BOLD, fontSize=11.5,
        fillColor=black, textAnchor="middle",
    ))
    drawing.hAlign = "CENTER"
    return drawing


def _decision_criterion(result: dict) -> str:
    labels = {
        "réseau observé auprès du persona": "Réseau réellement utilisé par le persona",
        "réseau le plus souvent utilisé par le persona": "Réseau le plus souvent utilisé par le persona",
        "objectif du cabinet": "Objectif du cabinet",
        "moyens du cabinet": "Moyens disponibles dans le cabinet",
        "égalité reconnue": "Égalité entre plusieurs plateformes",
        "égalité stratégique": "Égalité entre plusieurs plateformes",
    }
    value = result.get("tie_break") or "Égalité entre plusieurs plateformes"
    return labels.get(value, str(value).capitalize())


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


def _actions_box(actions: list[str], styles: dict, title: str, introduction: str) -> Table:
    data = [
        [Paragraph(escape(title.upper()), styles["action_eyebrow"]), ""],
        [Paragraph(escape(introduction), styles["body"]), ""],
    ]
    for index, action in enumerate(actions, start=1):
        data.append([
            Paragraph(f"{index:02d}", styles["action_number"]),
            Paragraph(escape(action), styles["body"]),
        ])

    commands = [
        ("SPAN", (0, 0), (1, 0)),
        ("SPAN", (0, 1), (1, 1)),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F8F8")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#222222")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]
    for row_index in range(2, len(data)):
        commands.append(("LINEABOVE", (0, row_index), (-1, row_index), .35, colors.HexColor("#D9DCDD")))

    table = Table(
        data,
        colWidths=[18 * mm, 146 * mm],
        style=TableStyle(commands),
        cornerRadii=[8, 8, 8, 8],
        spaceBefore=6,
        spaceAfter=8,
    )
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
        _cap_logo(),
        Spacer(1, 4),
        Paragraph("Synthèse du diagnostic", styles["subtitle"]),
        Paragraph(escape(result_title), styles["title"]),
        Paragraph(escape(result_subtitle), styles["subtitle"]),
    ]
    if retained:
        story.append(Paragraph(f"Plateforme choisie pour démarrer : {escape(retained)}", styles["subtitle"]))

    story.append(Paragraph("Données de décision", styles["heading"]))
    source_text = ", ".join(answers.get("q5", [])) or "Base de référence CAP"
    decision_rows = [[Paragraph("Élément", styles["label"]), Paragraph("Réponse", styles["label"])] ,
        [Paragraph("Persona analysé", styles["label"]), Paragraph(escape(persona), styles["value"])],
        [Paragraph("Besoin prioritaire", styles["label"]), Paragraph(escape(answers.get("priority_need", "")), styles["value"])],
        [Paragraph("Réseau le plus souvent utilisé", styles["label"]), Paragraph(escape(answers.get("q4_priority") or "Non identifié"), styles["value"])],
        [Paragraph("Source de l’information", styles["label"]), Paragraph(escape(source_text), styles["value"])],
        [Paragraph("Objectif", styles["label"]), Paragraph(escape(objective_line), styles["value"])],
        [Paragraph("Formats retenus", styles["label"]), Paragraph(escape(", ".join(answers.get("q14", []))), styles["value"])],
    ]
    story.append(_table(decision_rows, [48 * mm, 102 * mm]))

    story.append(Paragraph("Résultat du diagnostic", styles["heading"]))
    status_rows = [[Paragraph("Élément", styles["label"]), Paragraph("Résultat", styles["label"])]]
    if result.get("strategic_status") == "Choix validé":
        status_rows.extend([
            [Paragraph("Plateforme recommandée", styles["label"]), Paragraph(escape(" et ".join(recommended)), styles["value"])],
            [Paragraph("Élément déterminant", styles["label"]), Paragraph(escape(_decision_criterion(result)), styles["value"])],
            [Paragraph("Faisabilité", styles["label"]), Paragraph(escape(result.get("feasibility_label", "")), styles["value"])],
        ])
        if retained:
            status_rows.append([Paragraph("Plateforme choisie pour le lancement", styles["label"]), Paragraph(escape(retained), styles["value"])])
    else:
        status_rows.append([
            Paragraph("Résultat", styles["label"]),
            Paragraph("Aucune plateforme ne peut être recommandée à ce stade.", styles["value"]),
        ])
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
            story.append(_actions_box(
                actions,
                styles,
                "Préparation opérationnelle",
                "Réalisez ces actions avant de commencer.",
            ))
    else:
        actions = result.get("decision_notes", [])
        if actions:
            story.append(Paragraph("Actions nécessaires", styles["heading"]))
            story.append(_actions_box(
                actions,
                styles,
                "À corriger",
                "Corrigez ces éléments avant de relancer le diagnostic.",
            ))

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "Cette synthèse est une aide à la décision fondée sur les informations renseignées dans CAP.",
            styles["subtitle"],
        ),
    ])
    document.build(story)
    return buffer.getvalue()
