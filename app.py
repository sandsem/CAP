from pathlib import Path
from html import escape

import streamlit as st

from config import (
    APP_SUPPORT_OPTIONS,
    BUDGET_OPTIONS,
    COMPETENCY_LEVELS,
    EQUIPMENT_OPTIONS,
    INDICATOR_OPTIONS,
    OBJECTIVE_OPTIONS,
    PILOT_OPTIONS,
    PLATFORM_NAMES,
    PLATFORM_STATUS_OPTIONS,
    PROFILE_OPTIONS,
    SOURCE_OPTIONS,
    TARGET_NETWORK_OPTIONS,
    TIME_OPTIONS,
)
from pdf_export import build_summary_pdf
from scoring import evaluate


BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo_cap.svg"
GUIDES_DIR = BASE_DIR / "guides"

st.set_page_config(
    page_title="CAP — Choix de plateforme",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cap-black: #111111;
            --cap-charcoal: #1B1B1B;
            --cap-muted: #6B7280;
            --cap-line: #E6E7E9;
            --cap-soft: #F7F8F8;
            --cap-green: #111111;
            --primary-color: #111111;
        }

        header[data-testid="stHeader"],
        [data-testid="collapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stAppDeployButton"],
        .stDeployButton,
        footer {
            display: none;
        }

        .stApp {
            background: #FFFFFF;
            color: var(--cap-black);
        }

        .block-container {
            max-width: 860px;
            padding-top: 2.2rem;
            padding-bottom: 3.5rem;
        }

        h1, h2, h3, p, label, div {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", sans-serif;
        }

        h1 {
            letter-spacing: -0.045em;
            font-size: clamp(2.25rem, 6vw, 4.2rem) !important;
            line-height: 1.02 !important;
            font-weight: 720 !important;
        }

        h2 {
            letter-spacing: -0.035em;
            font-size: clamp(1.65rem, 4vw, 2.55rem) !important;
            line-height: 1.12 !important;
        }

        h3 {
            letter-spacing: -0.02em;
        }

        .cap-logo {
            width: 76px;
            margin: 0 auto 1.35rem auto;
        }

        .cap-center {
            text-align: center;
        }

        .cap-lead {
            color: #36393D;
            font-size: 1.12rem;
            line-height: 1.55;
            margin: 0.8rem auto 1.8rem auto;
            max-width: 570px;
        }

        .cap-eyebrow {
            color: var(--cap-muted);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }

        .cap-stepbar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin: 1.2rem 0 2.2rem 0;
        }

        .cap-step {
            height: 4px;
            border-radius: 100px;
            background: #E5E7EB;
        }

        .cap-step.active {
            background: var(--cap-black);
        }

        .cap-question {
            color: var(--cap-muted);
            font-size: 0.93rem;
            margin-top: -0.35rem;
            margin-bottom: 1.1rem;
        }

        .cap-card {
            border: 1px solid var(--cap-line);
            border-radius: 18px;
            padding: 1.15rem 1.25rem;
            background: #FFFFFF;
            height: 100%;
        }

        .cap-card-label {
            color: var(--cap-muted);
            font-size: 0.82rem;
            margin-bottom: 0.35rem;
        }

        .cap-card-value {
            font-size: 1.08rem;
            font-weight: 680;
        }

        .cap-card-purpose {
            color: var(--cap-muted);
            font-size: 0.82rem;
            line-height: 1.5;
            margin-top: 0.55rem;
        }

        .cap-recommendation {
            border-top: 1px solid var(--cap-line);
            border-bottom: 1px solid var(--cap-line);
            padding: 1.35rem 0;
            margin: 1.25rem 0 1.3rem 0;
        }

        .cap-platform {
            font-size: clamp(2.15rem, 7vw, 4rem);
            font-weight: 760;
            letter-spacing: -0.055em;
            line-height: 1;
        }

        .cap-score {
            color: var(--cap-green);
            font-size: 1.05rem;
            font-weight: 680;
            margin-top: 0.55rem;
        }

        .cap-note {
            color: var(--cap-muted);
            font-size: 0.84rem;
            line-height: 1.5;
        }

        .cap-launch-box {
            border: 1px solid var(--cap-black);
            border-radius: 20px;
            background: var(--cap-soft);
            margin: 1.65rem 0 0.7rem 0;
            padding: 1.35rem 1.45rem 0.45rem 1.45rem;
        }

        .cap-launch-kicker {
            color: var(--cap-muted);
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .cap-launch-title {
            color: var(--cap-black);
            font-size: 1.35rem;
            font-weight: 740;
            letter-spacing: -0.025em;
            margin-bottom: 0.35rem;
        }

        .cap-launch-intro {
            color: #45484C;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }

        .cap-action {
            display: grid;
            grid-template-columns: 2rem 1fr;
            gap: 0.65rem;
            align-items: start;
            border-top: 1px solid #D9DCDD;
            padding: 0.85rem 0;
        }

        .cap-action-number {
            color: var(--cap-muted);
            font-size: 0.74rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            padding-top: 0.12rem;
        }

        .cap-action-text {
            color: var(--cap-black);
            font-size: 0.9rem;
            line-height: 1.48;
        }

        .cap-nav-spacer {
            height: clamp(3rem, 8vh, 6rem);
        }

        .cap-review-card {
            border: 1px solid var(--cap-line);
            border-radius: 16px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.75rem;
            background: #FFFFFF;
        }

        .cap-review-title {
            font-size: 1.05rem;
            font-weight: 720;
            margin-bottom: 0.55rem;
        }

        .cap-review-line {
            color: #36393D;
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .cap-review-line strong {
            color: var(--cap-black);
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-secondary"] {
            min-height: 46px;
            border-radius: 10px;
            font-weight: 650;
            transition: none;
        }

        button[kind="primary"],
        .stDownloadButton > button,
        [data-testid="stBaseButton-primary"] {
            background: var(--cap-black) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--cap-black) !important;
        }

        button[kind="secondary"],
        [data-testid="stBaseButton-secondary"] {
            background: #FFFFFF !important;
            color: var(--cap-black) !important;
            border: 1px solid #D8DADD !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: var(--cap-black) !important;
        }

        div[data-baseweb="select"] > div {
            background: var(--cap-charcoal) !important;
            border-color: var(--cap-charcoal) !important;
            color: #FFFFFF !important;
            border-radius: 10px;
        }

        div[data-baseweb="select"] *,
        div[data-baseweb="input"] input {
            color: #FFFFFF !important;
        }

        div[data-baseweb="input"] {
            background: var(--cap-charcoal) !important;
            border-color: var(--cap-charcoal) !important;
        }

        div[data-baseweb="input"] input::placeholder {
            color: #C9CDD2 !important;
            opacity: 1;
        }

        div[role="listbox"],
        ul[role="listbox"],
        div[role="option"],
        li[role="option"] {
            background: var(--cap-charcoal) !important;
            color: #FFFFFF !important;
        }

        div[role="option"]:hover,
        li[role="option"]:hover,
        div[aria-selected="true"] {
            background: #303030 !important;
            color: #FFFFFF !important;
        }

        [data-testid="stPills"] button {
            background: #FFFFFF !important;
            color: var(--cap-black) !important;
            border: 1px solid #C9CDD2 !important;
        }

        [data-testid="stPills"] button[aria-pressed="true"] {
            background: var(--cap-black) !important;
            color: #FFFFFF !important;
            border-color: var(--cap-black) !important;
        }

        [data-testid="stRadio"] [aria-checked="true"] > div:first-child {
            background: var(--cap-black) !important;
            border-color: var(--cap-black) !important;
        }

        div[role="radiogroup"] {
            border-radius: 10px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        [data-testid="InputInstructions"],
        [data-testid="stTextInput"] > span:last-child {
            display: none !important;
        }

        [data-testid="stForm"] {
            border: 0;
            padding: 0;
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 1.3rem 1rem 2.5rem 1rem;
            }

            .cap-logo {
                width: 64px;
            }

            .cap-card {
                margin-bottom: 0.65rem;
            }

            .cap-nav-spacer {
                height: 2.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "screen": "home",
        "answers": {},
        "result": None,
        "return_to_review": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logo(center: bool = False) -> None:
    if not LOGO_PATH.exists():
        return
    if center:
        left, middle, right = st.columns([1, 0.28, 1])
        with middle:
            st.image(str(LOGO_PATH), width="stretch")
    else:
        st.image(str(LOGO_PATH), width=62)


def step_header(step: int, title: str, subtitle: str = "") -> None:
    logo()
    st.markdown(f'<div class="cap-eyebrow">Étape {step} sur 4</div>', unsafe_allow_html=True)
    bars = "".join(
        f'<div class="cap-step{" active" if index <= step else ""}"></div>'
        for index in range(1, 5)
    )
    st.markdown(f'<div class="cap-stepbar">{bars}</div>', unsafe_allow_html=True)
    st.header(title)
    if subtitle:
        st.markdown(f'<div class="cap-question">{subtitle}</div>', unsafe_allow_html=True)


def navigate(screen: str) -> None:
    st.session_state.screen = screen
    st.rerun()


def reset_diagnostic() -> None:
    widget_prefixes = (
        "target_",
        "objective_",
        "indicator_choice_",
        "status_",
        "resources_",
        "skill_",
    )
    for key in list(st.session_state):
        if key.startswith(widget_prefixes):
            del st.session_state[key]
    st.session_state.answers = {}
    st.session_state.result = None
    st.session_state.return_to_review = False
    navigate("home")


def render_nav(previous: str, continue_label: str = "Continuer") -> tuple[bool, bool]:
    st.markdown('<div class="cap-nav-spacer"></div>', unsafe_allow_html=True)
    left, spacer, right = st.columns([1.2, 2.2, 1.4])
    with left:
        back = st.button(
            "Précédent",
            type="secondary",
            width="stretch",
            key=f"back_to_{previous}_{st.session_state.screen}",
        )
    with right:
        forward = st.button(
            continue_label,
            type="primary",
            width="stretch",
            key=f"forward_from_{st.session_state.screen}",
        )
    return back, forward


def next_screen(default: str) -> None:
    if st.session_state.return_to_review:
        st.session_state.return_to_review = False
        navigate("review")
        return
    navigate(default)


def select_many(
    label: str,
    options: list[str],
    default: list[str],
    key: str,
    help_text: str | None = None,
) -> list[str]:
    selected = st.pills(
        label,
        options,
        selection_mode="multi",
        default=default,
        key=key,
        help=help_text,
    )
    return list(selected or [])


def join_values(values: list[str]) -> str:
    return ", ".join(values) if values else "Non renseigné"


def review_card(title: str, rows: list[tuple[str, str]]) -> None:
    content = "".join(
        f'<div class="cap-review-line"><strong>{escape(label)}</strong> {escape(value)}</div>'
        for label, value in rows
    )
    st.markdown(
        f"""
        <div class="cap-review-card">
            <div class="cap-review-title">{escape(title)}</div>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def home_page() -> None:
    st.write("")
    logo(center=True)
    st.markdown(
        """
        <div class="cap-center">
            <h1>Bienvenue</h1>
            <div class="cap-lead">Identifiez la plateforme la plus adaptée à votre cabinet.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, middle, right = st.columns([1, 1.1, 1])
    with middle:
        if st.button("Commencer", type="primary", width="stretch", key="start"):
            navigate("prepare")
    st.markdown(
        '<p class="cap-center cap-note">Ce diagnostic ne vous prendra que quelques minutes.</p>',
        unsafe_allow_html=True,
    )


def prepare_page() -> None:
    st.write("")
    logo(center=True)
    st.markdown(
        """
        <div class="cap-center">
            <h2>Avant de commencer</h2>
            <div class="cap-lead">Munissez-vous de votre persona, de votre objectif et de votre plan de charge.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="cap-nav-spacer"></div>', unsafe_allow_html=True)
    left, spacer, right = st.columns([1.2, 2.2, 1.4])
    with left:
        if st.button(
            "Précédent",
            type="secondary",
            width="stretch",
            key="prepare_back",
        ):
            navigate("home")
    with right:
        if st.button(
            "Continuer",
            type="primary",
            width="stretch",
            key="prepare_continue",
        ):
            navigate("target")


def target_page() -> None:
    answers = st.session_state.answers
    step_header(1, "Votre cible", "Les informations connues sur votre clientèle recherchée.")

    q1 = st.radio(
        "Persona finalisé ?",
        ["Oui", "Partiellement", "Non"],
        index=["Oui", "Partiellement", "Non"].index(answers.get("q1", "Oui")),
        horizontal=True,
        key="target_persona",
    )
    q2 = select_many(
        "Qui souhaitez-vous atteindre ?",
        PROFILE_OPTIONS,
        answers.get("q2", []),
        "target_profiles",
        "Sélectionnez trois profils au maximum.",
    )
    if len(q2) > 3:
        st.warning("Trois profils maximum. Désélectionnez un profil pour poursuivre.")

    q3 = st.radio(
        "Besoins recensés ?",
        ["Oui", "Partiellement", "Non"],
        index=["Oui", "Partiellement", "Non"].index(answers.get("q3", "Oui")),
        horizontal=True,
        key="target_needs",
    )
    q4 = select_many(
        "Sur quels réseaux votre cible recherche-t-elle des informations liées au besoin auquel votre cabinet souhaite répondre ?",
        TARGET_NETWORK_OPTIONS,
        answers.get("q4", []),
        "target_networks",
        "Ne retenez pas ses réseaux de divertissement s’ils ne sont pas utilisés pour rechercher cette information.",
    )
    q5 = select_many(
        "D’où viennent vos informations ?",
        SOURCE_OPTIONS,
        answers.get("q5", []),
        "target_sources",
    )

    back, forward = render_nav("prepare")
    if back:
        navigate("prepare")
    if forward:
        errors = []
        if q1 == "Non":
            errors.append("Persona non défini — complétez votre persona avant de poursuivre.")
        if not q2 or "Non identifié" in q2:
            errors.append("Identifiez au moins un profil cible.")
        if len(q2) > 3:
            errors.append("Sélectionnez trois profils au maximum.")
        if "Non identifié" in q4 and len(q4) > 1:
            errors.append("« Non identifié » ne peut pas être associé à un réseau.")
        if "Aucune source" in q5 and len(q5) > 1:
            errors.append("« Aucune source » ne peut pas être associée à une autre source.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update({"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5})
            next_screen("objective")


def objective_page() -> None:
    answers = st.session_state.answers
    step_header(2, "Votre objectif", "Le résultat que la communication doit produire.")

    q6 = st.selectbox(
        "Quel est votre objectif ?",
        OBJECTIVE_OPTIONS,
        index=OBJECTIVE_OPTIONS.index(answers.get("q6", OBJECTIVE_OPTIONS[0])),
        key="objective_choice",
    )

    indicator_options = INDICATOR_OPTIONS.get(q6, ["Autre indicateur"])
    saved_indicator = answers.get("indicator", indicator_options[0])
    indicator_index = (
        indicator_options.index(saved_indicator)
        if saved_indicator in indicator_options
        else 0
    )

    st.caption("Précisez la mesure suivie, le résultat recherché et le délai.")
    c1, c2, c3 = st.columns(3)
    with c1:
        indicator_choice = st.selectbox(
            "Indicateur suivi",
            indicator_options,
            index=indicator_index,
            key=f"indicator_choice_{q6}",
        )
    with c2:
        target = st.text_input(
            "Résultat attendu",
            value=answers.get("target", ""),
            placeholder="Ex. : 2",
            help="Indiquez la valeur chiffrée que vous souhaitez atteindre.",
            key="objective_target",
        )
    with c3:
        deadline = st.text_input(
            "Échéance",
            value=answers.get("deadline", ""),
            placeholder="Ex. : 3 mois",
            help="Indiquez le délai fixé pour atteindre le résultat.",
            key="objective_deadline",
        )

    if indicator_choice == "Autre indicateur":
        indicator = st.text_input(
            "Précisez l’indicateur",
            value=(
                answers.get("indicator", "")
                if answers.get("indicator") not in indicator_options
                else ""
            ),
            placeholder="Ex. : demandes de devis",
            key="objective_custom_indicator",
        )
    else:
        indicator = indicator_choice

    back, forward = render_nav("target")
    if back:
        navigate("target")
    if forward:
        if q6 == "Non défini":
            st.error("Objectif non défini — formalisez votre objectif avant de poursuivre.")
        elif not indicator.strip() or not target.strip() or not deadline.strip():
            st.error("Renseignez l’indicateur, le résultat attendu et l’échéance.")
        else:
            answers.update(
                {
                    "q6": q6,
                    "indicator": indicator.strip(),
                    "target": target.strip(),
                    "deadline": deadline.strip(),
                }
            )
            next_screen("presence")


def presence_page() -> None:
    answers = st.session_state.answers
    step_header(
        3,
        "Votre présence actuelle",
        "Retenez, pour chaque plateforme, le niveau le plus avancé déjà atteint.",
    )

    with st.expander("Comprendre les niveaux"):
        st.markdown(
            """
            - **Aucun compte** : aucun compte professionnel n’est ouvert.
            - **Compte inactif** : le compte existe, mais n’est plus alimenté.
            - **Compte actif** : des contenus sont publiés, sans résultat qualifié identifié.
            - **Audience cible engagée** : la clientèle recherchée suit ou sollicite le compte.
            - **Contacts obtenus** : le compte a déjà généré des demandes ou des rendez-vous.
            """
        )

    legacy_status = {
        "Aucun": "Aucun compte",
        "Inactif": "Compte inactif",
        "Actif": "Compte actif",
        "Audience qualifiée": "Audience cible engagée",
        "Contacts générés": "Contacts obtenus",
    }
    statuses = {}
    columns = st.columns(2)
    for index, platform in enumerate(PLATFORM_NAMES):
        with columns[index % 2]:
            previous = answers.get("q7", {}).get(platform, "Aucun compte")
            previous = legacy_status.get(previous, previous)
            statuses[platform] = st.selectbox(
                platform,
                PLATFORM_STATUS_OPTIONS,
                index=PLATFORM_STATUS_OPTIONS.index(previous),
                key=f"status_{platform}",
            )

    back, forward = render_nav("objective")
    if back:
        navigate("objective")
    if forward:
        answers["q7"] = statuses
        next_screen("resources")


def resources_page() -> None:
    answers = st.session_state.answers
    step_header(4, "Vos moyens", "Le temps et les ressources réellement mobilisables.")

    q8 = st.selectbox(
        "Quel temps mensuel pouvez-vous consacrer ?",
        TIME_OPTIONS,
        index=TIME_OPTIONS.index(answers.get("q8", TIME_OPTIONS[0])),
        key="resources_time",
    )

    st.markdown("**Quel est votre niveau ?**")
    competencies = {}
    for skill in ["Rédaction / script", "Création", "Montage", "Aisance face caméra"]:
        previous = answers.get("q9", {}).get(skill, "Notions")
        competencies[skill] = st.radio(
            skill,
            COMPETENCY_LEVELS,
            index=COMPETENCY_LEVELS.index(previous),
            horizontal=True,
            key=f"skill_{skill}",
        )

    q10 = select_many(
        "Quel matériel possédez-vous ?",
        EQUIPMENT_OPTIONS,
        answers.get("q10", []),
        "resources_equipment",
    )
    q11 = st.selectbox(
        "Qui pilotera la communication ?",
        PILOT_OPTIONS,
        index=PILOT_OPTIONS.index(answers.get("q11", PILOT_OPTIONS[0])),
        key="resources_pilot",
    )
    q12 = select_many(
        "Comment compléter vos compétences ?",
        APP_SUPPORT_OPTIONS,
        answers.get("q12", []),
        "resources_support",
    )
    q13 = st.selectbox(
        "Quel budget pouvez-vous mobiliser ?",
        BUDGET_OPTIONS,
        index=BUDGET_OPTIONS.index(answers.get("q13", BUDGET_OPTIONS[0])),
        key="resources_budget",
    )

    back, forward = render_nav("presence", "Continuer")
    if back:
        navigate("presence")
    if forward:
        errors = []
        if "Aucun matériel" in q10 and len(q10) > 1:
            errors.append("« Aucun matériel » ne peut pas être associé à un équipement.")
        if "Aucun appui" in q12 and len(q12) > 1:
            errors.append("« Aucun appui » ne peut pas être associé à une autre solution.")
        if "Non défini" in q12 and len(q12) > 1:
            errors.append("« Non défini » ne peut pas être associé à une autre solution.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update(
                {
                    "q8": q8,
                    "q9": competencies,
                    "q10": q10,
                    "q11": q11,
                    "q12": q12,
                    "q13": q13,
                }
            )
            st.session_state.return_to_review = False
            navigate("review")


def review_page() -> None:
    answers = st.session_state.answers
    logo()
    st.markdown('<div class="cap-eyebrow">Vérification</div>', unsafe_allow_html=True)
    st.header("Récapitulatif")
    st.markdown(
        '<div class="cap-question">Relisez vos réponses avant de lancer l’analyse.</div>',
        unsafe_allow_html=True,
    )

    review_card(
        "Votre cible",
        [
            ("Profils :", join_values(answers.get("q2", []))),
            ("Canaux d’information :", join_values(answers.get("q4", []))),
            ("Sources :", join_values(answers.get("q5", []))),
        ],
    )
    if st.button("Modifier la cible", type="secondary", key="edit_target"):
        st.session_state.return_to_review = True
        navigate("target")

    review_card(
        "Votre objectif",
        [
            ("Objectif :", answers.get("q6", "Non renseigné")),
            ("Indicateur :", answers.get("indicator", "Non renseigné")),
            ("Résultat attendu :", answers.get("target", "Non renseigné")),
            ("Échéance :", answers.get("deadline", "Non renseigné")),
        ],
    )
    if st.button("Modifier l’objectif", type="secondary", key="edit_objective"):
        st.session_state.return_to_review = True
        navigate("objective")

    statuses = answers.get("q7", {})
    presence = " · ".join(
        f"{platform} : {statuses.get(platform, 'Aucun compte')}"
        for platform in PLATFORM_NAMES
    )
    review_card("Votre présence actuelle", [("Comptes :", presence)])
    if st.button("Modifier la présence", type="secondary", key="edit_presence"):
        st.session_state.return_to_review = True
        navigate("presence")

    skill_summary = " · ".join(
        f"{skill} : {level}"
        for skill, level in answers.get("q9", {}).items()
    )
    review_card(
        "Vos moyens",
        [
            ("Temps :", answers.get("q8", "Non renseigné")),
            ("Compétences :", skill_summary or "Non renseigné"),
            ("Matériel :", join_values(answers.get("q10", []))),
            ("Pilotage :", answers.get("q11", "Non renseigné")),
            ("Appui :", join_values(answers.get("q12", []))),
            ("Budget :", answers.get("q13", "Non renseigné")),
        ],
    )
    if st.button("Modifier les moyens", type="secondary", key="edit_resources"):
        st.session_state.return_to_review = True
        navigate("resources")

    back, validate = render_nav("resources", "Valider")
    if back:
        navigate("resources")
    if validate:
        with st.spinner("Analyse en cours…"):
            st.session_state.result = evaluate(answers)
        navigate("result")


def result_page() -> None:
    result = st.session_state.result
    answers = st.session_state.answers
    if not result:
        navigate("home")

    logo()
    st.markdown('<div class="cap-eyebrow">Votre recommandation</div>', unsafe_allow_html=True)
    readiness_advice = (
        "Clarifiez d’abord les informations manquantes avant d’organiser le lancement."
    )

    if result["winner"] is None:
        st.header("Résultat à consolider")
        st.markdown(
            '<div class="cap-lead" style="margin-left:0">Les informations renseignées ne permettent pas de départager les plateformes de manière suffisamment fiable.</div>',
            unsafe_allow_html=True,
        )
    else:
        winner = result["winner"]
        score = result["scores"][winner]
        if result["readiness"] >= 75:
            deployment_text = (
                "Votre niveau de préparation permet d’engager le déploiement."
            )
            readiness_advice = (
                "Les conditions sont réunies. Programmez vos premières publications "
                "et suivez leurs résultats."
            )
        elif result["readiness"] >= 50:
            deployment_text = (
                "Réalisez les actions indiquées ci-dessous avant de programmer "
                "le lancement."
            )
            readiness_advice = (
                "Complétez les actions indiquées dans l’encadré « Avant de commencer », "
                "puis programmez un premier mois de publications."
            )
        else:
            deployment_text = (
                "Cette recommandation ne doit pas encore être déployée. "
                "Réalisez d’abord les actions indiquées ci-dessous."
            )
            readiness_advice = (
                "Ne commencez pas encore. Réalisez d’abord les actions indiquées "
                "dans l’encadré « Avant de commencer »."
            )
        st.markdown(
            f"""
            <div class="cap-recommendation">
                <div class="cap-platform">{escape(winner)}</div>
                <div class="cap-score">Indice de pertinence&nbsp;: {score:.0f}&nbsp;%</div>
            </div>
            <p class="cap-lead" style="margin-left:0">
                Parmi les réseaux sur lesquels votre cible recherche ses informations,
                {escape(winner)} est le plus cohérent avec votre objectif et son profil.
                Le temps disponible complète l’analyse et détermine surtout votre niveau
                de préparation. {escape(deployment_text)}
            </p>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        reliability_notes = result.get("reliability_notes", [])
        if reliability_notes:
            reliability_detail = " · ".join(reliability_notes) + "."
        else:
            reliability_detail = "Persona, besoins, réseaux et sources documentés."
        st.markdown(
            f"""
                <div class="cap-card">
                    <div class="cap-card-label">Fiabilité des données sur la cible</div>
                    <div class="cap-card-value">{result["reliability_label"]} · {result["reliability"]:.0f} %</div>
                    <div class="cap-note" style="margin-top:.45rem">{escape(reliability_detail)}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
                <div class="cap-card">
                    <div class="cap-card-label">Niveau de préparation</div>
                    <div class="cap-card-value">{result["readiness_label"]} · {result["readiness"]:.0f} %</div>
                    <div class="cap-card-purpose">
                        {escape(readiness_advice)}
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

    launch_actions = result.get("launch_actions", [])
    if launch_actions:
        actions_html = "".join(
            f"""
            <div class="cap-action">
                <div class="cap-action-number">{index:02}</div>
                <div class="cap-action-text">{escape(action)}</div>
            </div>
            """
            for index, action in enumerate(launch_actions, start=1)
        )
        st.markdown(
            f"""
            <div class="cap-launch-box">
                <div class="cap-launch-kicker">Préparation opérationnelle</div>
                <div class="cap-launch-title">Avant de commencer</div>
                <div class="cap-launch-intro">
                    Le diagnostic a relevé les actions suivantes. Réalisez-les avant
                    de programmer vos premières publications.
                </div>
                {actions_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    pdf_bytes = build_summary_pdf(answers, result)
    st.write("")
    download_col, guide_col = st.columns(2)
    with download_col:
        st.download_button(
            "Télécharger ma synthèse",
            data=pdf_bytes,
            file_name="synthese_CAP.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
        )
    with guide_col:
        guide_path = (
            GUIDES_DIR / f"{result['winner'].lower()}.pdf"
            if result["winner"]
            else None
        )
        if guide_path and guide_path.exists():
            st.download_button(
                "Accéder au guide",
                data=guide_path.read_bytes(),
                file_name=f"guide_CAP_{result['winner'].lower()}.pdf",
                mime="application/pdf",
                type="primary",
                width="stretch",
            )
        else:
            st.button(
                "Guide bientôt disponible",
                disabled=True,
                width="stretch",
            )

    left, spacer, right = st.columns([1.2, 2, 1.4])
    with left:
        if st.button("Précédent", type="secondary", width="stretch"):
            navigate("review")
    with right:
        if st.button("Recommencer", type="secondary", width="stretch"):
            reset_diagnostic()

    st.markdown(
        '<p class="cap-note">Les réponses restent dans votre session et sont supprimées lorsque celle-ci est fermée.</p>',
        unsafe_allow_html=True,
    )


inject_css()
init_state()

PAGES = {
    "home": home_page,
    "prepare": prepare_page,
    "target": target_page,
    "objective": objective_page,
    "presence": presence_page,
    "resources": resources_page,
    "review": review_page,
    "result": result_page,
}

PAGES.get(st.session_state.screen, home_page)()
