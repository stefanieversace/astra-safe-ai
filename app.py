import os
import re
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Any

import streamlit as st

# ============================================================
# ASTRA SAFE
# AI Safety & Risk Assistant for Women
# ------------------------------------------------------------
# Recruiter-ready Streamlit app with:
# - premium Apple x Palantir-inspired UI
# - hybrid risk engine (rule-based + optional LLM refinement)
# - scenario analysis
# - analyst-style reasoning panels
# - scenario simulator
# - pattern dashboard
# - downloadable case report
# ============================================================

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Astra Safe",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# APP CONSTANTS
# ============================================================
APP_NAME = "Astra Safe"
APP_TAGLINE = "AI-powered situational safety intelligence"
APP_VERSION = "v1.0"

DEFAULT_SCENARIOS = {
    "Late-night commute": "I’m leaving work at 10:30pm and walking 15 minutes to the station alone. My phone battery is at 12% and there’s a man lingering near the exit watching people leave.",
    "Rideshare mismatch": "I booked a rideshare after dinner. The number plate does not match the app, the driver is asking me to get in anyway, and the street is quiet.",
    "Online meetup changed last minute": "I’m meeting someone I’ve only spoken to online. He changed the location at the last minute to somewhere more private and wants me to come alone.",
    "Daytime low-risk movement": "I’m walking from a café to the tube at 2pm in a busy area with shops open, full phone battery, and I’m sharing my location with a friend.",
    "House party discomfort": "I’m at a house party and one of the guys keeps trying to get me upstairs alone. I know a couple of people here but not well, and my friend I came with has disappeared for a while.",
    "Hotel corridor unease": "I’m staying in a hotel and a stranger followed me off the lift and is lingering near my door. It’s late and I’m by myself.",
}

