from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from config import (
    APP_SUPPORT_OPTIONS,
    BUDGET_OPTIONS,
    COMPETENCY_LEVELS,
    EQUIPMENT_OPTIONS,
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
            --cap-muted: #6B7280;
            --cap-line: #E6E7E9;
            --cap-soft: #F7F8F8;
            --cap-green: #0D6B62;
        }

        header[data-testid="stHeader"],
        [data-testid="collapsedControl"],
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

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            min-height: 46px;
            border-radius: 10px;
            font-weight: 650;
            transition: none;
        }

        button[kind="primary"],
        .stDownloadButton > button {
            background: var(--cap-black) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--cap-black) !important;
        }

        button[kind="secondary"] {
            background: #FFFFFF !important;
            color: var(--cap-black) !important;
            border: 1px solid #D8DADD !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: var(--cap-black) !important;
        }

        div[data-baseweb="select"] > div,
        div[role="radiogroup"] {
            border-radius: 10px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
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
    st.session_state.answers = {}
    st.session_state.result = None
    navigate("home")


def render_nav(previous: str, continue_label: str = "Continuer") -> tuple[bool, bool]:
    left, spacer, right = st.columns([1.2, 2.2, 1.4])
    with left:
        back = st.form_submit_button(
            "Précédent",
            type="secondary",
            width="stretch",
            key=f"back_from_{previous}",
        )
    with right:
        forward = st.form_submit_button(
            continue_label,
            type="primary",
            width="stretch",
            key=f"forward_from_{previous}",
        )
    return back, forward


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
    left, middle, right = st.columns([1, 1.1, 1])
    with middle:
        if st.button("Continuer", type="primary", width="stretch", key="prepare_continue"):
            navigate("target")
    if st.button("Précédent", type="secondary", key="prepare_back"):
        navigate("home")


def target_page() -> None:
    answers = st.session_state.answers
    step_header(1, "Votre cible", "Les informations connues sur votre clientèle recherchée.")

    with st.form("target_form"):
        q1 = st.radio(
            "Persona finalisé ?",
            ["Oui", "Partiellement", "Non"],
            index=["Oui", "Partiellement", "Non"].index(answers.get("q1", "Oui")),
            horizontal=True,
        )
        q2 = st.multiselect(
            "Qui souhaitez-vous atteindre ?",
            PROFILE_OPTIONS,
            default=answers.get("q2", []),
            max_selections=3,
            placeholder="Trois réponses maximum",
        )
        q3 = st.radio(
            "Besoins recensés ?",
            ["Oui", "Partiellement", "Non"],
            index=["Oui", "Partiellement", "Non"].index(answers.get("q3", "Oui")),
            horizontal=True,
        )
        q4 = st.multiselect(
            "Quels réseaux utilise votre cible ?",
            TARGET_NETWORK_OPTIONS,
            default=answers.get("q4", []),
            placeholder="Plusieurs réponses possibles",
        )
        q5 = st.multiselect(
            "D’où viennent vos informations ?",
            SOURCE_OPTIONS,
            default=answers.get("q5", []),
            placeholder="Plusieurs réponses possibles",
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
            if "Non identifié" in q4 and len(q4) > 1:
                errors.append("« Non identifié » ne peut pas être associé à un réseau.")
            if "Aucune source" in q5 and len(q5) > 1:
                errors.append("« Aucune source » ne peut pas être associée à une autre source.")
            if errors:
                for error in errors:
                    st.error(error)
            else:
                answers.update({"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5})
                navigate("objective")


def objective_page() -> None:
    answers = st.session_state.answers
    step_header(2, "Votre objectif", "Le résultat que la communication doit produire.")

    with st.form("objective_form"):
        q6 = st.selectbox(
            "Quel est votre objectif ?",
            OBJECTIVE_OPTIONS,
            index=OBJECTIVE_OPTIONS.index(answers.get("q6", OBJECTIVE_OPTIONS[0])),
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            indicator = st.text_input(
                "Indicateur",
                value=answers.get("indicator", ""),
                placeholder="Prises de contact",
            )
        with c2:
            target = st.text_input(
                "Résultat attendu",
                value=answers.get("target", ""),
                placeholder="2",
            )
        with c3:
            deadline = st.text_input(
                "Échéance",
                value=answers.get("deadline", ""),
                placeholder="3 mois",
            )

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
                navigate("presence")


def presence_page() -> None:
    answers = st.session_state.answers
    step_header(3, "Votre présence actuelle", "Les comptes professionnels déjà ouverts.")

    with st.form("presence_form"):
        statuses = {}
        columns = st.columns(2)
        for index, platform in enumerate(PLATFORM_NAMES):
            with columns[index % 2]:
                previous = answers.get("q7", {}).get(platform, "Aucun")
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
            navigate("resources")


def resources_page() -> None:
    answers = st.session_state.answers
    step_header(4, "Vos moyens", "Le temps et les ressources réellement mobilisables.")

    with st.form("resources_form"):
        q8 = st.selectbox(
            "Quel temps mensuel pouvez-vous consacrer ?",
            TIME_OPTIONS,
            index=TIME_OPTIONS.index(answers.get("q8", TIME_OPTIONS[0])),
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

        q10 = st.multiselect(
            "Quel matériel possédez-vous ?",
            EQUIPMENT_OPTIONS,
            default=answers.get("q10", []),
            placeholder="Plusieurs réponses possibles",
        )
        q11 = st.selectbox(
            "Qui pilotera la communication ?",
            PILOT_OPTIONS,
            index=PILOT_OPTIONS.index(answers.get("q11", PILOT_OPTIONS[0])),
        )
        q12 = st.multiselect(
            "Comment compléter vos compétences ?",
            APP_SUPPORT_OPTIONS,
            default=answers.get("q12", []),
            placeholder="Plusieurs réponses possibles",
        )
        q13 = st.selectbox(
            "Quel budget pouvez-vous mobiliser ?",
            BUDGET_OPTIONS,
            index=BUDGET_OPTIONS.index(answers.get("q13", BUDGET_OPTIONS[0])),
        )

        back, forward = render_nav("presence", "Voir le résultat")
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
                st.session_state.result = evaluate(answers)
                navigate("result")


def result_chart(scores: dict[str, float], winner: str | None) -> go.Figure:
    ordered = sorted(scores.items(), key=lambda item: item[1])
    platforms = [item[0] for item in ordered]
    values = [item[1] for item in ordered]
    palette = {
        "Facebook": "#A8CDD0",
        "Instagram": "#B5D8C8",
        "TikTok": "#9AB4C8",
        "YouTube": "#C7D7E7",
    }
    colors = ["#0D6B62" if name == winner else palette[name] for name in platforms]

    figure = go.Figure(
        go.Bar(
            x=values,
            y=platforms,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{value:.0f} %" for value in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y} : %{x:.0f} %<extra></extra>",
        )
    )
    figure.update_layout(
        height=310,
        margin=dict(l=5, r=45, t=15, b=15),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(range=[0, 108], visible=False, fixedrange=True),
        yaxis=dict(
            title=None,
            fixedrange=True,
            tickfont=dict(color="#111111", size=13),
        ),
        font=dict(family="Inter, Arial, sans-serif"),
    )
    return figure


def result_page() -> None:
    result = st.session_state.result
    answers = st.session_state.answers
    if not result:
        navigate("home")

    logo()
    st.markdown('<div class="cap-eyebrow">Votre recommandation</div>', unsafe_allow_html=True)

    if result["winner"] is None:
        st.header("Résultat à consolider")
        st.markdown(
            '<div class="cap-lead" style="margin-left:0">Les informations renseignées ne permettent pas de départager les plateformes de manière suffisamment fiable.</div>',
            unsafe_allow_html=True,
        )
    else:
        winner = result["winner"]
        score = result["scores"][winner]
        st.markdown(
            f"""
            <div class="cap-recommendation">
                <div class="cap-platform">{winner}</div>
                <div class="cap-score">Indice de cohérence&nbsp;: {score:.0f}&nbsp;%</div>
            </div>
            <p class="cap-lead" style="margin-left:0">
                {winner} est la plateforme la plus cohérente avec votre cible,
                votre objectif et le temps que vous pouvez consacrer à votre communication.
            </p>
            """,
            unsafe_allow_html=True,
        )

    st.plotly_chart(
        result_chart(result["scores"], result["winner"]),
        width="stretch",
        config={"displayModeBar": False, "staticPlot": True},
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="cap-card">
                <div class="cap-card-label">Fiabilité des informations</div>
                <div class="cap-card-value">{result["reliability_label"]} · {result["reliability"]:.0f} %</div>
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
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result["alerts"]:
        st.subheader("Points à consolider")
        for alert in result["alerts"][:4]:
            st.markdown(f"- {alert}")

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
            navigate("resources")
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
    "result": result_page,
}

PAGES.get(st.session_state.screen, home_page)()
