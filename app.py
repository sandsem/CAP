from html import escape
from pathlib import Path

import streamlit as st

from config import (
    APP_SUPPORT_OPTIONS,
    COMPETENCY_LEVELS,
    EVIDENCE_QUALITY_OPTIONS,
    EQUIPMENT_OPTIONS,
    GENERIC_FORMATS,
    INDICATOR_OPTIONS,
    OBJECTIVE_OPTIONS,
    NO_PILOT,
    OUT_OF_SCOPE_NETWORK,
    PILOT_OPTIONS,
    PLATFORM_NAMES,
    PROFILE_OPTIONS,
    SOURCE_OPTIONS,
    SUPPORT_CONFIRMATION_LABELS,
    TIME_OPTIONS,
    UNKNOWN_NETWORK,
    VIDEO_FORMATS,
)
from pdf_export import build_summary_pdf
from scoring import evaluate, required_skills_for_formats


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
        :root { --black:#111; --muted:#6B7280; --line:#E3E5E7; --soft:#F7F8F8; }
        header[data-testid="stHeader"], [data-testid="collapsedControl"],
        [data-testid="stToolbar"], [data-testid="stAppDeployButton"], footer { display:none; }
        .stApp { background:#fff; color:var(--black); }
        .block-container { max-width:860px; padding-top:2.2rem; padding-bottom:3.5rem; }
        h1,h2,h3,p,label,div { font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
        h1 { letter-spacing:-.045em; font-size:clamp(2.25rem,6vw,4.2rem)!important; line-height:1.02!important; }
        h2 { letter-spacing:-.035em; font-size:clamp(1.65rem,4vw,2.55rem)!important; }
        .cap-center { text-align:center; }
        .cap-lead { color:#3d4044; font-size:1.1rem; line-height:1.55; margin:.8rem auto 1.8rem; max-width:620px; }
        .cap-eyebrow { color:var(--muted); font-size:.78rem; font-weight:750; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.65rem; }
        .cap-question { color:var(--muted); font-size:.93rem; margin-top:-.35rem; margin-bottom:1.1rem; }
        .cap-stepbar { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:1.2rem 0 2.2rem; }
        .cap-step { height:4px; border-radius:99px; background:#E5E7EB; }
        .cap-step.active { background:var(--black); }
        .cap-nav-spacer { height:clamp(2.5rem,7vh,5rem); }
        .cap-review-card { border:1px solid var(--line); border-radius:16px; padding:1rem 1.15rem; margin-bottom:.75rem; background:#fff; }
        .cap-review-title { font-size:1.05rem; font-weight:720; margin-bottom:.55rem; }
        .cap-review-line { color:#36393D; font-size:.92rem; line-height:1.55; }
        .cap-result-box { border:1px solid #D9DCDD; border-radius:20px; background:var(--soft); margin:1rem 0 1.25rem; padding:1.7rem; text-align:center; }
        .cap-result-title { font-size:clamp(1.75rem,5vw,2.8rem); font-weight:760; letter-spacing:-.04em; line-height:1.08; margin-bottom:.65rem; }
        .cap-result-text { color:#3F4246; font-size:1rem; line-height:1.55; }
        .cap-note { color:var(--muted); font-size:.84rem; line-height:1.5; }
        .stButton>button,.stDownloadButton>button { min-height:46px; border-radius:10px; font-weight:650; }
        button[kind="primary"],.stDownloadButton>button { background:var(--black)!important; color:#fff!important; border:1px solid var(--black)!important; }
        button[kind="secondary"] { background:#fff!important; color:var(--black)!important; border:1px solid #D8DADD!important; }
        [data-testid="stPills"] button { background:#fff!important; color:var(--black)!important; border:1px solid #C9CDD2!important; }
        [data-testid="stPills"] button[aria-pressed="true"] { background:var(--black)!important; color:#fff!important; border-color:var(--black)!important; }
        [data-testid="stRadio"] [aria-checked="true"]>div:first-child { background:var(--black)!important; border-color:var(--black)!important; }
        [data-testid="InputInstructions"], [data-testid*="InputInstructions"] { display:none!important; }
        div[data-baseweb="popover"], div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] [role="listbox"],
        div[data-baseweb="menu"], ul[role="listbox"], div[role="listbox"] {
            background:#111!important; color:#fff!important;
        }
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] [role="option"],
        ul[role="listbox"] [role="option"], div[role="listbox"] [role="option"] {
            background:#111!important; color:#fff!important;
        }
        div[data-baseweb="popover"] li *,
        div[data-baseweb="popover"] [role="option"] *,
        ul[role="listbox"] [role="option"] *, div[role="listbox"] [role="option"] * {
            color:#fff!important;
        }
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [role="option"]:hover,
        ul[role="listbox"] [role="option"]:hover,
        div[role="listbox"] [role="option"]:hover,
        [role="option"][aria-selected="true"] { background:#343434!important; }
        div[data-testid="stAlert"] { border-radius:12px; }
        @media(max-width:640px){ .block-container{padding:1.3rem 1rem 2.5rem}.cap-nav-spacer{height:2rem} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    for key, value in {
        "screen": "home",
        "answers": {},
        "result": None,
        "return_to_review": False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logo(center: bool = False) -> None:
    if not LOGO_PATH.exists():
        return
    if center:
        left, middle, right = st.columns([1, .28, 1])
        with middle:
            st.image(str(LOGO_PATH), width="stretch")
    else:
        st.image(str(LOGO_PATH), width=62)


def step_header(step: int, title: str, subtitle: str = "") -> None:
    logo()
    st.markdown(f'<div class="cap-eyebrow">Étape {step} sur 3</div>', unsafe_allow_html=True)
    bars = "".join(
        f'<div class="cap-step{" active" if index <= step else ""}"></div>'
        for index in range(1, 4)
    )
    st.markdown(f'<div class="cap-stepbar">{bars}</div>', unsafe_allow_html=True)
    st.header(title)
    if subtitle:
        st.markdown(f'<div class="cap-question">{subtitle}</div>', unsafe_allow_html=True)


def navigate(screen: str) -> None:
    st.session_state.screen = screen
    st.rerun()


def reset_diagnostic() -> None:
    for key in list(st.session_state):
        if key.startswith(("target_", "objective_", "resources_", "skill_", "support_")):
            del st.session_state[key]
    st.session_state.answers = {}
    st.session_state.result = None
    st.session_state.return_to_review = False
    navigate("home")


def render_nav(previous: str, continue_label: str = "Continuer") -> tuple[bool, bool]:
    st.markdown('<div class="cap-nav-spacer"></div>', unsafe_allow_html=True)
    left, spacer, right = st.columns([1.2, 2.2, 1.4])
    with left:
        back = st.button("Précédent", type="secondary", width="stretch", key=f"back_{st.session_state.screen}")
    with right:
        forward = st.button(continue_label, type="primary", width="stretch", key=f"next_{st.session_state.screen}")
    return back, forward


def next_screen(default: str) -> None:
    if st.session_state.return_to_review:
        st.session_state.return_to_review = False
        navigate("review")
        return
    navigate(default)


def select_many(label: str, options: list[str], default: list[str], key: str, help_text: str | None = None) -> list[str]:
    selected = st.pills(
        label,
        options,
        selection_mode="multi",
        default=[item for item in default if item in options],
        key=key,
        help=help_text,
    )
    return list(selected or [])


def join_values(values: list[str]) -> str:
    return ", ".join(values) if values else "Non renseigné"


def review_card(title: str, rows: list[tuple[str, str]]) -> None:
    content = "".join(
        f'<div class="cap-review-line"><strong>{escape(label)}</strong> {escape(str(value))}</div>'
        for label, value in rows
    )
    st.markdown(
        f'<div class="cap-review-card"><div class="cap-review-title">{escape(title)}</div>{content}</div>',
        unsafe_allow_html=True,
    )


def home_page() -> None:
    st.write("")
    logo(center=True)
    st.markdown(
        '<div class="cap-center"><h1>Bienvenue</h1><div class="cap-lead">Identifiez la plateforme la plus adaptée à votre cabinet.</div></div>',
        unsafe_allow_html=True,
    )
    left, middle, right = st.columns([1, 1.1, 1])
    with middle:
        if st.button("Commencer", type="primary", width="stretch"):
            navigate("prepare")
    st.markdown('<p class="cap-center cap-note">Ce diagnostic ne vous prendra que quelques minutes.</p>', unsafe_allow_html=True)


def prepare_page() -> None:
    st.write("")
    logo(center=True)
    st.markdown(
        '<div class="cap-center"><h2>Avant de commencer</h2><div class="cap-lead">Préparez un persona, un objectif chiffré et une estimation des moyens disponibles. Réalisez un diagnostic distinct pour chaque persona.</div></div>',
        unsafe_allow_html=True,
    )
    back, forward = render_nav("home")
    if back:
        navigate("home")
    if forward:
        navigate("target")


def target_page() -> None:
    answers = st.session_state.answers
    step_header(1, "Votre cible", "Un diagnostic porte sur un seul persona et un seul besoin prioritaire.")

    persona_status = st.radio(
        "Votre persona est-il défini ?",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(answers["q1"]) if answers.get("q1") in {"Oui", "Non"} else None,
        horizontal=True,
        key="target_persona_status",
    )
    saved_profile = (answers.get("q2") or [None])[0]
    profile = st.selectbox(
        "Quel persona souhaitez-vous analyser ?",
        PROFILE_OPTIONS,
        index=PROFILE_OPTIONS.index(saved_profile) if saved_profile in PROFILE_OPTIONS else None,
        placeholder="Choisir un persona",
        key="target_profile",
        help="Si le cabinet vise plusieurs publics, recommencez le diagnostic pour chacun.",
    )
    custom_profile = ""
    if profile == "Autre":
        custom_profile = st.text_input(
            "Précisez ce persona",
            value=answers.get("custom_profile", ""),
            key="target_custom_profile",
        )

    priority_need = st.text_input(
        "Quel besoin d’information prioritaire avez-vous identifié chez ce persona ?",
        value=answers.get("priority_need", ""),
        placeholder="Ex. choisir le statut juridique adapté à son activité",
        key="target_priority_need",
        help="Cette réponse précise le sujet à traiter. Elle ne choisit pas, à elle seule, la plateforme.",
    )

    known_choice = ""
    if answers.get("q4") == [UNKNOWN_NETWORK]:
        known_choice = UNKNOWN_NETWORK
    elif answers.get("q4") == [OUT_OF_SCOPE_NETWORK]:
        known_choice = OUT_OF_SCOPE_NETWORK
    elif any(item in PLATFORM_NAMES for item in answers.get("q4", [])):
        known_choice = "Oui"
    network_knowledge = st.radio(
        "Savez-vous sur quels réseaux ce persona recherche cette information ?",
        ["Oui", UNKNOWN_NETWORK, OUT_OF_SCOPE_NETWORK],
        index=["Oui", UNKNOWN_NETWORK, OUT_OF_SCOPE_NETWORK].index(known_choice) if known_choice else None,
        key="target_network_knowledge",
    )

    networks: list[str] = []
    preferred_network = None
    sources: list[str] = []
    evidence_quality = None
    if network_knowledge == "Oui":
        networks = select_many(
            "Quels réseaux utilise-t-il pour rechercher cette information ?",
            PLATFORM_NAMES,
            answers.get("q4", []),
            "target_networks",
        )
        if len(networks) == 1:
            preferred_network = networks[0]
        elif len(networks) > 1:
            priority_options = networks + [UNKNOWN_NETWORK]
            saved_priority = answers.get("q4_priority")
            preferred_network = st.selectbox(
                "Parmi ces réseaux, lequel utilise-t-il le plus souvent pour rechercher cette information ?",
                priority_options,
                index=priority_options.index(saved_priority) if saved_priority in priority_options else None,
                placeholder="Choisir un réseau ou « Je ne sais pas »",
                key="target_preferred_network",
            )

        has_source = st.radio(
            "Disposez-vous d’au moins une source pour confirmer cette réponse ?",
            ["Oui", "Non"],
            index=0 if answers.get("q5") and answers.get("q5") != ["Aucune source"] else (1 if answers.get("q5") == ["Aucune source"] else None),
            horizontal=True,
            key="target_has_source",
        )
        if has_source == "Oui":
            sources = select_many(
                "D’où viennent vos informations ?",
                [item for item in SOURCE_OPTIONS if item != "Aucune source"],
                answers.get("q5", []),
                "target_sources",
            )
            evidence_quality = st.radio(
                "Ces informations sont-elles récentes et fiables ?",
                EVIDENCE_QUALITY_OPTIONS,
                index=EVIDENCE_QUALITY_OPTIONS.index(answers["q5_quality"]) if answers.get("q5_quality") in EVIDENCE_QUALITY_OPTIONS else None,
                horizontal=True,
                key="target_evidence_quality",
            )
        elif has_source == "Non":
            sources = ["Aucune source"]
            st.error("Vérifiez le profil de la cible à l’aide d’une source récente avant de continuer.")
    elif network_knowledge == UNKNOWN_NETWORK:
        networks = [UNKNOWN_NETWORK]
        preferred_network = UNKNOWN_NETWORK
        st.info("CAP utilisera sa base de référence pour proposer les plateformes les plus probables pour ce persona.")
    elif network_knowledge == OUT_OF_SCOPE_NETWORK:
        networks = [OUT_OF_SCOPE_NETWORK]
        st.warning("CAP compare uniquement Facebook, Instagram, TikTok et YouTube.")

    back, forward = render_nav("prepare")
    if back:
        navigate("prepare")
    if forward:
        errors: list[str] = []
        if persona_status != "Oui":
            errors.append("Finalisez le persona avant de continuer.")
        if not profile:
            errors.append("Choisissez le persona à analyser.")
        if profile == "Autre" and not custom_profile.strip():
            errors.append("Précisez le persona à analyser.")
        if not priority_need.strip():
            errors.append("Précisez le besoin d’information prioritaire du persona.")
        if not network_knowledge:
            errors.append("Indiquez si les réseaux utilisés par ce persona sont connus.")
        elif network_knowledge == OUT_OF_SCOPE_NETWORK:
            errors.append("Ce diagnostic ne peut pas comparer un réseau situé hors du périmètre de CAP.")
        elif network_knowledge == "Oui":
            if not networks:
                errors.append("Sélectionnez au moins un réseau.")
            if len(networks) > 1 and not preferred_network:
                errors.append("Indiquez le réseau le plus souvent utilisé ou choisissez « Je ne sais pas ».")
            if sources == ["Aucune source"] or not sources:
                errors.append("Indiquez une source permettant de confirmer les réseaux utilisés.")
            if evidence_quality != "Oui":
                errors.append("Confirmez que les informations sont récentes et fiables.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update({
                "q1": persona_status,
                "q2": [profile],
                "custom_profile": custom_profile.strip(),
                "priority_need": priority_need.strip(),
                "q4": networks,
                "q4_priority": preferred_network,
                "q5": sources,
                "q5_quality": evidence_quality,
            })
            next_screen("objective")


def objective_page() -> None:
    answers = st.session_state.answers
    step_header(2, "Votre objectif", "Le résultat que la communication doit produire.")

    saved_objective = answers.get("q6", "Non défini")
    objective = st.selectbox(
        "Quel est votre objectif ?",
        OBJECTIVE_OPTIONS,
        index=OBJECTIVE_OPTIONS.index(saved_objective) if saved_objective in OBJECTIVE_OPTIONS else OBJECTIVE_OPTIONS.index("Non défini"),
        key="objective_choice",
    )
    custom_objective = ""
    indicator = ""
    target = ""
    deadline = ""
    if objective != "Non défini":
        if objective == "Autre":
            custom_objective = st.text_input(
                "Précisez votre objectif",
                value=answers.get("custom_objective", ""),
                key="objective_custom",
            )
        st.caption("Précisez la mesure suivie, le résultat attendu et le délai.")
        c1, c2, c3 = st.columns(3)
        with c1:
            saved_indicator = answers.get("indicator")
            indicator_choice = st.selectbox(
                "Indicateur suivi",
                INDICATOR_OPTIONS,
                index=INDICATOR_OPTIONS.index(saved_indicator) if saved_indicator in INDICATOR_OPTIONS else None,
                placeholder="Choisir un indicateur",
                key="objective_indicator",
            )
        with c2:
            target = st.text_input(
                "Résultat attendu",
                value=answers.get("target", ""),
                placeholder="Ex. 10",
                key="objective_target",
            )
        with c3:
            deadline = st.text_input(
                "Échéance",
                value=answers.get("deadline", ""),
                placeholder="Ex. 8 mois",
                key="objective_deadline",
            )
        if indicator_choice == "Autre indicateur":
            indicator = st.text_input(
                "Précisez l’indicateur",
                value=answers.get("custom_indicator", ""),
                placeholder="Ex. demandes de devis",
                key="objective_custom_indicator",
            )
        else:
            indicator = indicator_choice or ""

    back, forward = render_nav("target")
    if back:
        navigate("target")
    if forward:
        errors: list[str] = []
        if objective == "Non défini":
            errors.append("Définissez votre objectif avant de continuer.")
        if objective == "Autre" and not custom_objective.strip():
            errors.append("Précisez votre objectif.")
        if objective != "Non défini":
            if not indicator.strip() or not target.strip() or not deadline.strip():
                errors.append("Renseignez l’indicateur, le résultat attendu et l’échéance.")
            elif not any(character.isdigit() for character in target):
                errors.append("Indiquez un résultat attendu chiffré.")
            elif not any(character.isdigit() for character in deadline):
                errors.append("Indiquez une échéance précise, par exemple « 8 mois ».")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update({
                "q6": objective,
                "custom_objective": custom_objective.strip(),
                "indicator": indicator.strip(),
                "custom_indicator": indicator.strip() if indicator not in INDICATOR_OPTIONS else "",
                "target": target.strip(),
                "deadline": deadline.strip(),
            })
            next_screen("resources")


def resources_page() -> None:
    answers = st.session_state.answers
    step_header(3, "Vos moyens", "Le temps et les ressources réellement mobilisables.")

    saved_time = answers.get("q8")
    available_time = st.selectbox(
        "Quel temps mensuel pouvez-vous consacrer ?",
        TIME_OPTIONS,
        index=TIME_OPTIONS.index(saved_time) if saved_time in TIME_OPTIONS else None,
        placeholder="Choisir un temps disponible",
        key="resources_time",
    )
    formats = select_many(
        "Quels formats pouvez-vous produire régulièrement ?",
        GENERIC_FORMATS,
        answers.get("q14", []),
        "resources_formats",
        "Choisissez les formats que le cabinet peut réellement tenir dans la durée.",
    )

    on_camera = "Non"
    if set(formats).intersection(VIDEO_FORMATS):
        on_camera = st.radio(
            "Une personne apparaîtra-t-elle à l’écran ?",
            ["Oui", "Non"],
            index=["Oui", "Non"].index(answers["q16"]) if answers.get("q16") in {"Oui", "Non"} else None,
            horizontal=True,
            key="resources_on_camera",
            help="Répondez non si les vidéos utilisent seulement une voix off, une capture d’écran ou des visuels.",
        )

    required_skills = sorted(required_skills_for_formats(formats, on_camera == "Oui"))
    competencies: dict[str, str] = {}
    if required_skills:
        st.markdown("**Votre niveau pour les compétences nécessaires**")
        for skill in required_skills:
            saved_level = answers.get("q9", {}).get(skill)
            competencies[skill] = st.radio(
                skill,
                COMPETENCY_LEVELS,
                index=COMPETENCY_LEVELS.index(saved_level) if saved_level in COMPETENCY_LEVELS else None,
                horizontal=True,
                key=f"skill_{skill}",
            )

    has_equipment = st.radio(
        "Disposez-vous d’au moins un matériel pour produire les contenus ?",
        ["Oui", "Non"],
        index=1 if answers.get("q10") == ["Aucun matériel"] else (0 if answers.get("q10") else None),
        horizontal=True,
        key="resources_has_equipment",
    )
    equipment: list[str] = []
    if has_equipment == "Oui":
        equipment = select_many(
            "Quel matériel possédez-vous ?",
            [item for item in EQUIPMENT_OPTIONS if item != "Aucun matériel"],
            answers.get("q10", []),
            "resources_equipment",
        )
    elif has_equipment == "Non":
        equipment = ["Aucun matériel"]

    saved_pilots = answers.get("q11", [])
    if isinstance(saved_pilots, str):
        saved_pilots = [] if saved_pilots == NO_PILOT else [saved_pilots]
    has_pilot = st.radio(
        "Une ou plusieurs personnes sont-elles déjà désignées pour piloter la communication ?",
        ["Oui", "Non"],
        index=1 if answers.get("q11") == NO_PILOT or answers.get("q11") == [NO_PILOT] else (0 if saved_pilots else None),
        horizontal=True,
        key="resources_has_pilot",
    )
    pilots: list[str] = []
    if has_pilot == "Oui":
        pilots = list(st.multiselect(
            "Qui pilotera la communication ?",
            PILOT_OPTIONS,
            default=[item for item in saved_pilots if item in PILOT_OPTIONS],
            placeholder="Choisir une ou plusieurs personnes",
            key="resources_pilots",
        ))
    elif has_pilot == "Non":
        pilots = [NO_PILOT]

    skills_to_strengthen = [skill for skill, level in competencies.items() if level != "Autonome"]
    support: list[str] = []
    support_confirmed: dict[str, str] = {}
    if skills_to_strengthen:
        support = select_many(
            "Comment comptez-vous acquérir ou renforcer ces compétences ?",
            APP_SUPPORT_OPTIONS,
            answers.get("q12", []),
            "resources_support",
        )
        for solution in support:
            saved_confirmation = answers.get("q12_confirmed", {}).get(solution)
            support_confirmed[solution] = st.radio(
                SUPPORT_CONFIRMATION_LABELS[solution],
                ["Oui", "Non"],
                index=["Oui", "Non"].index(saved_confirmation) if saved_confirmation in {"Oui", "Non"} else None,
                horizontal=True,
                key=f"support_confirmation_{solution}",
            )

    has_cost = st.radio(
        "Les solutions ou le matériel prévus entraînent-ils une dépense ?",
        ["Oui", "Non"],
        index=["Oui", "Non"].index(answers["q13_has_cost"]) if answers.get("q13_has_cost") in {"Oui", "Non"} else None,
        horizontal=True,
        key="resources_has_cost",
    )
    budget_validated = None
    if has_cost == "Oui":
        budget_validated = st.radio(
            "Le budget nécessaire est-il validé ?",
            ["Oui", "Non"],
            index=["Oui", "Non"].index(answers["q13_budget_validated"]) if answers.get("q13_budget_validated") in {"Oui", "Non"} else None,
            horizontal=True,
            key="resources_budget_validated",
        )
    elif has_cost == "Non":
        budget_validated = "Sans objet"

    back, forward = render_nav("objective", "Continuer")
    if back:
        navigate("objective")
    if forward:
        errors: list[str] = []
        if not available_time:
            errors.append("Indiquez le temps mensuel disponible.")
        if not formats:
            errors.append("Choisissez au moins un format régulier.")
        if any(level is None for level in competencies.values()):
            errors.append("Indiquez votre niveau pour chaque compétence nécessaire.")
        if on_camera is None:
            errors.append("Indiquez si une personne apparaîtra à l’écran.")
        if has_equipment is None or (has_equipment == "Oui" and not equipment):
            errors.append("Indiquez le matériel disponible.")
        if has_pilot is None or (has_pilot == "Oui" and not pilots):
            errors.append("Indiquez qui pilotera la communication.")
        if any(value is None for value in support_confirmed.values()):
            errors.append("Confirmez si chaque solution choisie est réellement prévue.")
        if has_cost is None:
            errors.append("Indiquez si une dépense est prévue.")
        if has_cost == "Oui" and budget_validated is None:
            errors.append("Indiquez si le budget nécessaire est validé.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            answers.update({
                "q8": available_time,
                "q14": formats,
                "q16": on_camera,
                "q9": competencies,
                "q10": equipment,
                "q11": pilots,
                "q12": support,
                "q12_confirmed": support_confirmed,
                "q13_has_cost": has_cost,
                "q13_budget_validated": budget_validated,
                "q15": None,
            })
            st.session_state.return_to_review = False
            navigate("review")


def review_page() -> None:
    answers = st.session_state.answers
    logo()
    st.markdown('<div class="cap-eyebrow">Vérification</div>', unsafe_allow_html=True)
    st.header("Récapitulatif")
    st.markdown('<div class="cap-question">Relisez vos réponses avant de lancer l’analyse.</div>', unsafe_allow_html=True)

    persona = (answers.get("q2") or ["Non renseigné"])[0]
    if persona == "Autre":
        persona = answers.get("custom_profile") or persona
    review_card("Votre cible", [
        ("Persona :", persona),
        ("Besoin prioritaire :", answers.get("priority_need", "Non renseigné")),
        ("Réseaux connus :", join_values(answers.get("q4", []))),
        ("Réseau le plus souvent utilisé :", answers.get("q4_priority") or "Non renseigné"),
        ("Sources :", join_values(answers.get("q5", [])) if answers.get("q5") else "Base de référence CAP"),
        ("Informations récentes et fiables :", answers.get("q5_quality") or "Sans objet"),
    ])
    if st.button("Modifier la cible", type="secondary", key="edit_target"):
        st.session_state.return_to_review = True
        navigate("target")

    objective_label = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6")
    review_card("Votre objectif", [
        ("Objectif :", objective_label or "Non renseigné"),
        ("Indicateur :", answers.get("indicator", "Non renseigné")),
        ("Résultat attendu :", answers.get("target", "Non renseigné")),
        ("Échéance :", answers.get("deadline", "Non renseigné")),
    ])
    if st.button("Modifier l’objectif", type="secondary", key="edit_objective"):
        st.session_state.return_to_review = True
        navigate("objective")

    skill_summary = " · ".join(f"{skill} : {level}" for skill, level in answers.get("q9", {}).items())
    support_summary = " · ".join(
        f"{solution} : {'prévu' if answers.get('q12_confirmed', {}).get(solution) == 'Oui' else 'non confirmé'}"
        for solution in answers.get("q12", [])
    )
    budget = "Aucune dépense prévue" if answers.get("q13_has_cost") == "Non" else (
        "Budget validé" if answers.get("q13_budget_validated") == "Oui" else "Budget non validé"
    )
    review_card("Vos moyens", [
        ("Temps :", answers.get("q8", "Non renseigné")),
        ("Formats :", join_values(answers.get("q14", []))),
        ("Présence à l’écran :", answers.get("q16", "Sans objet")),
        ("Compétences :", skill_summary or "Non renseigné"),
        ("Matériel :", join_values(answers.get("q10", []))),
        ("Responsable(s) :", join_values(answers.get("q11", [])) if isinstance(answers.get("q11"), list) else answers.get("q11", "Non renseigné")),
        ("Solutions :", support_summary or "Sans objet"),
        ("Budget :", budget),
    ])
    if st.button("Modifier les moyens", type="secondary", key="edit_resources"):
        st.session_state.return_to_review = True
        navigate("resources")

    st.markdown('<div class="cap-nav-spacer"></div>', unsafe_allow_html=True)
    left, middle, right = st.columns([1, 1.4, 1])
    with middle:
        if st.button("Valider et obtenir le résultat", type="primary", width="stretch"):
            with st.spinner("Analyse en cours…"):
                st.session_state.result = evaluate(answers)
            navigate("result")


def result_page() -> None:
    result = st.session_state.result
    answers = st.session_state.answers
    if not result:
        navigate("home")
        return

    logo()
    st.markdown('<div class="cap-eyebrow cap-center">Résultat du diagnostic</div>', unsafe_allow_html=True)
    recommended = result.get("recommended_platforms", [])
    retained = result.get("retained_platform")
    winner = result.get("winner")

    if result["strategic_status"] != "Choix validé":
        title = "Projet à revoir"
        text = "Aucune plateforme ne peut être recommandée. Corrigez les informations indiquées dans la synthèse, puis relancez le diagnostic."
    elif len(recommended) > 1 and not retained:
        title = "Plateformes recommandées"
        text = f"CAP recommande {', '.join(recommended)} au même niveau. Choisissez celle que le cabinet retiendra pour le lancement."
    elif len(recommended) > 1 and retained:
        title = result["feasibility_label"]
        text = f"CAP recommande {', '.join(recommended)} au même niveau. Le cabinet retient {retained} pour le lancement."
    else:
        platform = winner or retained or (recommended[0] if recommended else "")
        title = result["feasibility_label"]
        if result["feasibility_label"] == "Projet prêt":
            text = f"{platform} est la plateforme recommandée. Les moyens déclarés permettent de commencer."
        else:
            text = f"{platform} est la plateforme recommandée. Réalisez les actions indiquées dans la synthèse avant de commencer."

    st.markdown(
        f'<div class="cap-result-box"><div class="cap-result-title">{escape(title)}</div><div class="cap-result-text">{escape(text)}</div></div>',
        unsafe_allow_html=True,
    )

    if len(recommended) > 1 and not retained:
        st.markdown("**Quelle plateforme le cabinet retient-il pour le lancement ?**")
        columns = st.columns(len(recommended))
        for index, platform in enumerate(recommended):
            with columns[index]:
                if st.button(platform, type="primary", width="stretch", key=f"retain_{platform}"):
                    answers["q15"] = platform
                    st.session_state.result = evaluate(answers)
                    st.rerun()

    pdf_bytes = build_summary_pdf(answers, result)
    st.write("")
    chosen_platform = retained or winner or (recommended[0] if len(recommended) == 1 else None)
    if chosen_platform:
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
            guide_path = BASE_DIR / "guides" / f"{chosen_platform.lower()}.pdf"
            if guide_path.exists():
                st.download_button(
                    "Télécharger le guide de la plateforme",
                    data=guide_path.read_bytes(),
                    file_name=guide_path.name,
                    mime="application/pdf",
                    width="stretch",
                )
            else:
                st.button("Guide de la plateforme non intégré", disabled=True, width="stretch")
    else:
        left, middle, right = st.columns([1, 2, 1])
        with middle:
            st.download_button(
                "Télécharger ma synthèse",
                data=pdf_bytes,
                file_name="synthese_CAP.pdf",
                mime="application/pdf",
                type="primary",
                width="stretch",
            )

    st.markdown('<div class="cap-nav-spacer"></div>', unsafe_allow_html=True)
    left, middle, right = st.columns([1, 1.2, 1])
    with middle:
        if st.button("Recommencer", type="secondary", width="stretch"):
            reset_diagnostic()
    st.markdown('<p class="cap-note cap-center">Les réponses sont supprimées à la fermeture de la session.</p>', unsafe_allow_html=True)


inject_css()
init_state()

PAGES = {
    "home": home_page,
    "prepare": prepare_page,
    "target": target_page,
    "objective": objective_page,
    "resources": resources_page,
    "review": review_page,
    "result": result_page,
}

PAGES.get(st.session_state.screen, home_page)()
