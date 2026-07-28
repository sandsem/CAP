from io import BytesIO
from pathlib import Path

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


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="Synthèse CAP",
        author="CAP",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "CapTitle",
        parent=styles["Title"],
        fontName=FONT_BOLD,
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111111"),
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "CapSubtitle",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5F6368"),
        spaceAfter=20,
    )
    heading = ParagraphStyle(
        "CapHeading",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111111"),
        spaceBefore=12,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "CapBody",
        parent=styles["BodyText"],
        fontName=FONT_REGULAR,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#222222"),
    )
    table_label = ParagraphStyle(
        "CapTableLabel",
        parent=body,
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
    )
    table_value = ParagraphStyle(
        "CapTableValue",
        parent=body,
        fontSize=8.5,
        leading=11,
    )

    winner = result.get("winner")
    recommendation = winner or "Résultat à consolider"
    score = result["scores"].get(winner, 0) if winner else 0

    story = [
        Paragraph("CAP", title),
        Paragraph("Synthèse du diagnostic", subtitle),
        Paragraph(recommendation, title),
    ]
    if winner:
        story.append(Paragraph(f"Indice de pertinence : {score:.0f} %", subtitle))

    story.extend(
        [
            Spacer(1, 8),
            Paragraph("Données de décision", heading),
        ]
    )

    objective = (
        f"{answers.get('q6', '')} - {answers.get('indicator', '')} : "
        f"{answers.get('target', '')} à {answers.get('deadline', '')}"
    )
    decision_rows = [
        [
            Paragraph("Profils ciblés", table_label),
            Paragraph(", ".join(answers.get("q2", [])), table_value),
        ],
        [
            Paragraph("Canaux d’information de la cible", table_label),
            Paragraph(
                ", ".join(answers.get("q4", [])) or "Non identifiés",
                table_value,
            ),
        ],
        [
            Paragraph("Objectif", table_label),
            Paragraph(objective, table_value),
        ],
        [
            Paragraph("Temps disponible", table_label),
            Paragraph(answers.get("q8", ""), table_value),
        ],
    ]
    decision_table = Table(decision_rows, colWidths=[42 * mm, 108 * mm])
    decision_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
                ("FONTNAME", (1, 0), (1, -1), FONT_REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9DCDD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(decision_table)

    story.append(Paragraph("Qualité du diagnostic", heading))
    quality_rows = [
        [
            Paragraph("Fiabilité des données sur la cible", table_label),
            Paragraph(
                f"{result['reliability_label']} - {result['reliability']:.0f} %",
                table_value,
            ),
        ],
        [
            Paragraph("Niveau de préparation", table_label),
            Paragraph(
                f"{result['readiness_label']} - {result['readiness']:.0f} %",
                table_value,
            ),
        ],
    ]
    quality_table = Table(quality_rows, colWidths=[60 * mm, 90 * mm])
    quality_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6F6")),
                ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
                ("FONTNAME", (1, 0), (1, -1), FONT_REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9DCDD")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9DCDD")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(quality_table)

    story.append(Paragraph("Avant de commencer", heading))
    story.append(
        Paragraph(
            "Ces actions préparent les conditions nécessaires au lancement sur "
            "la plateforme recommandée.",
            body,
        )
    )
    story.append(Spacer(1, 5))
    for index, action in enumerate(result.get("launch_actions", [])[:4], start=1):
        story.append(Paragraph(f"{index}. {action}", body))
        story.append(Spacer(1, 3))

    story.extend(
        [
            Spacer(1, 18),
            Paragraph(
                "Cette synthèse constitue une aide à la décision. Elle doit être relue à la lumière "
                "de la stratégie, du plan de charge et des règles professionnelles applicables au cabinet.",
                subtitle,
            ),
        ]
    )

    document.build(story)
    return buffer.getvalue()
