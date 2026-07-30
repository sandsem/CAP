from pathlib import Path
from html import escape

import streamlit as st

from config import (
    AUDIENCE_EFFECT_OPTIONS,
    APP_SUPPORT_OPTIONS,
    BUDGET_OPTIONS,
    COMPETENCY_LEVELS,
    DISCOVERY_MODE_OPTIONS,
    EDITORIAL_TREATMENT_OPTIONS,
    EVIDENCE_QUALITY_OPTIONS,
    EQUIPMENT_OPTIONS,
    INDICATOR_OPTIONS,
    OBJECTIVE_OPTIONS,
    PILOT_OPTIONS,
    PLATFORM_FORMATS,
    PLATFORM_NAMES,
    PLATFORM_STATUS_OPTIONS,
    PROFILE_OPTIONS,
    SOURCE_OPTIONS,
    TARGET_NETWORK_OPTIONS,
    TIME_OPTIONS,
)
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
    priority_need = st.text_input(
        "Quel besoin prioritaire votre cible cherche-t-elle à résoudre ?",
        value=answers.get("priority_need", ""),
        placeholder="Ex. passer de la micro-entreprise à une société",
        key="target_priority_need",
    )
    if q3 == "Non":
        st.warning(
            "Recensez au moins un besoin prioritaire avant de poursuivre le diagnostic."
        )

    if len(q2) > 1:
        coherence_options = ["Oui", "À vérifier", "Non"]
        saved_coherence = {
            "Partiellement": "À vérifier",
        }.get(
            answers.get("q2_coherence", "Oui"),
            answers.get("q2_coherence", "Oui"),
        )
        if saved_coherence not in coherence_options:
            saved_coherence = "À vérifier"
        q2_coherence = st.radio(
            "Les profils sélectionnés recherchent-ils la même information sur les mêmes réseaux ?",
            coherence_options,
            index=coherence_options.index(saved_coherence),
            horizontal=True,
            key="target_profile_coherence",
        )
        if q2_coherence == "À vérifier":
            st.warning(
                "Confirmez ce point auprès de la cible. Si les besoins ou les "
                "réseaux diffèrent, conservez seulement les profils comparables "
                "et réalisez un diagnostic séparé pour les autres."
            )
        elif q2_coherence == "Non":
            st.warning(
                "Conservez uniquement les profils qui recherchent cette information "
                "sur les mêmes réseaux, puis réalisez un autre diagnostic pour les autres."
            )
    else:
        q2_coherence = "Oui"

    q4 = select_many(
        "Sur quels réseaux votre cible recherche-t-elle des informations liées au besoin auquel votre cabinet souhaite répondre ?",
        TARGET_NETWORK_OPTIONS,
        answers.get("q4", []),
        "target_networks",
        "Ne retenez pas ses réseaux de divertissement s’ils ne sont pas utilisés pour rechercher cette information.",
    )
    q4_modes = select_many(
        "Comment accède-t-elle habituellement à cette information ?",
        DISCOVERY_MODE_OPTIONS,
        answers.get("q4_modes", []),
        "target_discovery_modes",
        "Sélectionnez les usages réellement observés, et non les fonctions simplement disponibles sur la plateforme.",
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
        if q1 == "Non":
            errors.append("Persona non défini — complétez votre persona avant de poursuivre.")
        if not q2 or "Non identifié" in q2:
            errors.append("Identifiez au moins un profil cible.")
        if len(q2) > 3:
            errors.append("Sélectionnez trois profils au maximum.")
        if q3 == "Non" or not priority_need.strip():
            errors.append(
                "Précisez au moins un besoin prioritaire de la cible avant de poursuivre."
            )
        if q2_coherence == "Non":
            errors.append(
                "Réalisez un diagnostic distinct pour chaque persona sélectionné."
            )
        if "Non identifié" in q4 and len(q4) > 1:
            errors.append("« Non identifié » ne peut pas être associé à un réseau.")
        if not q4_modes or "Non identifié" in q4_modes:
            errors.append(
                "Précisez comment la cible accède habituellement à cette information."
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
                    "q2_coherence": q2_coherence,
                    "q3": q3,
                    "priority_need": priority_need.strip(),
                    "q4": q4,
                    "q4_modes": q4_modes,
                    "q5": q5,
                    "q5_quality": q5_quality,
                }
            )
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

    q6_treatment = st.selectbox(
        "Comment souhaitez-vous traiter vos contenus ?",
        EDITORIAL_TREATMENT_OPTIONS,
        index=EDITORIAL_TREATMENT_OPTIONS.index(
            answers.get("q6_treatment", EDITORIAL_TREATMENT_OPTIONS[0])
        ),
        help=(
            "Ce choix décrit la manière dont le cabinet souhaite présenter son "
            "expertise, indépendamment du format utilisé."
        ),
        key="objective_treatment",
    )
    q6_effect = st.selectbox(
        "Quel effet principal recherchez-vous auprès de l’audience ?",
        AUDIENCE_EFFECT_OPTIONS,
        index=AUDIENCE_EFFECT_OPTIONS.index(
            answers.get("q6_effect", AUDIENCE_EFFECT_OPTIONS[0])
        ),
        key="objective_effect",
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
        elif q6_treatment == "Non défini" or q6_effect == "Non défini":
            st.error(
                "Précisez le traitement éditorial et l’effet recherché avant de poursuivre."
            )
        elif not indicator.strip() or not target.strip() or not deadline.strip():
            st.error("Renseignez l’indicateur, le résultat attendu et l’échéance.")
        else:
            answers.update(
                {
                    "q6": q6,
                    "q6_treatment": q6_treatment,
                    "q6_effect": q6_effect,
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

    preview = compare_platforms(answers)
    recommended = preview["winner"]
    tied_platforms = preview["tied_platforms"]

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

    required_skills = required_skills_for_formats(q14)
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
            ("Besoin prioritaire :", answers.get("priority_need", "Non renseigné")),
            ("Canaux d’information :", join_values(answers.get("q4", []))),
            ("Mode d’accès :", join_values(answers.get("q4_modes", []))),
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
            ("Traitement éditorial :", answers.get("q6_treatment", "Non renseigné")),
            ("Effet recherché :", answers.get("q6_effect", "Non renseigné")),
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
            ("Formats :", join_values(answers.get("q14", []))),
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
    st.markdown('<div class="cap-eyebrow">Résultat du diagnostic</div>', unsafe_allow_html=True)
    strategic_status = result["strategic_status"]
    winner = result["winner"]
    tied_platforms = result.get("tied_platforms", [])
    observation_platform = result.get("observation_platform")

    if strategic_status != "Choix validé":
        result_title = strategic_status
        result_text = (
            "Aucune plateforme ne peut être recommandée à ce stade. "
            "Corrigez les informations indiquées, puis relancez le diagnostic."
        )
        actions_to_show = result.get("decision_notes", [])
    elif winner and result["feasibility_label"] == "Projet prêt":
        result_title = "Tout est prêt"
        result_text = (
            f"Vous pouvez vous lancer. {winner} est la plateforme la plus "
            "cohérente avec votre stratégie et vos moyens."
        )
        actions_to_show = []
    elif winner:
        result_title = result["feasibility_label"]
        result_text = (
            f"{winner} est la plateforme la plus cohérente avec votre stratégie. "
            "Les moyens indiqués ci-dessous doivent être revus avant de commencer."
        )
        actions_to_show = result.get("launch_actions", [])
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
        actions_to_show = result.get("launch_actions", [])

    st.markdown(
        f"""
        <div class="cap-result-box">
            <div class="cap-result-title">{escape(result_title)}</div>
            <div class="cap-result-text">{escape(result_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if actions_to_show:
        actions_html = "".join(
            f"""
            <div class="cap-action">
                <div class="cap-action-number">{index:02}</div>
                <div class="cap-action-text">{escape(action)}</div>
            </div>
            """
            for index, action in enumerate(actions_to_show, start=1)
        )
        box_kicker = "Actions nécessaires"
        box_title = "À revoir"
        box_intro = (
            "Corrigez ces éléments avant de relancer le diagnostic."
            if strategic_status != "Choix validé"
            else "Réalisez ces actions avant de commencer."
        )
        st.markdown(
            f"""
            <div class="cap-launch-box">
                <div class="cap-launch-kicker">{escape(box_kicker)}</div>
                <div class="cap-launch-title">{escape(box_title)}</div>
                <div class="cap-launch-intro">
                    {escape(box_intro)}
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
        st.button(
            (
                "Guide de la plateforme non intégré"
                if winner
                else "Guide disponible après recommandation"
            ),
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
