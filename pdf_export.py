from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape, quoteattr

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
            fontSize=9.5, leading=13, alignment=TA_CENTER,
            textColor=colors.HexColor("#5F6368"), spaceAfter=14,
        ),
        "heading": ParagraphStyle(
            "CapHeading", parent=base["Heading2"], fontName=FONT_BOLD,
            fontSize=13, leading=16, spaceBefore=12, spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "CapBody", parent=base["BodyText"], fontName=FONT_REGULAR,
            fontSize=9.1, leading=13, textColor=colors.HexColor("#222222"),
        ),
        "small": ParagraphStyle(
            "CapSmall", parent=base["BodyText"], fontName=FONT_REGULAR,
            fontSize=7.8, leading=10.5, textColor=colors.HexColor("#444444"),
        ),
        "label": ParagraphStyle(
            "CapLabel", parent=base["BodyText"], fontName=FONT_BOLD,
            fontSize=8.2, leading=11,
        ),
        "value": ParagraphStyle(
            "CapValue", parent=base["BodyText"], fontName=FONT_REGULAR,
            fontSize=8.2, leading=11,
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
        "croisement cible–besoin–objectif": "Croisement de la cible, du besoin et de l’objectif",
        "moyens du cabinet": "Compatibilité avec les moyens du cabinet",
        "recherche externe": "Informations publiques actualisées",
        "données de cible": "Informations observées sur la cible",
        "règle stable de départage": "Règle stable de départage",
    }
    value = result.get("tie_break") or "Croisement des critères"
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

    return Table(
        data,
        colWidths=[18 * mm, 146 * mm],
        style=TableStyle(commands),
        cornerRadii=[8, 8, 8, 8],
        spaceBefore=6,
        spaceAfter=8,
    )


def _join(values) -> str:
    if not values:
        return "Sans objet"
    if isinstance(values, str):
        return values
    return ", ".join(str(item) for item in values)


def _responsibles(answers: dict) -> str:
    values = answers.get("q11", [])
    if isinstance(values, str):
        values = [values]
    result = []
    for value in values:
        if value == "Autre":
            result.append(answers.get("custom_pilot") or "Autre responsable")
        else:
            result.append(value)
    return _join(result)


def _competencies(answers: dict) -> str:
    return " · ".join(
        f"{skill} : {level}" for skill, level in answers.get("q9", {}).items()
    ) or "Sans objet"


def _support(answers: dict) -> str:
    support = answers.get("q12", [])
    confirmations = answers.get("q12_confirmed", {})
    return " · ".join(
        f"{item} : {'prévu' if confirmations.get(item) == 'Oui' else 'non confirmé'}"
        for item in support
    ) or "Sans objet"


