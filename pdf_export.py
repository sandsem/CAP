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
    PageBreak,
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


def _feasibility_table(rows: list[dict], styles: dict) -> Table:
    data = [
        [
            Paragraph("Élément", styles["label"]),
            Paragraph("Constat", styles["label"]),
            Paragraph("Action", styles["label"]),
        ]
    ]
    backgrounds = {
        "vert": colors.HexColor("#E8F5E9"),
        "orange": colors.HexColor("#FFF3E0"),
        "rouge": colors.HexColor("#FDECEC"),
    }
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F3F3")),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
        ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#D9DCDD")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9DCDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    status_order = {"vert": 0, "orange": 1, "rouge": 2}
    ordered_rows = sorted(
        rows,
        key=lambda row: status_order.get(row["status"], 3),
    )
    for index, row in enumerate(ordered_rows, start=1):
        data.append(
            [
                Paragraph(escape(row["criterion"]), styles["value"]),
                Paragraph(escape(row["observation"]), styles["value"]),
                Paragraph(escape(row["action"]), styles["value"]),
            ]
        )
        commands.append(
            ("BACKGROUND", (0, index), (-1, index), backgrounds[row["status"]])
        )

    table = Table(data, colWidths=[38 * mm, 63 * mm, 63 * mm], repeatRows=1)
    table.setStyle(TableStyle(commands))
    return table


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = _document(buffer, "Synthèse CAP")
    styles = _styles()

    winner = result.get("winner")
    observation = result.get("observation_platform")
    tied = result.get("tied_platforms", [])
    strategic_choice_is_valid = result["strategic_status"] == "Choix validé"
    selection_outcome = result.get("selection_outcome")
    selection_is_available = selection_outcome in {"recommended", "tie"}
    if strategic_choice_is_valid and winner:
        recommendation = winner
        recommendation_label = "Plateforme recommandée"
    elif strategic_choice_is_valid and tied:
        recommendation = "Plateformes équivalentes"
        recommendation_label = ", ".join(tied)
    elif strategic_choice_is_valid and selection_outcome == "no_compatible_platform":
        recommendation = "Aucune plateforme compatible"
        recommendation_label = (
            "Aucun réseau ne correspond à la fois à l’usage du persona "
            "et à l’objectif du cabinet"
        )
    else:
        recommendation = result["strategic_status"]
        recommendation_label = "Aucune plateforme recommandée"

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
            Paragraph("Persona analysé", styles["label"]),
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
            Paragraph("Usage par réseau", styles["label"]),
            Paragraph(
                escape(
                    " ; ".join(
                        f"{platform} : {mode}"
                        for platform, mode in answers.get(
                            "q4_modes_by_network", {}
                        ).items()
                    )
                    or "Non identifié"
                ),
                styles["value"],
            ),
        ],
        [
            Paragraph("Objectif", styles["label"]),
            Paragraph(escape(objective), styles["value"]),
        ],
    ]
    if selection_is_available:
        decision_rows.append(
            [
                Paragraph("Formats retenus", styles["label"]),
                Paragraph(
                    escape(", ".join(answers.get("q14", [])) or "Non définis"),
                    styles["value"],
                ),
            ]
        )
    story.append(_table(decision_rows, [46 * mm, 104 * mm]))

    story.append(Paragraph("Résultat du diagnostic", styles["heading"]))
    status_rows = [
        [Paragraph("Contrôle", styles["label"]), Paragraph("Résultat", styles["label"])],
        [
            Paragraph("Données stratégiques", styles["label"]),
            Paragraph(escape(result["strategic_status"]), styles["value"]),
        ],
    ]
    if strategic_choice_is_valid and selection_is_available:
        status_rows.append(
            [
                Paragraph("Moyens du cabinet", styles["label"]),
                Paragraph(escape(result["feasibility_label"]), styles["value"]),
            ]
        )
    elif strategic_choice_is_valid and selection_outcome == "no_compatible_platform":
        status_rows.append(
            [
                Paragraph("Comparaison des plateformes", styles["label"]),
                Paragraph("Aucune plateforme compatible", styles["value"]),
            ]
        )
    if strategic_choice_is_valid and winner and result.get("tie_break"):
        status_rows.append(
            [
                Paragraph("Critère de départage", styles["label"]),
                Paragraph(escape(result["tie_break"]), styles["value"]),
            ]
        )
    story.append(_table(status_rows, [60 * mm, 90 * mm]))

    if strategic_choice_is_valid and result.get("selection_reasons"):
        story.append(Paragraph("Motifs de la recommandation", styles["heading"]))
        for reason in result["selection_reasons"]:
            story.append(Paragraph(f"• {escape(reason)}", styles["body"]))
            story.append(Spacer(1, 2))

    if strategic_choice_is_valid and selection_is_available:
        story.append(PageBreak())
        story.append(Paragraph("Vérification de la faisabilité", styles["heading"]))
        story.append(
            _feasibility_table(result.get("feasibility_rows", []), styles)
        )
    else:
        actions = result.get("decision_notes", [])
        if actions:
            story.append(Paragraph("Actions nécessaires", styles["heading"]))
            story.append(
                Paragraph(
                    "Corrigez ces éléments avant de relancer le diagnostic.",
                    styles["body"],
                )
            )
            story.append(Spacer(1, 5))
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
