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
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
REGULAR_FONT = FONT_DIR / "DejaVuSans.ttf"
BOLD_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"

if REGULAR_FONT.exists() and BOLD_FONT.exists():
    pdfmetrics.registerFont(TTFont("CAP-Regular", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("CAP-Bold", str(BOLD_FONT)))
    FONT_REGULAR = "CAP-Regular"
    FONT_BOLD = "CAP-Bold"
else:
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


def _document(buffer: BytesIO, title: str) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title=title,
        author="CAP",
    )


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CapTitle",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=23,
            leading=27,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "CapSubtitle",
            parent=base["Normal"],
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5F6368"),
            spaceAfter=18,
        ),
        "heading": ParagraphStyle(
            "CapHeading",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#111111"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "CapBody",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#222222"),
        ),
        "label": ParagraphStyle(
            "CapLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
        ),
        "value": ParagraphStyle(
            "CapValue",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=11,
        ),
    }


def _table(rows: list, widths: list) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F3F3")),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
                ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#D9DCDD")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9DCDD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = _document(buffer, "Synthèse CAP")
    styles = _styles()

    winner = result.get("winner")
    observation = result.get("observation_platform")
    tied = result.get("tied_platforms", [])
    if winner:
        recommendation = winner
        recommendation_label = "Plateforme recommandée"
    elif observation:
        recommendation = observation
        recommendation_label = "Plateforme retenue pour la période d’observation"
    elif tied:
        recommendation = "Plateformes équivalentes"
        recommendation_label = ", ".join(tied)
    else:
        recommendation = "Recommandation impossible"
        recommendation_label = "Informations stratégiques à compléter"

    story = [
        Paragraph("CAP", styles["title"]),
        Paragraph("Synthèse du diagnostic", styles["subtitle"]),
        Paragraph(escape(recommendation), styles["title"]),
        Paragraph(escape(recommendation_label), styles["subtitle"]),
        Paragraph("Données de décision", styles["heading"]),
    ]

    objective = (
        f"{answers.get('q6', '')} — {answers.get('indicator', '')} : "
        f"{answers.get('target', '')} à {answers.get('deadline', '')}"
    )
    decision_rows = [
        [Paragraph("Élément", styles["label"]), Paragraph("Réponse", styles["label"])],
        [
            Paragraph("Profils ciblés", styles["label"]),
            Paragraph(escape(", ".join(answers.get("q2", []))), styles["value"]),
        ],
        [
            Paragraph("Besoin prioritaire", styles["label"]),
            Paragraph(
                escape(answers.get("priority_need", "") or "Non renseigné"),
                styles["value"],
            ),
        ],
        [
            Paragraph("Canaux d’information", styles["label"]),
            Paragraph(
                escape(", ".join(answers.get("q4", [])) or "Non identifiés"),
                styles["value"],
            ),
        ],
        [
            Paragraph("Mode d’accès", styles["label"]),
            Paragraph(
                escape(", ".join(answers.get("q4_modes", [])) or "Non identifié"),
                styles["value"],
            ),
        ],
        [
            Paragraph("Objectif", styles["label"]),
            Paragraph(escape(objective), styles["value"]),
        ],
        [
            Paragraph("Traitement éditorial", styles["label"]),
            Paragraph(escape(answers.get("q6_treatment", "")), styles["value"]),
        ],
        [
            Paragraph("Effet recherché", styles["label"]),
            Paragraph(escape(answers.get("q6_effect", "")), styles["value"]),
        ],
        [
            Paragraph("Formats retenus", styles["label"]),
            Paragraph(
                escape(", ".join(answers.get("q14", [])) or "Non définis"),
                styles["value"],
            ),
        ],
    ]
    story.append(_table(decision_rows, [46 * mm, 104 * mm]))

    story.append(Paragraph("Décision", styles["heading"]))
    status_rows = [
        [Paragraph("Contrôle", styles["label"]), Paragraph("Résultat", styles["label"])],
        [
            Paragraph("Données stratégiques", styles["label"]),
            Paragraph(escape(result["strategic_status"]), styles["value"]),
        ],
        [
            Paragraph("Moyens du cabinet", styles["label"]),
            Paragraph(escape(result["feasibility_label"]), styles["value"]),
        ],
    ]
    story.append(_table(status_rows, [60 * mm, 90 * mm]))

    if result.get("selection_reasons"):
        story.append(Paragraph("Motifs de la recommandation", styles["heading"]))
        for reason in result["selection_reasons"]:
            story.append(Paragraph(f"• {escape(reason)}", styles["body"]))
            story.append(Spacer(1, 2))

    story.append(Paragraph("Contrôle de la faisabilité", styles["heading"]))
    feasibility_rows = [
        [
            Paragraph("État", styles["label"]),
            Paragraph("Élément", styles["label"]),
            Paragraph("Action", styles["label"]),
        ]
    ]
    labels = {"vert": "Vert", "orange": "Orange", "rouge": "Rouge"}
    for row in result.get("feasibility_rows", []):
        feasibility_rows.append(
            [
                Paragraph(labels[row["status"]], styles["value"]),
                Paragraph(escape(row["criterion"]), styles["value"]),
                Paragraph(escape(row["action"]), styles["value"]),
            ]
        )
    story.append(_table(feasibility_rows, [22 * mm, 38 * mm, 90 * mm]))

    actions = (
        result.get("decision_notes", [])
        if result["strategic_status"] == "Recommandation impossible"
        else result.get("launch_actions", [])
    )
    if actions:
        story.append(Paragraph("Actions à réaliser", styles["heading"]))
        for index, action in enumerate(actions, start=1):
            story.append(Paragraph(f"{index}. {escape(action)}", styles["body"]))
            story.append(Spacer(1, 3))

    story.extend(
        [
            Spacer(1, 14),
            Paragraph(
                "Cette synthèse constitue une aide à la décision. Les réponses "
                "restent limitées à la session d’utilisation.",
                styles["subtitle"],
            ),
        ]
    )
    document.build(story)
    return buffer.getvalue()

