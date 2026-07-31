from pathlib import Path
from html import escape

import streamlit as st

from config import (
    APP_SUPPORT_OPTIONS,
    BUDGET_OPTIONS,
    COMPETENCY_LEVELS,
    DISCOVERY_MODE_OPTIONS,
    EVIDENCE_QUALITY_OPTIONS,
    EQUIPMENT_OPTIONS,
    INDICATOR_OPTIONS,
    OBJECTIVE_OPTIONS,
    PILOT_OPTIONS,
    PLATFORM_FORMATS,
    PLATFORM_NAMES,
    PROFILE_OPTIONS,
    SOURCE_OPTIONS,
    TARGET_NETWORK_OPTIONS,
    TIME_OPTIONS,
)

try:
    from config import PLATFORM_RESULT_OPTIONS
except ImportError:
    # Permet à l’application de rester disponible si app.py est déployé avant
    # config.py. Les statuts de compte ne sont volontairement pas repris.
    PLATFORM_RESULT_OPTIONS = [
        "Aucun résultat identifié",
        "Audience cible engagée",
        "Contacts obtenus",
    ]
from pdf_export import build_summary_pdf
from scoring import compare_platforms, evaluate, required_skills_for_formats


BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo_cap.svg"

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

        .cap-result-box {
            border: 1px solid #D9DCDD;
            border-radius: 20px;
            background: var(--cap-soft);
            margin: 1rem 0 1.1rem 0;
            padding: 1.55rem 1.55rem 1.45rem 1.55rem;
            text-align: center;
        }

        .cap-result-title {
            color: var(--cap-black);
            font-size: clamp(1.75rem, 5vw, 2.8rem);
            font-weight: 760;
            letter-spacing: -0.04em;
            line-height: 1.08;
            margin-bottom: 0.65rem;
        }

        .cap-result-text {
            color: #3F4246;
            font-size: 1rem;
            line-height: 1.55;
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
    valid_default = [value for value in default if value in options]
    selected = st.pills(
        label,
        options,
        selection_mode="multi",
        default=valid_default,
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

    persona_options = ["Oui", "Non"]
    saved_persona_status = answers.get("q1")
    saved_persona_index = (
        persona_options.index(saved_persona_status)
        if saved_persona_status in persona_options
        else None
    )
    q1 = st.radio(
        "Persona défini ?",
        persona_options,
        index=saved_persona_index,
        horizontal=True,
        key="target_persona",
    )
    saved_profiles = [
        profile for profile in answers.get("q2", []) if profile in PROFILE_OPTIONS
    ]
    saved_profile = saved_profiles[0] if saved_profiles else "Non identifié"
    selected_profile = st.selectbox(
        "Quel persona souhaitez-vous analyser ?",
        PROFILE_OPTIONS,
        index=PROFILE_OPTIONS.index(saved_profile),
        key="target_profile",
        help=(
            "Réalisez un diagnostic distinct pour chaque persona. Deux profils "
            "peuvent avoir des besoins et des usages différents."
        ),
    )
    q2 = [selected_profile]
    priority_need = st.text_input(
        "Quel besoin d’information prioritaire avez-vous identifié chez ce persona ?",
        value=answers.get("priority_need", ""),
        placeholder="Ex. choisir la forme juridique adaptée à son activité",
        key="target_priority_need",
        help=(
            "Renseignez un besoin observé dans vos échanges, entretiens, "
            "questionnaires, données clients ou recherches sectorielles."
        ),
    )

    q4 = select_many(
        "Sur quels réseaux ce persona recherche-t-il des informations liées à ce besoin ?",
        TARGET_NETWORK_OPTIONS,
        answers.get("q4", []),
        "target_networks",
        "Ne retenez pas ses réseaux de divertissement s’ils ne sont pas utilisés pour rechercher cette information.",
    )
    q4_modes_by_network = {}
    saved_modes = answers.get("q4_modes_by_network", {})
    selected_known_networks = [
        platform for platform in q4 if platform in PLATFORM_NAMES
    ]
    if selected_known_networks:
        st.markdown("**Précisez l’usage observé sur chaque réseau**")
        st.caption(
            "Indiquez ce que le persona fait réellement lorsqu’il cherche "
            "l’information liée à son besoin."
        )
        for platform in selected_known_networks:
            saved_mode = saved_modes.get(platform, "Non identifié")
            if saved_mode not in DISCOVERY_MODE_OPTIONS:
                saved_mode = "Non identifié"
            q4_modes_by_network[platform] = st.selectbox(
                f"Sur {platform}, comment ce persona recherche-t-il concrètement cette information ?",
                DISCOVERY_MODE_OPTIONS,
                index=DISCOVERY_MODE_OPTIONS.index(saved_mode),
                key=f"target_discovery_mode_{platform}",
            )
    q5 = select_many(
        "D’où viennent vos informations ?",
        SOURCE_OPTIONS,
        answers.get("q5", []),
        "target_sources",
    )
    previous_quality = answers.get("q5_quality", EVIDENCE_QUALITY_OPTIONS[0])
    if previous_quality == "Récentes et confirmées":
        previous_quality = "Récentes et fiables"
    q5_quality = st.radio(
        "Les informations sur les réseaux utilisés par votre cible sont-elles récentes et fiables ?",
        EVIDENCE_QUALITY_OPTIONS,
        index=EVIDENCE_QUALITY_OPTIONS.index(previous_quality),
        horizontal=True,
        key="target_evidence_quality",
    )

    back, forward = render_nav("prepare")
    if back:
        navigate("prepare")
    if forward:
        errors = []
        if q1 is None:
            errors.append("Indiquez si le persona est défini.")
        if "Non identifié" in q4 and len(q4) > 1:
            errors.append("« Non identifié » ne peut pas être associé à un réseau.")
        unidentified_modes = [
            platform
            for platform, mode in q4_modes_by_network.items()
            if mode == "Non identifié"
        ]
        if unidentified_modes:
            errors.append(
                "Précisez comment le persona recherche cette information sur "
                f"{', '.join(unidentified_modes)}."
            )
        if "Aucune source" in q5 and len(q5) > 1:
            errors.append("« Aucune source » ne peut pas être associée à une autre source.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update(
                {
                    "q1": q1,
                    "q2": q2,
                    "q2_coherence": "Oui",
                    "q3": "Oui" if priority_need.strip() else "Non",
                    "priority_need": priority_need.strip(),
                    "q4": q4,
                    "q4_modes_by_network": q4_modes_by_network,
                    "q5": q5,
                    "q5_quality": q5_quality,
                }
            )
            answers.pop("q4_modes", None)
            next_screen("objective")


def objective_page() -> None:
    answers = st.session_state.answers
    step_header(2, "Votre objectif", "Le résultat que la communication doit produire.")

    q6 = st.selectbox(
        "Quel est votre objectif ?",
        OBJECTIVE_OPTIONS,
        index=OBJECTIVE_OPTIONS.index(answers.get("q6", "Non défini")),
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
        elif q6 == "Autre":
            st.error(
                "Choisissez un objectif proposé afin que l’outil puisse comparer "
                "les plateformes."
            )
        elif not indicator.strip() or not target.strip() or not deadline.strip():
            st.error("Renseignez l’indicateur, le résultat attendu et l’échéance.")
        elif not any(character.isdigit() for character in target):
            st.error("Indiquez un résultat attendu chiffré.")
        elif not any(character.isdigit() for character in deadline):
            st.error("Indiquez une échéance précise, par exemple « 3 mois ».")
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
        "Vos résultats actuels",
        "Ces informations servent uniquement à départager plusieurs plateformes compatibles.",
    )

    preview = compare_platforms(answers)
    compatible_platforms = preview["compatible_platforms"]

    legacy_status = {
        "Aucun": "Aucun résultat identifié",
        "Aucun compte": "Aucun résultat identifié",
        "Inactif": "Aucun résultat identifié",
        "Compte inactif": "Aucun résultat identifié",
        "Actif": "Aucun résultat identifié",
        "Compte actif": "Aucun résultat identifié",
        "Audience qualifiée": "Audience cible engagée",
        "Contacts générés": "Contacts obtenus",
    }
    statuses = {}
    if len(compatible_platforms) > 1:
        st.markdown("**Résultats obtenus auprès du persona analysé**")
        st.caption(
            "Ne retenez que les résultats obtenus avec ce persona pour le besoin "
            "étudié. Les résultats provenant d’un autre public ne comptent pas."
        )
        with st.expander("Comprendre les niveaux"):
            st.markdown(
                """
                - **Aucun résultat identifié** : aucun résultat n’a encore été observé auprès de ce persona sur cette plateforme.
                - **Audience cible engagée** : ce persona suit ou sollicite déjà le compte.
                - **Contacts obtenus** : ce persona a déjà pris contact ou demandé un rendez-vous.

                L’existence d’un compte actif ou inactif ne départage jamais les plateformes.
                """
            )
        columns = st.columns(2)
        for index, platform in enumerate(compatible_platforms):
            with columns[index % 2]:
                previous = answers.get("q7", {}).get(
                    platform, "Aucun résultat identifié"
                )
                previous = legacy_status.get(previous, previous)
                if previous not in PLATFORM_RESULT_OPTIONS:
                    previous = "Aucun résultat identifié"
                statuses[platform] = st.selectbox(
                    platform,
                    PLATFORM_RESULT_OPTIONS,
                    index=PLATFORM_RESULT_OPTIONS.index(previous),
                    key=f"status_{platform}",
                )
    elif len(compatible_platforms) == 1:
        st.info(
            f"{compatible_platforms[0]} est la seule plateforme compatible. "
            "Aucun départage n’est nécessaire."
        )
    else:
        st.warning(
            "Aucune plateforme ne correspond à la fois à l’usage observé du "
            "persona et à l’objectif du cabinet."
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

    preview = compare_platforms(answers)
    recommended = preview["winner"]
    tied_platforms = preview["tied_platforms"]

    if preview["outcome"] in {"invalid_data", "no_compatible_platform"}:
        if preview["outcome"] == "no_compatible_platform":
            st.warning(
                "Aucune plateforme ne correspond à la fois à l’usage observé du "
                "persona et à l’objectif du cabinet. Les moyens ne sont donc pas "
                "évalués à ce stade."
            )
        else:
            st.warning(
                "Les moyens seront évalués lorsque les informations stratégiques "
                "permettront de comparer les plateformes."
            )
        back, forward = render_nav("presence", "Continuer")
        if back:
            navigate("presence")
        if forward:
            st.session_state.return_to_review = False
            navigate("review")
        return

    if recommended:
        format_platforms = [recommended]
    elif tied_platforms:
        format_platforms = tied_platforms
    else:
        st.warning(
            "Les formats seront proposés lorsque les informations stratégiques "
            "permettront d’identifier une plateforme."
        )
        format_platforms = []

    q8 = st.selectbox(
        "Quel temps mensuel pouvez-vous consacrer ?",
        TIME_OPTIONS,
        index=TIME_OPTIONS.index(answers.get("q8", TIME_OPTIONS[0])),
        key="resources_time",
    )

    if format_platforms:
        compatible_formats = []
        for platform in format_platforms:
            for content_format in PLATFORM_FORMATS[platform]:
                if content_format not in compatible_formats:
                    compatible_formats.append(content_format)
        saved_formats = [
            content_format
            for content_format in answers.get("q14", [])
            if content_format in compatible_formats
        ]
        q14 = select_many(
            "Quels formats pouvez-vous produire régulièrement ?",
            compatible_formats,
            saved_formats,
            "resources_formats",
            "Les choix proposés correspondent à l’analyse réalisée. Sélectionnez "
            "uniquement les formats que le cabinet peut tenir dans la durée.",
        )
    else:
        q14 = []

    recorded_video_formats = [
        content_format
        for content_format in q14
        if content_format in {
            "Reel / vidéo courte",
            "Reel",
            "Vidéo",
            "Vidéo longue",
            "Short",
        }
    ]
    if recorded_video_formats:
        q16 = st.radio(
            "Pour les vidéos enregistrées, une personne apparaîtra-t-elle face caméra ?",
            ["Oui", "Non"],
            index=["Oui", "Non"].index(answers.get("q16", "Non")),
            horizontal=True,
            key="resources_on_camera",
            help=(
                "Répondez non si les vidéos reposent uniquement sur une voix off, "
                "une capture d’écran, une animation ou des visuels."
            ),
        )
    elif "Live" in q14:
        q16 = "Oui"
        st.info("Un Live nécessite une aisance face caméra.")
    else:
        q16 = "Non"

    required_skills = required_skills_for_formats(
        q14,
        appears_on_camera=q16 == "Oui",
    )
    competencies = {}
    if required_skills:
        st.markdown("**Votre niveau pour les compétences réellement nécessaires**")
        for skill in sorted(required_skills):
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
    skills_to_strengthen = [
        skill for skill, level in competencies.items() if level != "Autonome"
    ]
    legacy_support = {
        "Appui interne": "Aide interne",
        "Prestataire externe": "Prestataire",
    }
    saved_support = [
        legacy_support.get(item, item)
        for item in answers.get("q12", [])
        if legacy_support.get(item, item) in APP_SUPPORT_OPTIONS
    ]
    if skills_to_strengthen:
        q12 = select_many(
            "Quelle solution avez-vous retenue pour les compétences à renforcer ?",
            APP_SUPPORT_OPTIONS,
            saved_support,
            "resources_support",
            "Sélectionnez la solution qui sera réellement utilisée avant le lancement.",
        )
    else:
        q12 = []

    legacy_budget = {
        "Budget validé": "Oui",
        "Montant à confirmer": "À vérifier",
        "Dépense indispensable non finançable": "Non",
        "Non évalué": "À vérifier",
    }
    saved_budget = legacy_budget.get(
        answers.get("q13"),
        answers.get("q13", BUDGET_OPTIONS[0]),
    )
    q13 = st.selectbox(
        "Le cabinet peut-il financer les dépenses nécessaires au lancement ?",
        BUDGET_OPTIONS,
        index=BUDGET_OPTIONS.index(saved_budget),
        key="resources_budget",
    )

    back, forward = render_nav("presence", "Continuer")
    if back:
        navigate("presence")
    if forward:
        errors = []
        if format_platforms and not q14:
            errors.append(
                "Sélectionnez au moins un format que vous pouvez produire régulièrement."
            )
        if "Aucun matériel" in q10 and len(q10) > 1:
            errors.append("« Aucun matériel » ne peut pas être associé à un équipement.")
        if skills_to_strengthen and not q12:
            errors.append(
                "Indiquez comment les compétences à renforcer seront complétées."
            )
        if "Solution à trouver" in q12 and len(q12) > 1:
            errors.append(
                "« Solution à trouver » ne peut pas être associée à une solution déjà retenue."
            )
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update(
                {
                    "q8": q8,
                    "q14": q14,
                    "q9": competencies,
                    "q10": q10,
                    "q11": q11,
                    "q12": q12,
                    "q13": q13,
                    "q15": None,
                    "q16": q16,
                }
            )
            st.session_state.return_to_review = False
            navigate("review")


def review_page() -> None:
    answers = st.session_state.answers
    preview = compare_platforms(answers)
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
            ("Persona :", join_values(answers.get("q2", []))),
            ("Besoin prioritaire :", answers.get("priority_need", "Non renseigné")),
            ("Canaux d’information :", join_values(answers.get("q4", []))),
            (
                "Usage par réseau :",
                " · ".join(
                    f"{platform} : {mode}"
                    for platform, mode in answers.get(
                        "q4_modes_by_network", {}
                    ).items()
                )
                or "Non renseigné",
            ),
            ("Sources :", join_values(answers.get("q5", []))),
            (
                "Vérification des informations :",
                answers.get("q5_quality", "Non renseignée"),
            ),
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
        f"{platform} : {status}" for platform, status in statuses.items()
    ) or "Aucun départage nécessaire"
    review_card(
        "Résultats actuels",
        [("Résultats auprès du persona :", presence)],
    )
    if st.button("Modifier la présence", type="secondary", key="edit_presence"):
        st.session_state.return_to_review = True
        navigate("presence")

    if preview["outcome"] in {"recommended", "tie"}:
        skill_summary = " · ".join(
            f"{skill} : {level}"
            for skill, level in answers.get("q9", {}).items()
        )
        review_card(
            "Vos moyens",
            [
                ("Temps :", answers.get("q8", "Non renseigné")),
                ("Formats :", join_values(answers.get("q14", []))),
                (
                    "Présence face caméra :",
                    answers.get("q16", "Non")
                    if any(
                        content_format
                        in {
                            "Reel / vidéo courte",
                            "Reel",
                            "Vidéo",
                            "Vidéo longue",
                            "Short",
                            "Live",
                        }
                        for content_format in answers.get("q14", [])
                    )
                    else "Sans objet",
                ),
                ("Compétences :", skill_summary or "Non renseigné"),
                ("Matériel :", join_values(answers.get("q10", []))),
                ("Pilotage :", answers.get("q11", "Non renseigné")),
                (
                    "Solution pour les compétences :",
                    join_values(answers.get("q12", []))
                    if answers.get("q12")
                    else "Sans objet",
                ),
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
    st.markdown(
        '<div class="cap-eyebrow cap-center">Résultat du diagnostic</div>',
        unsafe_allow_html=True,
    )
    strategic_status = result["strategic_status"]
    winner = result["winner"]
    tied_platforms = result.get("tied_platforms", [])
    observation_platform = result.get("observation_platform")
    selection_outcome = result.get("selection_outcome")

    if strategic_status != "Choix validé":
        result_title = strategic_status
        result_text = (
            "Aucune plateforme ne peut être recommandée à ce stade. "
            "Corrigez les informations indiquées, puis relancez le diagnostic."
        )
    elif selection_outcome == "no_compatible_platform":
        result_title = "Aucune plateforme compatible"
        result_text = (
            "Les réseaux indiqués sont utilisés par le persona, mais aucun ne "
            "correspond à la fois à sa manière d’y rechercher cette information "
            "et à l’objectif du cabinet. Vérifiez les réponses ou adaptez l’objectif."
        )
    elif winner and result["feasibility_label"] == "Projet prêt":
        result_title = "Tout est prêt"
        result_text = (
            f"Vous pouvez vous lancer. {winner} est la plateforme la plus "
            "cohérente avec votre stratégie et vos moyens."
        )
    elif winner:
        result_title = result["feasibility_label"]
        result_text = (
            f"{winner} est la plateforme la plus cohérente avec votre stratégie. "
            "Consultez la synthèse pour préparer son lancement."
        )
    else:
        platforms_text = ", ".join(tied_platforms)
        result_title = "Plateformes équivalentes"
        if observation_platform:
            result_text = (
                f"Aucun élément objectif ne permet de départager {platforms_text}. "
                f"{observation_platform} est retenue pour la période d’observation."
            )
        else:
            result_text = (
                f"Aucun élément objectif ne permet de départager {platforms_text}. "
                "Retenez une seule plateforme pour la période d’observation définie."
            )

    st.markdown(
        f"""
        <div class="cap-result-box">
            <div class="cap-result-title">{escape(result_title)}</div>
            <div class="cap-result-text">{escape(result_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_bytes = build_summary_pdf(answers, result)
    st.write("")
    if strategic_status == "Choix validé" and winner:
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
            st.button(
                "Guide de la plateforme non intégré",
                disabled=True,
                width="stretch",
            )
    else:
        left_download, download_col, right_download = st.columns([1, 2, 1])
        with download_col:
            st.download_button(
                "Télécharger ma synthèse",
                data=pdf_bytes,
                file_name="synthese_CAP.pdf",
                mime="application/pdf",
                type="primary",
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
