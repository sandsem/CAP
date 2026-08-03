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
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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


def _safe_text(value, limit: int = 1200) -> str:
    text = str(value or "").replace("\x00", " ").replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    words = []
    for word in text.split(" "):
        if len(word) > 45:
            words.extend(word[index:index + 45] for index in range(0, len(word), 45))
        else:
            words.append(word)
    return " ".join(words)


def _escaped(value, limit: int = 1200) -> str:
    return escape(_safe_text(value, limit))


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
    status_labels = {"vert": "Prêt", "orange": "À préparer", "rouge": "À reporter"}
    data = [[
        Paragraph("Élément", styles["label"]),
        Paragraph("Statut", styles["label"]),
        Paragraph("Constat", styles["label"]),
        Paragraph("Action", styles["label"]),
    ]]
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F3F3")),
        ("BOX", (0, 0), (-1, -1), .3, colors.HexColor("#D9DCDD")),
        ("INNERGRID", (0, 0), (-1, -1), .25, colors.HexColor("#D9DCDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    backgrounds = {
        "vert": colors.HexColor("#E8F5E9"),
        "orange": colors.HexColor("#FFF3E0"),
        "rouge": colors.HexColor("#FDECEC"),
    }
    for index, row in enumerate(ordered, start=1):
        data.append([
            Paragraph(_escaped(row["criterion"], 100), styles["value"]),
            Paragraph(_escaped(status_labels.get(row["status"], row["status"]), 60), styles["value"]),
            Paragraph(_escaped(row["observation"], 900), styles["value"]),
            Paragraph(_escaped(row["action"], 900), styles["value"]),
        ])
        commands.append(("BACKGROUND", (0, index), (-1, index), backgrounds[row["status"]]))
    table = Table(data, colWidths=[30 * mm, 24 * mm, 53 * mm, 57 * mm], repeatRows=1)
    table.setStyle(TableStyle(commands))
    return table


def _actions_box(actions: list[str], styles: dict, title: str, introduction: str) -> Table:
    data = [
        [Paragraph(_escaped(title.upper(), 120), styles["action_eyebrow"]), ""],
        [Paragraph(_escaped(introduction, 500), styles["body"]), ""],
    ]
    for index, action in enumerate(actions, start=1):
        data.append([
            Paragraph(f"{index:02d}", styles["action_number"]),
            Paragraph(_escaped(action, 900), styles["body"]),
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
        return _safe_text(values, 800)
    return _safe_text(", ".join(str(item) for item in values), 800)


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
    by_skill = answers.get("q12_by_skill", {})
    if by_skill:
        return " · ".join(
            f"{skill} : {item.get('solution', 'Aucun appui prévu')} "
            f"({'prévu' if item.get('confirmed') == 'Oui' else 'non confirmé'})"
            for skill, item in by_skill.items()
        )
    support = answers.get("q12", [])
    confirmations = answers.get("q12_confirmed", {})
    return " · ".join(
        f"{item} : {'prévu' if confirmations.get(item) == 'Oui' else 'non confirmé'}"
        for item in support
    ) or "Sans objet"


def _source_paragraph(source: dict, styles: dict) -> Paragraph:
    title = _escaped(source.get("title", "Source publique"), 220)
    url = str(source.get("url", ""))
    domain = _safe_text(source.get("domain") or urlparse(url).netloc, 120)
    platform = _safe_text(source.get("platform", ""), 40)
    source_type = _safe_text(source.get("source_type", "source publique"), 80)
    authority = _safe_text(source.get("authority", "non précisée"), 60)
    published = _safe_text(source.get("published_date", "date non disponible"), 40) or "date non disponible"
    label = f"{platform} — {title}" if platform else title
    metadata = _escaped(f"{domain} · {source_type} · autorité {authority} · {published}", 260)
    if url.startswith("http"):
        html = f'<link href={quoteattr(url)} color="#111111"><u>{label}</u></link><br/>{metadata}'
    else:
        html = f"{label}<br/>{metadata}"
    return Paragraph(html, styles["small"])


def build_summary_pdf(answers: dict, result: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title=f"Synthèse CAP - {answers.get('cabinet_name', 'Cabinet')}", author="CAP",
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
        Paragraph(_escaped(result_title, 120), styles["title"]),
        Paragraph(escape(result_subtitle), styles["subtitle"]),
        Paragraph(f"Cabinet : {_escaped(answers.get('cabinet_name', 'Non renseigné'), 100)}", styles["subtitle"]),
    ]
    if complementary:
        story.append(Paragraph(
            f"Plateforme complémentaire éventuelle : {_escaped(complementary, 60)}",
            styles["subtitle"],
        ))

    story.append(Paragraph("Données de décision", styles["heading"]))
    source_text = ", ".join(answers.get("q5", [])) or "Référentiel CAP"
    if answers.get("custom_source_details"):
        source_text += f" — {answers.get('custom_source_details')}"
    decision_rows = [
        [Paragraph("Élément", styles["label"]), Paragraph("Réponse", styles["label"])],
        [Paragraph("Persona analysé", styles["label"]), Paragraph(_escaped(persona, 180), styles["value"])],
        [Paragraph("Besoin prioritaire", styles["label"]), Paragraph(_escaped(answers.get("priority_need", ""), 500), styles["value"])],
        [Paragraph("Tranche d’âge dominante", styles["label"]), Paragraph(_escaped(answers.get("target_age_range") or "Je ne sais pas", 80), styles["value"])],
        [Paragraph("Réseaux observés", styles["label"]), Paragraph(_escaped(_join(observed), 200), styles["value"])],
        [Paragraph("Réseau le plus souvent utilisé", styles["label"]), Paragraph(_escaped(answers.get("q4_priority") or "Non identifié", 100), styles["value"])],
        [Paragraph("Sources renseignées", styles["label"]), Paragraph(_escaped(source_text, 350), styles["value"])],
        [Paragraph("Objectif SMART", styles["label"]), Paragraph(_escaped(objective_line, 500), styles["value"])],
        [Paragraph("Temps disponible", styles["label"]), Paragraph(_escaped(answers.get("q8", ""), 80), styles["value"])],
        [Paragraph("Formats retenus", styles["label"]), Paragraph(_escaped(_join(answers.get("q14", [])), 300), styles["value"])],
        [Paragraph("Présence à l’écran", styles["label"]), Paragraph(_escaped(answers.get("q16", "Sans objet"), 80), styles["value"])],
        [Paragraph("Compétences", styles["label"]), Paragraph(_escaped(_competencies(answers), 700), styles["value"])],
        [Paragraph("Matériel", styles["label"]), Paragraph(_escaped(_join(answers.get("q10", [])), 400), styles["value"])],
        [Paragraph("Responsable(s)", styles["label"]), Paragraph(_escaped(_responsibles(answers), 300), styles["value"])],
        [Paragraph("Appui ou formation", styles["label"]), Paragraph(_escaped(_support(answers), 700), styles["value"])],
        [Paragraph("Budget", styles["label"]), Paragraph(_escaped(budget, 120), styles["value"])],
    ]
    story.append(_table(decision_rows, [48 * mm, 112 * mm]))

    story.append(Paragraph("Résultat du diagnostic", styles["heading"]))
    status_rows = [[Paragraph("Élément", styles["label"]), Paragraph("Résultat", styles["label"])]]
    if result.get("strategic_status") == "Choix validé":
        status_rows.extend([
            [Paragraph("Plateforme prioritaire", styles["label"]), Paragraph(_escaped(winner or "", 60), styles["value"])],
            [Paragraph("Rôle principal", styles["label"]), Paragraph(_escaped(result.get("comparison", {}).get(winner, {}).get("role", ""), 300), styles["value"])],
            [Paragraph("Plateforme complémentaire", styles["label"]), Paragraph(_escaped(complementary or "Aucune au lancement", 100), styles["value"])],
            [Paragraph("Faisabilité", styles["label"]), Paragraph(_escaped(result.get("feasibility_label", ""), 100), styles["value"])],
            [Paragraph("Acteurs mobilisés", styles["label"]), Paragraph(_escaped(_join(result.get("actors", [])), 300), styles["value"])],
        ])
    else:
        status_rows.append([
            Paragraph("Résultat", styles["label"]),
            Paragraph("Aucune plateforme ne peut être recommandée à ce stade.", styles["value"]),
        ])
    story.append(_table(status_rows, [58 * mm, 102 * mm]))

    if result.get("selection_reasons"):
        story.append(Paragraph(f"Pourquoi CAP recommande {_escaped(winner or 'cette plateforme', 60)} ?", styles["heading"]))
        for reason in result["selection_reasons"]:
            story.append(Paragraph(f"• {_escaped(reason, 900)}", styles["body"]))
            story.append(Spacer(1, 3))

    if complementary and result.get("complementary_reason"):
        story.append(Paragraph("Rôle de la plateforme complémentaire", styles["heading"]))
        story.append(Paragraph(_escaped(result["complementary_reason"], 800), styles["body"]))

    non_priority = result.get("non_priority_reasons", {})
    if non_priority:
        story.append(Paragraph("Pourquoi les autres plateformes ne sont-elles pas prioritaires ?", styles["heading"]))
        rows = [[Paragraph("Plateforme", styles["label"]), Paragraph("Motif", styles["label"])]]
        for platform, reason in non_priority.items():
            rows.append([
                Paragraph(_escaped(platform, 60), styles["value"]),
                Paragraph(_escaped(reason, 600), styles["value"]),
            ])
        story.append(_table(rows, [38 * mm, 122 * mm]))

    research = result.get("external_research", {})
    if research:
        story.append(Paragraph("Vérification externe", styles["heading"]))
        status = research.get("status", "indisponible")
        searched_at = research.get("searched_at", "date non disponible")
        if status == "complet":
            winner_signal = research.get("platforms", {}).get(winner, {}).get("signal", "faible")
            if winner_signal in {"fort", "modéré"}:
                message = (
                    f"Une vérification de sources publiques a été réalisée le {searched_at}. "
                    "Elle est cohérente avec la recommandation, sans remplacer les informations fournies par le cabinet."
                )
            else:
                message = (
                    f"Une vérification de sources publiques a été réalisée le {searched_at}. "
                    "Les résultats étaient trop généraux pour modifier la recommandation."
                )
        elif status in {"partiel", "insuffisant"}:
            message = (
                f"La vérification externe du {searched_at} était incomplète ou insuffisante. "
                "Elle n’a pas influencé la recommandation."
            )
        else:
            message = (
                "Aucune vérification externe exploitable n’a été utilisée. "
                "La recommandation repose sur les réponses du cabinet et les repères intégrés à CAP."
            )
        story.append(Paragraph(_escaped(message, 650), styles["small"]))

    if result.get("strategic_status") == "Choix validé":
        story.append(Paragraph("Contrôle de la faisabilité", styles["heading"]))
        story.append(Paragraph(
            "La faisabilité ne remplace pas la recommandation stratégique. Elle indique si le cabinet peut commencer immédiatement ou doit préparer certains moyens.",
            styles["body"],
        ))
        story.append(Spacer(1, 5))
        story.append(_feasibility_table(result.get("feasibility_rows", []), styles))
        actions = result.get("launch_actions", [])
        if actions:
            story.append(KeepTogether([
                Paragraph("Actions à réaliser", styles["heading"]),
                _actions_box(
                    actions,
                    styles,
                    "Préparation opérationnelle",
                    "Réalisez ces actions avant de commencer.",
                ),
            ]))
    else:
        actions = result.get("decision_notes", [])
        if actions:
            story.append(KeepTogether([
                Paragraph("Actions nécessaires", styles["heading"]),
                _actions_box(
                    actions,
                    styles,
                    "À corriger",
                    "Corrigez ces éléments avant de relancer le diagnostic.",
                ),
            ]))

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "CAP constitue une aide à la décision. La communication du cabinet doit rester informative, exacte, mesurée et conforme aux règles déontologiques de la profession. Aucun démarchage individualisé ou insistant n’est proposé par l’outil.",
            styles["subtitle"],
        ),
    ])
    document.build(story)
    return buffer.getvalue()