FEATURE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "alone": {
        "weight": 2,
        "category": "Exposure",
        "patterns": [
            r"\balone\b", r"\bby myself\b", r"\bon my own\b", r"\bsolo\b", r"\bwalking alone\b",
            r"\bby myself tonight\b"
        ],
        "note": "User appears to be alone.",
        "why_it_matters": "Being alone can reduce immediate support and increase vulnerability in rapidly changing situations.",
    },
    "night": {
        "weight": 2,
        "category": "Environment",
        "patterns": [
            r"\bnight\b", r"\blate\b", r"\bdark\b", r"\bevening\b", r"\bafter dark\b",
            r"\bmidnight\b", r"\b10:?\d{0,2}\s?pm\b", r"\b11:?\d{0,2}\s?pm\b", r"\b12:?\d{0,2}\s?am\b"
        ],
        "note": "Reduced visibility / late-hour conditions.",
        "why_it_matters": "Lower visibility, reduced foot traffic, and fewer available services can increase situational risk.",
    },
    "isolated": {
        "weight": 2,
        "category": "Environment",
        "patterns": [
            r"\bquiet\b", r"\bempty\b", r"\bdeserted\b", r"\bisolated\b", r"\bno one around\b",
            r"\blow traffic\b", r"\blow-traffic\b", r"\bprivate\b", r"\balley\b", r"\bback street\b",
            r"\bside street\b", r"\bcar park\b", r"\bparking lot\b"
        ],
        "note": "Low-footfall or isolated environment.",
        "why_it_matters": "Less visibility and fewer witnesses can reduce options for help and increase concern.",
    },
    "low_battery": {
        "weight": 1,
        "category": "Capability",
        "patterns": [
            r"\bbattery\b.*\b(1[0-9]|[0-9])%\b", r"\bphone\b.*\b(1[0-9]|[0-9])%\b", r"\blow battery\b",
            r"\bphone is dying\b", r"\bphone is dead\b", r"\bno battery\b", r"\bphone almost dead\b"
        ],
        "note": "Reduced ability to call, message, or navigate.",
        "why_it_matters": "Low battery can reduce communication, navigation, and emergency contact options.",
    },
    "suspicious_person": {
        "weight": 3,
        "category": "Behavioural signal",
        "patterns": [
            r"\bfollow(ing|ed)?\b", r"\bstaring\b", r"\bwatching\b", r"\blingering\b", r"\bwaiting near\b",
            r"\bunknown person\b", r"\bman near\b", r"\bkeeps approaching\b", r"\bmade me uncomfortable\b",
            r"\bfeels off\b", r"\bcreepy\b", r"\bwouldn't leave me alone\b", r"\bhovering\b"
        ],
        "note": "Presence of suspicious or concerning behaviour.",
        "why_it_matters": "Observed behaviour can indicate elevated concern, especially when combined with isolation or vulnerability factors.",
    },
    "transport_mismatch": {
        "weight": 4,
        "category": "Transport",
        "patterns": [
            r"\bnumber plate does not match\b", r"\bcar does not match\b", r"\bwrong plate\b",
            r"\bwrong driver\b", r"\bget in anyway\b", r"\brideshare\b.*\bdoes not match\b",
            r"\bdriver doesn.t match\b", r"\bdriver does not match\b"
        ],
        "note": "Transport identity inconsistency.",
        "why_it_matters": "A mismatch between the booked ride and the arriving vehicle/driver is a major safety indicator.",
    },
    "coercion_or_pressure": {
        "weight": 3,
        "category": "Social pressure",
        "patterns": [
            r"\bpressuring me\b", r"\bwon't take no\b", r"\binsisting\b", r"\basking me to come alone\b",
            r"\btrying to isolate me\b", r"\bchanged the location\b", r"\bmore private\b", r"\bcome upstairs\b",
            r"\bkeeps trying to get me alone\b", r"\bwon't leave me alone\b"
        ],
        "note": "Potential coercion, pressure, or isolation attempt.",
        "why_it_matters": "Pressure to isolate or override boundaries can materially increase concern.",
    },
    "intoxication_or_disorientation": {
        "weight": 2,
        "category": "Capability",
        "patterns": [
            r"\bdrunk\b", r"\bintoxicated\b", r"\btipsy\b", r"\bdizzy\b", r"\bdisoriented\b",
            r"\bunwell\b", r"\bpanic\b", r"\bshaky\b", r"\bfaint\b"
        ],
        "note": "Reduced situational capacity.",
        "why_it_matters": "Reduced physical or cognitive capacity can make it harder to assess and respond quickly.",
    },
    "urgent_distress": {
        "weight": 4,
        "category": "Urgency",
        "patterns": [
            r"\bi feel unsafe\b", r"\bi am scared\b", r"\bi'm scared\b", r"\bhelp\b",
            r"\bin immediate danger\b", r"\bafraid\b", r"\bterrified\b", r"\bpanic attack\b"
        ],
        "note": "User expresses elevated distress or danger.",
        "why_it_matters": "Direct expressions of fear or imminent danger should materially raise urgency.",
    },
    "no_support_contact": {
        "weight": 1,
        "category": "Support network",
        "patterns": [
            r"\bno one knows where i am\b", r"\bhaven't told anyone\b", r"\bno one knows\b", r"\bi didn.t tell anyone\b"
        ],
        "note": "No clear support visibility.",
        "why_it_matters": "A lack of shared plans or support visibility can increase isolation risk.",
    },
    "public_busy_area": {
        "weight": -2,
        "category": "Protective factor",
        "patterns": [
            r"\bbusy area\b", r"\bcrowded\b", r"\bshops open\b", r"\bpublic place\b", r"\bwell-lit\b",
            r"\bsecurity staff\b", r"\bdaytime\b", r"\bstaffed area\b"
        ],
        "note": "Protective factor: visible public environment.",
        "why_it_matters": "Visible, public, or staffed environments can lower exposure and improve access to help.",
    },
    "trusted_contact": {
        "weight": -1,
        "category": "Protective factor",
        "patterns": [
            r"\bsharing my location\b", r"\bfriend knows where i am\b", r"\bcalled a friend\b", r"\bwith my sister\b",
            r"\bwith friends\b", r"\btrusted person\b", r"\bsomeone is tracking me\b", r"\blive location\b"
        ],
        "note": "Protective factor: active support network.",
        "why_it_matters": "Shared plans and active contacts can reduce isolation and speed up support if needed.",
    },
    "escape_option": {
        "weight": -1,
        "category": "Protective factor",
        "patterns": [
            r"\bi can go back inside\b", r"\bnear a hotel\b", r"\bthere.s a shop open\b", r"\bsecurity desk\b"
        ],
        "note": "Protective factor: accessible safe or staffed fallback option.",
        "why_it_matters": "Immediate fallback options can reduce urgency and improve next-step choices.",
    },
}

