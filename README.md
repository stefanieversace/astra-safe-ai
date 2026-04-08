# Astra Safe
### AI Safety & Risk Assistant for Women

Astra Safe is an AI-powered situational safety tool designed to help women assess real-world scenarios, identify key risk indicators, and receive structured, practical guidance for safer decision-making.

Built at the intersection of **AI, safety intelligence, and threat-informed risk assessment**, Astra Safe combines natural language analysis with rule-based scoring to turn unstructured situations into clear, actionable safety insights.

---

## Why Astra Safe?

Many personal safety situations are ambiguous.

A woman leaving work late, getting into a rideshare, meeting someone new, or walking through an unfamiliar area may notice signals that feel “off” — but struggle to quickly assess how concerning they are, which factors matter most, and what the safest immediate next step should be.

Astra Safe is designed to support that moment.

It helps users:
- describe a situation in natural language
- detect contextual risk factors
- assign a structured severity level
- receive calm, practical safety recommendations

This is **not** an emergency service and does **not** replace human judgement. It is a decision-support tool designed to improve situational awareness and safety planning.

---

## Core Concept

Astra Safe uses a **hybrid AI + logic approach**:

1. **User describes a real-world situation**
2. **The system extracts risk signals** from the text
3. **A weighted scoring engine assesses severity**
4. **The app returns structured guidance**, including:
   - situation summary
   - risk indicators
   - protective factors
   - risk level
   - recommended actions
   - analyst reasoning

This design makes the project more robust than a generic chatbot and reflects how real-world decision-support systems are often built.

---

## Features

### Situational Risk Analysis
Users can enter a scenario in plain English, such as:

> “I’m leaving work at 10:30pm and walking 15 minutes to the station alone. My phone battery is at 12% and there’s a man lingering near the exit watching people leave.”

The system analyses the scenario and identifies relevant signals such as:
- being alone
- night-time conditions
- low battery
- isolated environment
- suspicious behaviour
- transport inconsistencies
- coercion or pressure
- limited support visibility

---

### Structured Severity Scoring
Astra Safe assigns a clear risk level:
- **Low**
- **Medium**
- **High**
- **Critical**

The classification is based on weighted scenario features rather than vague AI-only output.

Example scoring logic:
- alone at night → increased risk
- suspicious or predatory behaviour → strongly increased risk
- rideshare mismatch → critical indicator
- busy public space / trusted contact / shared location → protective factors

---

### Analyst-Style Output
Instead of returning generic chatbot text, Astra Safe presents results in a more structured format:

- **Situation Summary**
- **Risk Indicators**
- **Protective Factors**
- **Risk Level**
- **Recommended Immediate Actions**
- **Analyst Reasoning**

This gives the product a more credible and operational feel, inspired by principles used in intelligence analysis and structured risk assessment.

---

### Premium UI Design
The interface is designed with an **Apple-style minimalism** fused with a **Palantir-inspired intelligence dashboard aesthetic**:
- glassmorphism panels
- dark luxury visual theme
- high-contrast risk states
- clean operational layout
- modern, recruiter-friendly product presentation

---

### Optional LLM Enhancement
The project can optionally use the OpenAI API to refine summaries and recommendations, while still preserving rule-based logic as the system’s core decision layer.

This ensures the app remains:
- explainable
- structured
- safer than pure free-form generation
- stronger in interviews and portfolio reviews

---

## Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Regex / rule-based NLP**
- **Optional OpenAI API**
- **Custom weighted scoring engine**
- **Custom CSS for premium UI styling**

---

## Project Structure

```bash
astra-safe-ai/
│
├── app.py
├── requirements.txt
├── README.md
└── assets/
    ├── astra_safe_cover.png
    ├── screenshot_dashboard.png
    └── screenshot_analysis.png
