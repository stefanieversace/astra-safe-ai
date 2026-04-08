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
```
## Example Use Cases

### 1. Late-Night Commute

A user is walking alone after work at night with low phone battery and notices suspicious behaviour nearby.

Astra Safe can:

- Detect multiple compounding risk factors
- Classify the situation as elevated risk
- Recommend pausing, moving to a staffed area, contacting a trusted person, and arranging safer transport

### 2. Rideshare Mismatch

A user’s rideshare number plate or driver identity does not match the app.

Astra Safe can:

- Identify this as a major safety signal
- Classify the scenario as high or critical risk
- Recommend not entering the vehicle and moving to a safer public area

### 3. Online-to-Offline Meetup

A person met online changes the location last minute to somewhere more private and pressures the user to come alone.

Astra Safe can:

- Detect coercive and isolating behaviour
- Identify pattern-based risk
- Recommend declining the change and prioritising public, visible environments

## Why This Project Matters

Astra Safe is intentionally built as more than a portfolio demo.

It explores how AI can be used responsibly in a safety context:

- To support judgement
- To structure uncertainty
- To surface risk indicators clearly
- To encourage practical next-step decision-making

It also reflects a broader principle:

AI is most useful when it helps people think more clearly in high-friction moments.

## Design Philosophy

Astra Safe is designed around five principles:

1. Calm over alarm

The app should never feel chaotic or sensationalist.

2. Structured over vague

Outputs should be clear, reasoned, and explainable.

3. Supportive over authoritative

The system supports user decision-making rather than pretending to guarantee outcomes.

4. Practical over abstract

Recommendations should be immediately usable.

5. Responsible by design

The product includes clear boundaries and avoids overstating certainty.

## Safety Disclaimer

Astra Safe is a decision-support prototype for educational and product demonstration purposes.

It:

- Does not guarantee safety
- Does not replace emergency services
- Does not replace professional security support or local safeguarding resources

If a user believes they are in immediate danger, they should contact local emergency services, venue security, transport staff, or a trusted person immediately.

## Screenshots



## Dashboard

Risk Analysis Output

App Overview

What This Project Demonstrates

## This project showcases:

- Applied AI product thinking
- Structured risk assessment design
- Explainable decision-support systems
- Human-centred safety tooling
- Premium frontend presentation in Streamlit
- Strong portfolio storytelling for AI, security, and intelligence roles

## Recruiter / Hiring Manager Notes

Astra Safe was built to demonstrate how AI can be applied to real-world safety and security problems in a thoughtful, operationally credible way.

It reflects strengths in:

- Python development
- AI-assisted workflow design
- Intelligence-style reasoning
- Risk modelling
- Product framing
- User-centred systems thinking

## Future Enhancements

Planned next steps include:

- Location-aware safety context
- Check-in timer workflow
- Trusted contact alert logic
- Scenario history and trend analysis
- Multilingual support
- Richer explainability layer
- Anonymised pattern insights across scenario types

## Author

Stefanie Versace

If you're interested in AI, security, threat analysis, OSINT, or decision-support tools, feel free to connect.

LinkedIn: www.linkedin.com/in/stefanie-versace-26766428a
GitHub: https://github.com/stefanieversace

## Final Note

Astra Safe is built around a simple idea:

Good technology should help people think more clearly when clarity matters most.