def _source_paragraph(source: dict, styles: dict) -> Paragraph:
    title = escape(source.get("title", "Source publique"))
    url = source.get("url", "")
    domain = source.get("domain") or urlparse(url).netloc
    platform = source.get("platform", "")
    label = f"{platform} — {title}" if platform else title
    if url.startswith("http"):
        html = f'<link href={quoteattr(url)} color="#111111"><u>{label}</u></link> — {escape(domain)}'
    else:
        html = f"{label} — {escape(domain)}"
    return Paragraph(html, styles["small"])


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title="Synthèse CAP", author="CAP",
    )
    styles = _styles()

    winner = result.get("winner")
    complementary = result.get("complementary_platform")
    if result.get("strategic_status") != "Choix validé":
        result_title = "Projet à revoir"
        result_subtitle = "Aucune plateforme recommandée"
    else:
        result_title = winner or "Aucune recommandation"
        result_subtitle = "Plateforme prioritaire recommandée par CAP"

    persona = (answers.get("q2") or ["Non renseigné"])[0]
    if persona == "Autre":
        persona = answers.get("custom_profile") or persona
    objective = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6")
    objective_line = (
        f"{objective or ''} — {answers.get('indicator', '')} : "
        f"{answers.get('target', '')} à {answers.get('deadline', '')}"
    )
    observed = [item for item in answers.get("q4", []) if item in {"Facebook", "Instagram", "TikTok", "YouTube"}]
    budget = "Aucune dépense prévue" if answers.get("q13_has_cost") == "Non" else (
        "Budget validé" if answers.get("q13_budget_validated") == "Oui" else "Budget non validé"
    )

    story = [
        _cap_logo(),
        Spacer(1, 4),
        Paragraph("Synthèse du diagnostic", styles["subtitle"]),
        Paragraph(escape(result_title), styles["title"]),
        Paragraph(escape(result_subtitle), styles["subtitle"]),
    ]
    if complementary:
        story.append(Paragraph(
            f"Plateforme complémentaire éventuelle : {escape(complementary)}",
            styles["subtitle"],
        ))

    story.append(Paragraph("Données de décision", styles["heading"]))
    source_text = ", ".join(answers.get("q5", [])) or "Recherche CAP et référentiel interne"
    decision_rows = [
        [Paragraph("Élément", styles["label"]), Paragraph("Réponse", styles["label"])],
        [Paragraph("Persona analysé", styles["label"]), Paragraph(escape(persona), styles["value"])],
        [Paragraph("Besoin prioritaire", styles["label"]), Paragraph(escape(answers.get("priority_need", "")), styles["value"])],
        [Paragraph("Réseaux observés", styles["label"]), Paragraph(escape(_join(observed)), styles["value"])],
        [Paragraph("Réseau le plus souvent utilisé", styles["label"]), Paragraph(escape(answers.get("q4_priority") or "Non identifié"), styles["value"])],
        [Paragraph("Sources renseignées", styles["label"]), Paragraph(escape(source_text), styles["value"])],
        [Paragraph("Objectif SMART", styles["label"]), Paragraph(escape(objective_line), styles["value"])],
        [Paragraph("Temps disponible", styles["label"]), Paragraph(escape(answers.get("q8", "")), styles["value"])],
        [Paragraph("Formats retenus", styles["label"]), Paragraph(escape(_join(answers.get("q14", []))), styles["value"])],
        [Paragraph("Présence à l’écran", styles["label"]), Paragraph(escape(answers.get("q16", "Sans objet")), styles["value"])],
        [Paragraph("Compétences", styles["label"]), Paragraph(escape(_competencies(answers)), styles["value"])],
        [Paragraph("Matériel", styles["label"]), Paragraph(escape(_join(answers.get("q10", []))), styles["value"])],
        [Paragraph("Responsable(s)", styles["label"]), Paragraph(escape(_responsibles(answers)), styles["value"])],
        [Paragraph("Appui ou formation", styles["label"]), Paragraph(escape(_support(answers)), styles["value"])],
        [Paragraph("Budget", styles["label"]), Paragraph(escape(budget), styles["value"])],
    ]
    story.append(_table(decision_rows, [48 * mm, 112 * mm]))

    story.append(Paragraph("Résultat du diagnostic", styles["heading"]))
    status_rows = [[Paragraph("Élément", styles["label"]), Paragraph("Résultat", styles["label"])]]
    if result.get("strategic_status") == "Choix validé":
        status_rows.extend([
            [Paragraph("Plateforme prioritaire", styles["label"]), Paragraph(escape(winner or ""), styles["value"])],
            [Paragraph("Rôle principal", styles["label"]), Paragraph(escape(result.get("comparison", {}).get(winner, {}).get("role", "")), styles["value"])],
            [Paragraph("Plateforme complémentaire", styles["label"]), Paragraph(escape(complementary or "Aucune au lancement"), styles["value"])],
            [Paragraph("Élément déterminant", styles["label"]), Paragraph(escape(_decision_criterion(result)), styles["value"])],
            [Paragraph("Besoin interprété", styles["label"]), Paragraph(escape(result.get("need_analysis", {}).get("category", "")), styles["value"])],
            [Paragraph("Faisabilité", styles["label"]), Paragraph(escape(result.get("feasibility_label", "")), styles["value"])],
            [Paragraph("Acteurs mobilisés", styles["label"]), Paragraph(escape(_join(result.get("actors", []))), styles["value"])],
        ])
    else:
        status_rows.append([
            Paragraph("Résultat", styles["label"]),
            Paragraph("Aucune plateforme ne peut être recommandée à ce stade.", styles["value"]),
        ])
    story.append(_table(status_rows, [58 * mm, 102 * mm]))

    if result.get("selection_reasons"):
        story.append(Paragraph("Pourquoi cette recommandation ?", styles["heading"]))
        for reason in result["selection_reasons"]:
            story.append(Paragraph(f"• {escape(reason)}", styles["body"]))
            story.append(Spacer(1, 3))

    if complementary and result.get("complementary_reason"):
        story.append(Paragraph("Rôle de la plateforme complémentaire", styles["heading"]))
        story.append(Paragraph(escape(result["complementary_reason"]), styles["body"]))

    non_priority = result.get("non_priority_reasons", {})
    if non_priority:
        story.append(Paragraph("Pourquoi les autres plateformes ne sont-elles pas prioritaires ?", styles["heading"]))
        rows = [[Paragraph("Plateforme", styles["label"]), Paragraph("Motif", styles["label"])]]
        for platform, reason in non_priority.items():
            rows.append([
                Paragraph(escape(platform), styles["value"]),
                Paragraph(escape(reason), styles["value"]),
            ])
        story.append(_table(rows, [38 * mm, 122 * mm]))

    research = result.get("external_research", {})
    if research:
        story.append(Paragraph("Informations publiques mobilisées", styles["heading"]))
        status_text = (
            f"Recherche publique réalisée le {research.get('searched_at', '')}."
            if research.get("status") == "live"
            else "Recherche publique indisponible lors du diagnostic."
        )
        story.append(Paragraph(escape(status_text), styles["body"]))
        story.append(Paragraph(escape(research.get("note", "")), styles["small"]))
        sources = research.get("sources", [])
        if sources:
            story.append(Spacer(1, 5))
            for source in sources:
                story.append(_source_paragraph(source, styles))
                story.append(Spacer(1, 2))

    if result.get("strategic_status") == "Choix validé":
        story.append(PageBreak())
        story.append(Paragraph("Contrôle de la faisabilité", styles["heading"]))
        story.append(Paragraph(
            "La faisabilité ne remplace pas la recommandation stratégique. Elle indique si le cabinet peut commencer immédiatement ou doit préparer certains moyens.",
            styles["body"],
        ))
        story.append(Spacer(1, 5))
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
            "CAP constitue une aide à la décision. La communication du cabinet doit rester informative, exacte, mesurée et conforme aux règles déontologiques de la profession. Aucun démarchage individualisé ou insistant n’est proposé par l’outil.",
            styles["subtitle"],
        ),
    ])
    document.build(story)
    return buffer.getvalue()