RISK_GUIDANCE = {
    "Low": [
        "Stay aware of your surroundings and keep your route visible and public.",
        "Keep your phone accessible and let someone know if your plans change.",
        "If the situation starts to feel different, reassess before continuing."
    ],
    "Medium": [
        "Move toward a busier, well-lit, or staffed area if possible.",
        "Share your live location or message a trusted person with your plan.",
        "Avoid any option that feels inconsistent, pressured, or private."
    ],
    "High": [
        "Pause the current plan if you can safely do so and prioritise a staffed or visible place.",
        "Call or message a trusted person now and consider arranging alternative transport.",
        "Keep exit options open and do not move into a private or isolated setting."
    ],
    "Critical": [
        "Treat this as urgent and prioritise immediate safety in a public or staffed location.",
        "Contact local emergency services, venue staff, transport staff, or security if you believe you are in danger.",
        "Do not enter the vehicle, property, room, or isolated space if the situation feels unsafe."
    ],
}

RISK_BANDS = [
    ("Low", 0, 2),
    ("Medium", 3, 5),
    ("High", 6, 8),
    ("Critical", 9, 999),
]

# ============================================================
# STYLE
# ============================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #071018;
            --bg-2: #0a1019;
            --panel: rgba(16, 22, 34, 0.76);
            --panel-2: rgba(20, 27, 41, 0.9);
            --line: rgba(255, 255, 255, 0.08);
            --text: #f4f7fb;
            --muted: #aab6ca;
            --accent: #8fb7ff;
            --accent-2: #9ef2d7;
            --danger: #ff8c8c;
            --warn: #ffd48d;
            --ok: #97f0ae;
            --shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 10% 10%, rgba(85, 150, 255, 0.16), transparent 24%),
                radial-gradient(circle at 88% 12%, rgba(100, 255, 210, 0.12), transparent 18%),
                linear-gradient(180deg, #060b12 0%, #0b111a 100%);
            color: var(--text);
        }

        header, footer, #MainMenu {visibility: hidden;}
        [data-testid="stHeader"] {background: transparent;}

        .block-container {
            max-width: 1420px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8,12,19,0.98), rgba(12,17,26,0.98));
            border-right: 1px solid var(--line);
        }

        .glass {
            border: 1px solid var(--line);
            border-radius: 26px;
            padding: 1.2rem 1.2rem 1rem 1.2rem;
            background: var(--panel);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 30px;
            padding: 1.5rem 1.6rem 1.25rem 1.6rem;
            background: linear-gradient(180deg, rgba(16, 22, 34, 0.92), rgba(11, 16, 24, 0.86));
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .hero:before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 8% 12%, rgba(143, 183, 255, 0.18), transparent 22%),
                radial-gradient(circle at 90% 16%, rgba(158, 242, 215, 0.12), transparent 18%);
            pointer-events: none;
        }

        .eyebrow {
            display: inline-block;
            margin-bottom: 0.6rem;
            color: var(--accent-2);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .hero-title {
            font-size: 3rem;
            line-height: 1.02;
            letter-spacing: -0.03em;
            font-weight: 850;
            margin: 0;
            color: var(--text);
        }

        .hero-sub {
            max-width: 950px;
            margin-top: 0.85rem;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-top: 1rem;
        }

        .kpi-card {
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.025);
            border-radius: 20px;
            padding: 1rem;
            min-height: 104px;
        }

        .kpi-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.76rem;
            margin-bottom: 0.45rem;
        }

        .kpi-value {
            color: var(--text);
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.15;
        }

        .kpi-note {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 0.4rem;
        }

        .section-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 0.92rem;
            margin-bottom: 1rem;
        }

        .risk-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border-radius: 999px;
            padding: 0.55rem 0.92rem;
            font-weight: 700;
            font-size: 0.92rem;
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.8rem;
        }

        .risk-low {background: rgba(151, 240, 174, 0.12); color: var(--ok);}
        .risk-medium {background: rgba(143, 183, 255, 0.14); color: var(--accent);}
        .risk-high {background: rgba(255, 212, 141, 0.12); color: var(--warn);}
        .risk-critical {background: rgba(255, 140, 140, 0.12); color: var(--danger);}

        .list-card {
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem;
            background: rgba(255,255,255,0.02);
            height: 100%;
        }

        .list-card ul {
            margin: 0.1rem 0 0 1rem;
            padding-left: 0.55rem;
        }

        .list-card li {
            color: var(--text);
            line-height: 1.58;
            margin-bottom: 0.55rem;
        }

        .small-muted {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.65;
        }

        .mini-label {
            display: inline-block;
            color: var(--muted);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }

        .callout {
            border-left: 3px solid rgba(143, 183, 255, 0.55);
            padding: 0.85rem 0.95rem;
            background: rgba(255,255,255,0.025);
            border-radius: 12px;
            color: var(--muted);
            line-height: 1.65;
            margin-top: 0.75rem;
        }

        .mono {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }

        .divider {
            height: 1px;
            background: var(--line);
            margin: 0.95rem 0 0.9rem 0;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stTextArea textarea,
        .stTextInput input {
            background: rgba(255,255,255,0.03) !important;
            color: var(--text) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
        }

        .stTextArea textarea {
            min-height: 180px;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 999px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: var(--shadow) !important;
        }

        .stButton > button {
            background: linear-gradient(180deg, rgba(143,183,255,0.20), rgba(143,183,255,0.08)) !important;
        }

        .stDownloadButton > button {
            background: linear-gradient(180deg, rgba(158,242,215,0.18), rgba(158,242,215,0.07)) !important;
        }

        @media (max-width: 980px) {
            .hero-title {font-size: 2.3rem;}
            .kpi-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
        }

        @media (max-width: 640px) {
            .kpi-grid {grid-template-columns: 1fr;}
            .hero-title {font-size: 1.95rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SESSION STATE
# ============================================================
def init_state() -> None:
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "scenario_history" not in st.session_state:
        st.session_state.scenario_history = []
    if "selected_preset" not in st.session_state:
        st.session_state.selected_preset = "Late-night commute"

# ============================================================
# HELPERS
# ============================================================
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def get_current_timestamp() -> str:
    return datetime.now().strftime("%d %b %Y, %H:%M")


def score_to_label(score: int) -> str:
    for label, lower, upper in RISK_BANDS:
        if lower <= score <= upper:
            return label
    return "Medium"


def risk_css_class(label: str) -> str:
    return {
        "Low": "risk-low",
        "Medium": "risk-medium",
        "High": "risk-high",
        "Critical": "risk-critical",
    }.get(label, "risk-medium")


def extract_context(text: str, time_of_day: str, alone_status: str, location_type: str) -> Dict[str, str]:
    norm = normalize_text(text)

    if time_of_day != "Auto-detect":
        derived_time = time_of_day
    elif any(token in norm for token in ["night", "late", "pm", "midnight", "dark", "evening"]):
        derived_time = "Night / late"
    elif any(token in norm for token in ["morning", "am", "daytime", "afternoon"]):
        derived_time = "Daytime"
    else:
        derived_time = "Unclear"

    if alone_status != "Auto-detect":
        derived_alone = alone_status
    elif any(token in norm for token in ["alone", "by myself", "solo", "on my own"]):
        derived_alone = "Yes"
    elif any(token in norm for token in ["with friends", "with my sister", "with my friend", "with colleagues"]):
        derived_alone = "No"
    else:
        derived_alone = "Unclear"

    if location_type != "Auto-detect":
        derived_location = location_type
    elif any(token in norm for token in ["station", "platform", "tube", "train", "bus", "tram", "rideshare", "uber", "taxi"]):
        derived_location = "Transport"
    elif any(token in norm for token in ["bar", "club", "hotel", "restaurant", "cafe", "venue"]):
        derived_location = "Venue / hospitality"
    elif any(token in norm for token in ["home", "flat", "apartment", "house", "hallway", "corridor"]):
        derived_location = "Residential"
    elif any(token in norm for token in ["street", "road", "alley", "car park", "parking lot"]):
        derived_location = "Street / outdoor"
    else:
        derived_location = "Unclear"

    return {
        "time_context": derived_time,
        "alone_context": derived_alone,
        "environment": derived_location,
    }


def detect_features(text: str) -> List[Dict[str, Any]]:
    norm = normalize_text(text)
    hits: List[Dict[str, Any]] = []

    for feature_name, config in FEATURE_LIBRARY.items():
        for pattern in config["patterns"]:
            if re.search(pattern, norm):
                hits.append(
                    {
                        "feature": feature_name,
                        "weight": config["weight"],
                        "category": config["category"],
                        "note": config["note"],
                        "why_it_matters": config["why_it_matters"],
                    }
                )
                break

    return hits


def apply_explicit_input_adjustments(features: List[Dict[str, Any]], time_of_day: str, alone_status: str, location_type: str) -> List[Dict[str, Any]]:
    existing_features = {item["feature"] for item in features}

    if time_of_day == "Night / late" and "night" not in existing_features:
        features.append(
            {
                "feature": "night_manual",
                "weight": 2,
                "category": "Environment",
                "note": "User explicitly selected night / late conditions.",
                "why_it_matters": "Late-hour conditions can materially increase exposure in uncertain situations.",
            }
        )

    if alone_status == "Yes" and "alone" not in existing_features:
        features.append(
            {
                "feature": "alone_manual",
                "weight": 2,
                "category": "Exposure",
                "note": "User explicitly selected that they are alone.",
                "why_it_matters": "Being alone may reduce immediate support and increase vulnerability.",
            }
        )

    if location_type == "Street / outdoor":
        features.append(
            {
                "feature": "street_context_manual",
                "weight": 1,
                "category": "Environment",
                "note": "Street / outdoor environment selected.",
                "why_it_matters": "Open outdoor environments can vary significantly and may require closer situational attention.",
            }
        )
    elif location_type == "Transport":
        features.append(
            {
                "feature": "transport_context_manual",
                "weight": 1,
                "category": "Transport",
                "note": "Transport context selected.",
                "why_it_matters": "Transport transitions can introduce timing, visibility, and identity-verification risks.",
            }
        )

    return features


def build_risk_breakdown(features: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
    score = 0
    breakdown = []

    for item in features:
        score += item["weight"]
        breakdown.append(
            {
                "signal": item["note"],
                "category": item["category"],
                "impact": item["weight"],
                "explanation": item["why_it_matters"],
            }
        )

    score = max(score, 0)
    return score, breakdown


def build_confidence(features: List[Dict[str, Any]], text: str) -> int:
    positive_count = len([x for x in features if x["weight"] > 0])
    char_count = len(text.strip())

    confidence = 52
    confidence += min(positive_count * 7, 28)
    confidence += 8 if char_count > 120 else 0
    confidence += 5 if char_count > 220 else 0
    return min(confidence, 96)


def build_summary(text: str, context: Dict[str, str], score: int, label: str, features: List[Dict[str, Any]]) -> Dict[str, Any]:
    positive_notes = [f["note"] for f in features if f["weight"] > 0]
    protective_notes = [f["note"] for f in features if f["weight"] < 0]

    if positive_notes:
        opening = ", ".join(note.lower() for note in positive_notes[:3])
        situation_summary = (
            f"The scenario presents a {label.lower()} level of concern based on the described circumstances, "
            f"with notable indicators including {opening}."
        )
    else:
        situation_summary = (
            f"The scenario currently appears {label.lower()} concern based on the information provided, "
            f"with limited strong risk indicators clearly detected in the text."
        )

    analyst_reasoning = (
        f"Astra Safe classified this scenario as {label.upper()} because the weighted risk score reached {score}. "
        f"Time context: {context['time_context']}. Alone status: {context['alone_context']}. "
        f"Environment: {context['environment']}."
    )

    if protective_notes:
        analyst_reasoning += " Protective factors detected: " + "; ".join(protective_notes)

    if label in ["High", "Critical"]:
        escalation_view = (
            "The scenario contains multiple compounding indicators. The best next step is to reduce exposure, "
            "increase visibility, and keep access to support or staffed environments open."
        )
    elif label == "Medium":
        escalation_view = (
            "The situation is not necessarily immediately dangerous, but enough uncertainty is present to justify "
            "a cautious adjustment to the current plan."
        )
    else:
        escalation_view = (
            "The current signal set appears limited, but maintaining awareness remains sensible in case conditions change."
        )

    return {
        "situation_summary": situation_summary,
        "risk_indicators": positive_notes if positive_notes else ["No strong high-risk indicators were clearly detected from the scenario text alone."],
        "protective_factors": protective_notes if protective_notes else ["No explicit protective factors were clearly stated."],
        "recommended_actions": RISK_GUIDANCE[label],
        "analyst_reasoning": analyst_reasoning,
        "escalation_view": escalation_view,
    }


def try_llm_refinement(base_output: Dict[str, Any], scenario_text: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return base_output

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)

        prompt = f"""
You are refining the output of a personal safety decision-support app called Astra Safe.

Rules:
- Do not guarantee safety.
- Do not act like emergency services.
- Keep the tone calm, practical, structured, and non-sensational.
- Preserve the existing risk label and overall logic.
- Return valid JSON with these keys only:
  situation_summary, recommended_actions, analyst_reasoning, escalation_view
- recommended_actions must be a list of 3 concise items.

Scenario:
{scenario_text}

Base structured output:
{json.dumps(base_output, ensure_ascii=False)}
"""

        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        text = getattr(resp, "output_text", "").strip()
        if not text:
            return base_output

        parsed = json.loads(text)
        for key in ["situation_summary", "recommended_actions", "analyst_reasoning", "escalation_view"]:
            if key in parsed:
                base_output[key] = parsed[key]
        return base_output
    except Exception:
        return base_output


def generate_mock_timeline(label: str, score: int) -> pd.DataFrame:
    base = [
        ("T-15 min", "Initial context received", "Scenario captured from user input"),
        ("T-12 min", "Context extraction", "Time, environment, support visibility, and exposure assessed"),
        ("T-08 min", "Behavioural signal review", "Potential pressure, mismatch, or suspicious activity evaluated"),
        ("T-04 min", "Risk scoring", f"Weighted risk score reached {score}"),
        ("T+00", "Assessment issued", f"Scenario classified as {label}"),
    ]
    return pd.DataFrame(base, columns=["Time", "Stage", "Detail"])


def build_case_report(result: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"# {APP_NAME} Case Report")
    lines.append("")
    lines.append(f"Generated: {result['timestamp']}")
    lines.append(f"Risk Level: {result['risk_label']}")
    lines.append(f"Risk Score: {result['risk_score']}")
    lines.append(f"Confidence: {result['confidence']}%")
    lines.append("")
    lines.append("## Scenario")
    lines.append(result["scenario_text"])
    lines.append("")
    lines.append("## Situation Summary")
    lines.append(result["summary"]["situation_summary"])
    lines.append("")
    lines.append("## Risk Indicators")
    for item in result["summary"]["risk_indicators"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Protective Factors")
    for item in result["summary"]["protective_factors"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Recommended Actions")
    for item in result["summary"]["recommended_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Analyst Reasoning")
    lines.append(result["summary"]["analyst_reasoning"])
    lines.append("")
    lines.append("## Escalation View")
    lines.append(result["summary"]["escalation_view"])
    lines.append("")
    lines.append("## Risk Breakdown")
    for item in result["breakdown"]:
        sign = "+" if item["impact"] >= 0 else ""
        lines.append(f"- [{item['category']}] {item['signal']} ({sign}{item['impact']})")
        lines.append(f"  - Why it matters: {item['explanation']}")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("Astra Safe is a decision-support prototype and does not replace emergency services or professional safety support. If the user believes they are in immediate danger, they should contact local emergency services, venue staff, or transport/security personnel immediately.")
    return "\n".join(lines)


def analyse_scenario(
    scenario_text: str,
    time_of_day: str,
    alone_status: str,
    location_type: str,
    llm_refine: bool,
) -> Dict[str, Any]:
    context = extract_context(scenario_text, time_of_day, alone_status, location_type)
    features = detect_features(scenario_text)
    features = apply_explicit_input_adjustments(features, time_of_day, alone_status, location_type)
    score, breakdown = build_risk_breakdown(features)
    label = score_to_label(score)
    confidence = build_confidence(features, scenario_text)
    summary = build_summary(scenario_text, context, score, label, features)

    if llm_refine:
        summary = try_llm_refinement(summary, scenario_text)

    timeline = generate_mock_timeline(label, score)

    result = {
        "timestamp": get_current_timestamp(),
        "scenario_text": scenario_text,
        "context": context,
        "features": features,
        "breakdown": breakdown,
        "risk_score": score,
        "risk_label": label,
        "confidence": confidence,
        "summary": summary,
        "timeline": timeline,
    }
    return result

# ============================================================
# UI COMPONENTS
# ============================================================
def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">AI Safety Intelligence · {APP_VERSION}</div>
            <div class="hero-title">{APP_NAME}</div>
            <div class="hero-sub">
                {APP_TAGLINE}. Astra Safe is a recruiter-ready decision-support prototype that analyses written scenarios,
                detects key risk signals, applies structured scoring logic, and returns calm, actionable guidance.
                It is designed to demonstrate applied AI, product thinking, human-centred safety design, and intelligence-style reasoning.
            </div>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Analysis Model</div>
                    <div class="kpi-value">Hybrid</div>
                    <div class="kpi-note">Rule-based scoring + optional LLM refinement</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Output Style</div>
                    <div class="kpi-value">Analyst-grade</div>
                    <div class="kpi-note">Structured reasoning over vague chatbot output</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Risk Bands</div>
                    <div class="kpi-value">4-tier</div>
                    <div class="kpi-note">Low, Medium, High, Critical</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Design Language</div>
                    <div class="kpi-value">Apple × Palantir</div>
                    <div class="kpi-note">Dark luxury UI with intelligence dashboard cues</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Tuple[str, str, str, bool, str]:
    with st.sidebar:
        st.markdown("## Control Panel")
        st.caption("Configure the scenario context and analysis behaviour.")

        selected_preset = st.selectbox(
            "Load a scenario preset",
            options=list(DEFAULT_SCENARIOS.keys()),
            index=list(DEFAULT_SCENARIOS.keys()).index(st.session_state.selected_preset),
        )
        st.session_state.selected_preset = selected_preset

        time_of_day = st.selectbox(
            "Time context",
            ["Auto-detect", "Daytime", "Night / late"],
            index=0,
        )
        alone_status = st.selectbox(
            "Are you alone?",
            ["Auto-detect", "Yes", "No"],
            index=0,
        )
        location_type = st.selectbox(
            "Location type",
            ["Auto-detect", "Street / outdoor", "Transport", "Venue / hospitality", "Residential"],
            index=0,
        )
        llm_refine = st.toggle("Use optional LLM refinement", value=False)

        st.markdown("---")
        st.markdown("### Product Notes")
        st.caption(
            "Astra Safe is a decision-support prototype. It does not guarantee safety and does not replace emergency services or trained support staff."
        )

    return selected_preset, time_of_day, alone_status, location_type, llm_refine


def render_input_panel(default_text: str) -> str:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scenario Input</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Describe the situation in natural language. The stronger the detail, the better the system can structure the analysis.</div>',
        unsafe_allow_html=True,
    )

    scenario_text = st.text_area(
        "Describe what is happening",
        value=default_text,
        label_visibility="collapsed",
        placeholder="Example: I’m leaving work late, the street is quiet, my phone battery is low, and someone has been lingering near the exit watching me.",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return scenario_text


def render_risk_header(result: Dict[str, Any]) -> None:
    label = result["risk_label"]
    css = risk_css_class(label)
    st.markdown(
        f"""
        <div class="glass">
            <div class="mini-label">Assessment Output</div>
            <div class="risk-pill {css}">● {label} Risk</div>
            <div class="section-title">Primary Assessment</div>
            <div class="small-muted">{result['summary']['situation_summary']}</div>
            <div class="divider"></div>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Risk Score</div>
                    <div class="kpi-value">{result['risk_score']}</div>
                    <div class="kpi-note">Weighted signal total</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Confidence</div>
                    <div class="kpi-value">{result['confidence']}%</div>
                    <div class="kpi-note">Heuristic output confidence</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Environment</div>
                    <div class="kpi-value">{result['context']['environment']}</div>
                    <div class="kpi-note">Derived from scenario + user input</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Timestamp</div>
                    <div class="kpi-value">{result['timestamp']}</div>
                    <div class="kpi-note">Assessment generation time</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_lists(result: Dict[str, Any]) -> None:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="list-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Indicators</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Signals that increased concern in the current scenario.</div>', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{item}</li>" for item in result["summary"]["risk_indicators"]) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="list-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Protective Factors</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Signals that may reduce exposure or improve options.</div>', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{item}</li>" for item in result["summary"]["protective_factors"]) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_actions_and_reasoning(result: Dict[str, Any]) -> None:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="list-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Calm, practical next-step suggestions based on the current signal set.</div>', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{item}</li>" for item in result["summary"]["recommended_actions"]) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="list-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Analyst Reasoning</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">How the system interpreted the scenario and why it landed on the final classification.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-muted">{result["summary"]["analyst_reasoning"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="callout"><strong>Escalation View:</strong> {result["summary"]["escalation_view"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_breakdown(result: Dict[str, Any]) -> None:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Weighted Risk Breakdown</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Each detected signal contributes to the final score. Positive values increase concern, negative values represent protective factors.</div>',
        unsafe_allow_html=True,
    )

    if result["breakdown"]:
        df = pd.DataFrame(result["breakdown"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No explicit signals were detected from the scenario text.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_timeline(result: Dict[str, Any]) -> None:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">SOC-Style Analysis Timeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">A stylised incident workflow showing how the scenario moved from raw input to final assessment.</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(result["timeline"], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_history_panel() -> None:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scenario History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">A running log of analyses completed in the current session.</div>', unsafe_allow_html=True)

    history = st.session_state.scenario_history
    if history:
        rows = []
        for item in history[::-1]:
            rows.append(
                {
                    "Timestamp": item["timestamp"],
                    "Risk": item["risk_label"],
                    "Score": item["risk_score"],
                    "Environment": item["context"]["environment"],
                    "Preview": item["scenario_text"][:88] + ("..." if len(item["scenario_text"]) > 88 else ""),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No scenarios analysed yet in this session.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_pattern_dashboard() -> None:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Pattern Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Aggregate view of themes across the current session history.</div>', unsafe_allow_html=True)

    history = st.session_state.scenario_history
    if not history:
        st.info("Run a few scenarios to populate the pattern dashboard.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    risk_counts = pd.DataFrame([x["risk_label"] for x in history], columns=["Risk"]).value_counts().reset_index(name="Count")
    env_counts = pd.DataFrame([x["context"]["environment"] for x in history], columns=["Environment"]).value_counts().reset_index(name="Count")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Risk Level Distribution**")
        st.dataframe(risk_counts, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**Environment Distribution**")
        st.dataframe(env_counts, use_container_width=True, hide_index=True)

    all_features = []
    for record in history:
        for feature in record["features"]:
            all_features.append(feature["category"])

    if all_features:
        feature_df = pd.DataFrame(all_features, columns=["Category"]).value_counts().reset_index(name="Count")
        st.markdown("**Most Frequent Signal Categories**")
        st.dataframe(feature_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_disclaimer() -> None:
    st.markdown(
        """
        <div class="glass">
            <div class="section-title">Responsible Use</div>
            <div class="small-muted">
                Astra Safe is a decision-support prototype for product demonstration and portfolio use. It does not guarantee safety,
                does not replace emergency services, and should not be treated as a substitute for local safeguarding resources,
                security professionals, transport staff, or venue staff. If someone believes they are in immediate danger, they should
                contact local emergency services or nearby trained personnel immediately.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# MAIN APP
# ============================================================
def main() -> None:
    inject_css()
    init_state()
    render_hero()

    preset, time_of_day, alone_status, location_type, llm_refine = render_sidebar()
    default_text = DEFAULT_SCENARIOS[preset]
    scenario_text = render_input_panel(default_text)

    cta1, cta2, cta3 = st.columns([1.15, 1, 1])
    with cta1:
        run_analysis = st.button("Run analysis", use_container_width=True)
    with cta2:
        save_to_history = st.button("Save current result", use_container_width=True)
    with cta3:
        clear_history = st.button("Clear session history", use_container_width=True)

    if clear_history:
        st.session_state.scenario_history = []
        st.success("Session history cleared.")

    if run_analysis:
        if not scenario_text.strip():
            st.warning("Please enter a scenario before running the analysis.")
        else:
            result = analyse_scenario(
                scenario_text=scenario_text,
                time_of_day=time_of_day,
                alone_status=alone_status,
                location_type=location_type,
                llm_refine=llm_refine,
            )
            st.session_state.analysis_result = result

    if save_to_history:
        if st.session_state.analysis_result is None:
            st.info("Run an analysis first, then save it to the session history.")
        else:
            st.session_state.scenario_history.append(st.session_state.analysis_result)
            st.success("Current result saved to session history.")

    result = st.session_state.analysis_result

    if result is not None:
        render_risk_header(result)
        render_lists(result)
        render_actions_and_reasoning(result)
        render_breakdown(result)
        render_timeline(result)

        report_text = build_case_report(result)
        st.download_button(
            label="Download case report (.md)",
            data=report_text,
            file_name="astra_safe_case_report.md",
            mime="text/markdown",
            use_container_width=False,
        )

    render_history_panel()
    render_pattern_dashboard()
    render_disclaimer()


if __name__ == "__main__":
    main()
