
from pathlib import Path
import sys
from datetime import date

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.service_matcher import rank_services, identify_missing_information
from src.llm_service import (
    analyze_with_groq,
    format_inr_budget_label,
    GroqConfigurationError,
    sanitize_generated_analysis,
)

BUDGET_OPTIONS = [
    "Not specified",
    "Under ₹2,00,000",
    "₹2,00,000–₹10,00,000",
    "₹10,00,000–₹30,00,000",
    "Above ₹30,00,000",
]


st.set_page_config(
    page_title="Cynbit AI | Blueprint Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --bg:#070d17;
  --bg-2:#0d1525;
  --panel:#101a2b;
  --panel-strong:#121f37;
  --panel-soft:#0d182a;
  --cyan:#39e7ff;
  --cyan-soft:#aaf7ff;
  --purple:#9b8cff;
  --purple-soft:#d3ccff;
  --green:#62f2b0;
  --muted:#a4b5cf;
  --text:#edf5ff;
  --line:rgba(112,176,255,.22);
  --shadow:rgba(19, 29, 46, 0.7);
}
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at top left, rgba(57, 231, 255, 0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(155, 140, 255, 0.12), transparent 30%),
    linear-gradient(180deg, var(--bg) 0%, #09131f 100%);
  color:var(--text);
  font-family:'Inter',sans-serif;
}
[data-testid="stHeader"] {
  background:rgba(8,13,22,0.82);
  backdrop-filter: blur(8px);
  border-bottom:1px solid rgba(68,152,255,0.14);
}
.main .block-container {
  max-width: 1480px;
  padding-top: 1.4rem;
  padding-bottom: 2.5rem;
}
section.main > div {
  padding-top: 0.4rem;
}
h1,h2,h3,h4 {font-family:'Space Grotesk',sans-serif!important;color:var(--text)!important;}
.hero {
  position: relative;
  border:1px solid rgba(57,231,255,.25);
  border-radius: 22px;
  padding: 1.8rem 1.75rem 1.5rem;
  margin: 0.3rem 0 1.2rem;
  background:linear-gradient(120deg, rgba(12,30,48,0.96), rgba(19,21,47,0.95));
  box-shadow:0 18px 45px rgba(7, 12, 21, 0.45);
  overflow: hidden;
}
.hero::before {
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(135deg, rgba(57,231,255,0.12), rgba(155,140,255,0.1), transparent 55%);
  pointer-events:none;
}
.hero > * {position:relative;z-index:1;}
.eyebrow {
  color:var(--cyan-soft);
  font-size:.76rem;
  letter-spacing:2.5px;
  font-weight:800;
  text-transform:uppercase;
  margin-bottom:0.75rem;
}
.hero-title {
  font-family:'Space Grotesk',sans-serif!important;
  font-size: clamp(2rem, 3vw, 3.1rem);
  line-height: 1.05;
  letter-spacing: -0.04em;
  font-weight: 800;
  max-width: 900px;
  color:#f5fbff;
  margin: 0.08rem 0 0.55rem;
}
.hero-title span {color:var(--cyan);}
.hero-sub {
  color:#d0dbeb;
  font-size: 1rem;
  line-height:1.55;
  max-width: 760px;
  margin: 0;
}
.section-label {
  color:var(--cyan);
  font-size:.75rem;
  font-weight:800;
  letter-spacing:1.6px;
  text-transform:uppercase;
  margin: 0.5rem 0 0.85rem;
}
.card {
  background:linear-gradient(145deg, rgba(18,29,48,0.96), rgba(12,18,29,0.96));
  border:1px solid rgba(89,213,255,.2);
  border-radius:16px;
  padding:16px;
  margin-bottom:12px;
  min-height:160px;
  box-shadow:0 10px 24px rgba(0,0,0,.08);
}
.card-rank {color:var(--cyan);font-size:.72rem;font-weight:800;letter-spacing:.7px;}
.card-title {color:#f3f8ff;font-weight:800;font-size:1rem;margin:8px 0;}
.card-score {color:var(--green);font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1.45rem;}
.card-desc {color:#b9c7da;font-size:.84rem;line-height:1.5;margin-top:8px;}
.small-note {color:#8fa2bd;font-size:.78rem;line-height:1.5;}
.dashboard-shell {
  border:1px solid var(--line);
  background: rgba(12,20,32,0.88);
  border-radius: 20px;
  padding: 0.4rem 0.1rem 0.1rem;
}
.dashboard-card {
  background:linear-gradient(180deg, rgba(16,27,40,0.96), rgba(10,18,29,0.94));
  border:1px solid var(--line);
  border-radius:16px;
  padding:1rem 1rem 0.9rem;
  height:100%;
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}
.metric-card {
  background:linear-gradient(180deg, rgba(15,24,38,0.98), rgba(10,16,27,0.96));
  border:1px solid rgba(99,214,255,0.18);
  border-radius:14px;
  padding:0.9rem 1rem;
  height:100%;
}
.blueprint-section-title {
  color: var(--cyan-soft);
  font-size: .73rem;
  letter-spacing: 1.7px;
  text-transform: uppercase;
  font-weight: 800;
  margin: 1.2rem 0 0.65rem;
}
.blueprint-headline {
  font-size: 1.45rem;
  letter-spacing: -0.03em;
  margin: 0 0 0.9rem;
}
.chip {
  display:inline-block;
  padding:0.25rem 0.6rem;
  border-radius:999px;
  background:rgba(57,231,255,0.08);
  border:1px solid rgba(57,231,255,0.16);
  color:var(--cyan-soft);
  font-size:.74rem;
  font-weight:700;
}
.stTextArea textarea,.stTextInput input {
  background:#0d1524!important;color:#f3f8ff!important;
  border:1px solid rgba(105,155,207,.3)!important;border-radius:10px!important;
}
div[data-baseweb="select"]>div {
  background:#0c1322!important;border-color:rgba(105,155,207,.3)!important;
}
div[data-baseweb="select"] * {color:#eef5ff!important;}
.stButton>button,.stFormSubmitButton>button {
  background:linear-gradient(100deg,#39e7ff,#9283ff)!important;
  color:#07101d!important;font-weight:800!important;border:0!important;border-radius:10px!important;
  min-height:42px;
  box-shadow:0 12px 26px rgba(57,231,255,0.15)!important;
}
button[data-baseweb="tab"] {color:#adbed4!important;font-weight:700!important;}
button[data-baseweb="tab"][aria-selected="true"] {color:var(--cyan)!important;}
div[data-testid="stMetric"] {
  background:#111c2e;border:1px solid rgba(89,213,255,.18);padding:12px;border-radius:12px;
}
div[data-testid="stMetricValue"] {color:var(--cyan)!important;}
[data-testid="stDownloadButton"] button {
  background:#111b2c!important;color:var(--cyan)!important;border:1px solid rgba(57,231,255,.35)!important;
  border-radius:9px!important;
}
.footer {border-top:1px solid rgba(89,213,255,.15);padding-top:12px;margin-top:20px;color:#7e91ad;font-size:.74rem;text-align:center;}
</style>
""", unsafe_allow_html=True)


def as_bullets(items):
    if not items:
        return "- To be confirmed during discovery."
    return "\n".join(f"- {item}" for item in items)


def build_blueprint(analysis, matches, timeline, project_details):
    selected_ids = set(analysis.get("selected_service_ids", []))
    selected = [item for item in matches if item["service_id"] in selected_ids] if selected_ids else matches
    if not selected:
        selected = matches

    service_lines = "\n".join(
        f"- **{item['service_name']}** (catalogue similarity: {item['similarity_score']:.2f}/100)"
        for item in selected
    ) or "- No suitable catalogue candidate returned."

    phase_lines = []
    for item in analysis.get("implementation_phases", []):
        phase_lines.append(f"### {item['phase']}\n{as_bullets(item.get('deliverables', []))}")
    if not phase_lines:
        phase_lines = ["### Discovery and validation\n- Confirm scope and deliverables with stakeholders."]

    timeline_text = "Not specified" if timeline is None else f"{timeline} weeks (client-stated target)"
    budget_text = format_inr_budget_label(project_details.get("budget", "Not specified"))
    security_text = project_details.get("data_sensitivity", "Not specified")

    return f"""# Preliminary Project Blueprint

**Generated:** {date.today().isoformat()}  
**Status:** Draft for human review — not a quote, commitment, or approved architecture.

## 1. Requirement summary
{analysis.get('requirement_summary', 'To be confirmed during discovery.')}

## 2. Business goal
{analysis.get('business_goal', 'To be confirmed during discovery.')}

## 3. Target users
{as_bullets(analysis.get('target_users', []))}

## 4. Functional requirements
{as_bullets(analysis.get('functional_requirements', []))}

## 5. Recommended catalogue services
{service_lines}

*Similarity scores measure text overlap. They are not probabilities or guarantees of suitability.*

## 6. Proposed solution approach
{as_bullets(analysis.get('solution_approach', []))}

## 7. Proposed technical architecture
{analysis.get('architecture_overview') or 'High-level architecture to be defined after discovery.'}

### Architecture components
{as_bullets(analysis.get('architecture_components', []))}

## 8. Recommended technology stack
{as_bullets(analysis.get('recommended_technology_stack', []))}

## 9. Preliminary implementation phases
{chr(10).join(phase_lines)}

## 10. Client-stated timeline and budget
- **Timeline:** {timeline_text}. This is an input, not a feasibility estimate or delivery promise.
- **Budget:** {budget_text}. This is a client input, not a validated cost estimate.
- **Data sensitivity:** {security_text}. Security controls require technical and policy review.

## 11. Resource requirements
{as_bullets(analysis.get('resource_requirements', []))}

*Resource requirements are provisional and should be refined during discovery before any staffing commitment.*

## 12. Provisional phase-wise effort estimation
{as_bullets(analysis.get('phase_effort_estimates', []))}

## 13. Expected deliverables
{as_bullets(analysis.get('expected_deliverables', []))}

## 14. Discovery questions
{as_bullets(analysis.get('discovery_questions', []))}

## 15. Proposed success metrics
{as_bullets(analysis.get('success_metrics', []))}

*All targets are preliminary and require client approval.*

## 16. Proposed acceptance criteria
{as_bullets(analysis.get('acceptance_criteria', []))}

## 17. Constraints and dependencies
{as_bullets(analysis.get('constraints_and_dependencies', []))}

## 18. Risks
{as_bullets(analysis.get('risks', []))}

## 19. Assumptions to validate
{as_bullets(analysis.get('assumptions', []))}

## Human review required
Validate scope, service suitability, architecture, data access, security, integrations,
resources, costs, timeline, deliverables, and acceptance criteria before sharing externally.
"""


def render_blueprint_dashboard(analysis, matches, timeline, project_details):
    selected_ids = set(analysis.get("selected_service_ids", []))
    selected = [item for item in matches if item["service_id"] in selected_ids] if selected_ids else matches
    if not selected:
        selected = matches

    timeline_text = "Not specified" if timeline is None else f"{timeline} weeks"
    budget_text = format_inr_budget_label(project_details.get("budget", "Not specified"))
    data_availability = project_details.get("data_availability", "Data availability unknown")
    integration = project_details.get("integration_context", "None specified")
    urgency = project_details.get("urgency", "Normal")
    security_text = project_details.get("data_sensitivity", "Not specified")

    st.markdown('<div class="dashboard-shell">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dashboard-card" style="margin:0.4rem 0 0.9rem;">
          <div class="eyebrow" style="margin-bottom:0.4rem;">Project Blueprint</div>
          <div class="blueprint-headline">{analysis.get('business_goal', 'Project proposal')}</div>
          <div class="chip">Draft for human review</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="blueprint-section-title">A. Project Overview</div>', unsafe_allow_html=True)
    overview_cols = st.columns(2)
    with overview_cols[0]:
        st.markdown(
            f"""
            <div class="dashboard-card">
              <div style="color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;">Project title</div>
              <div style="font-size:1.35rem; font-weight:800; margin-top:0.6rem;">{analysis.get('requirement_summary', 'Discovery opportunity').split('.')[0][:120] or 'Project opportunity'}</div>
              <div style="color:#c2d2ea; margin-top:0.7rem; line-height:1.6;">{analysis.get('requirement_summary', 'Requirement summary to be confirmed during discovery.')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with overview_cols[1]:
        st.markdown(
            f"""
            <div class="dashboard-card">
              <div style="color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;">Business goal</div>
              <div style="font-size:1.05rem; font-weight:700; margin-top:0.6rem;">{analysis.get('business_goal', 'To be confirmed during discovery.')}</div>
              <div style="margin-top:0.9rem; color:#c2d2ea; line-height:1.6;">
                <strong>Target users:</strong> {as_bullets(analysis.get('target_users', []))}<br>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="blueprint-section-title">B. Project Snapshot</div>', unsafe_allow_html=True)
    snapshot = [
        ("Selected services", str(len(selected))),
        ("Budget range", budget_text),
        ("Target timeline", timeline_text),
        ("Data availability", data_availability),
        ("Integration", integration),
        ("Urgency", urgency),
    ]
    cols = st.columns(3)
    for idx, (label, value) in enumerate(snapshot):
        with cols[idx % 3]:
            st.metric(label, value)

    st.markdown('<div class="blueprint-section-title">C. Technical Architecture</div>', unsafe_allow_html=True)
    st.caption("Provisional technology choices and architecture decisions are high-level recommendations only and require discovery validation.")
    arch_cols = st.columns(2)
    with arch_cols[0]:
        st.markdown(
            f"""
            <div class="dashboard-card">
              <div style="font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; color:#aaf7ff; font-weight:800;">Architecture overview</div>
              <div style="margin-top:0.65rem; color:#dfeafc; line-height:1.7;">{analysis.get('architecture_overview', 'High-level architecture to be defined after discovery.')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with arch_cols[1]:
        components = analysis.get("architecture_components", [])
        if not components:
            components = ["Discovery and validation workflow", "Proposed integration layer", "Application layer to be confirmed"]
        st.markdown(
            "<div class='dashboard-card'>"
            + "".join(f"<div style='padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.06);'><strong>{i + 1}.</strong> {component}</div>" for i, component in enumerate(components[:5]))
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="blueprint-section-title">D. Recommended Technology Stack</div>', unsafe_allow_html=True)
    st.caption("Technology choices are provisional and should be validated against the client’s existing standards, integrations, and operating model.")
    stack = analysis.get("recommended_technology_stack", [])
    if stack:
        rows = [
            "| Layer | Recommended technology | Purpose |\n| --- | --- | --- |"
        ]
        for item in stack[:6]:
            parts = [part.strip() for part in item.split(" - ", 2)]
            if len(parts) == 3:
                rows.append(f"| {parts[0]} | {parts[1]} | {parts[2]} |")
            else:
                rows.append(f"| Proposed layer | {item} | To be confirmed through discovery |")
        st.markdown("\n".join(rows))
    else:
        st.info("No technology stack recommendation was produced. The team should validate options after discovery.")

    st.markdown('<div class="blueprint-section-title">E. Implementation Roadmap</div>', unsafe_allow_html=True)
    st.caption("Effort estimates are provisional planning placeholders only and are not delivery commitments.")
    phases = analysis.get("implementation_phases", [])
    if not phases:
        phases = [{"phase": "Discovery and validation", "deliverables": ["Confirm scope and deliverables."]}]
    phase_cols = st.columns(min(len(phases), 3) or 1)
    for i, phase in enumerate(phases[:6]):
        with phase_cols[i % 3]:
            deliverables = phase.get("deliverables", []) or ["To be estimated after discovery."]
            st.markdown(
                f"""
                <div class="dashboard-card">
                  <div style="color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;">{phase.get('phase', f'Phase {i + 1}')}</div>
                  <div style="margin-top:0.55rem; color:#dfeafc; line-height:1.7;">{''.join(f'<div>• {item}</div>' for item in deliverables[:4])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="blueprint-section-title">F. Resources and Deliverables</div>', unsafe_allow_html=True)
    resource_cols = st.columns(2)
    with resource_cols[0]:
        st.markdown(
            "<div class='dashboard-card'><div style='color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;'>Resource requirements</div>"
            + f"<div style='margin-top:0.7rem; color:#dfeafc; line-height:1.7;'>{as_bullets(analysis.get('resource_requirements', []))}</div></div>",
            unsafe_allow_html=True,
        )
    with resource_cols[1]:
        st.markdown(
            "<div class='dashboard-card'><div style='color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;'>Expected deliverables</div>"
            + f"<div style='margin-top:0.7rem; color:#dfeafc; line-height:1.7;'>{as_bullets(analysis.get('expected_deliverables', []))}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="blueprint-section-title">G. Discovery Questions</div>', unsafe_allow_html=True)
    questions = analysis.get("discovery_questions", [])
    for idx, question in enumerate(questions[:8], start=1):
        with st.expander(f"Q{idx:02d}. {question[:110]}{'…' if len(question) > 110 else ''}", expanded=False):
            st.write(question)

    st.markdown('<div class="blueprint-section-title">H. Proposed Success Metrics and Acceptance Criteria</div>', unsafe_allow_html=True)
    st.caption("All targets are preliminary and require client approval.")
    metrics_cols = st.columns(2)
    with metrics_cols[0]:
        st.markdown(
            "<div class='dashboard-card'><div style='color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;'>Success metrics</div>"
            + f"<div style='margin-top:0.7rem; color:#dfeafc; line-height:1.7;'>{as_bullets(analysis.get('success_metrics', []))}</div></div>",
            unsafe_allow_html=True,
        )
    with metrics_cols[1]:
        st.markdown(
            "<div class='dashboard-card'><div style='color:#aaf7ff; font-size:0.72rem; letter-spacing:1.2px; text-transform:uppercase; font-weight:800;'>Acceptance criteria</div>"
            + f"<div style='margin-top:0.7rem; color:#dfeafc; line-height:1.7;'>{as_bullets(analysis.get('acceptance_criteria', []))}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="blueprint-section-title">I. Risks, Assumptions, Constraints</div>', unsafe_allow_html=True)
    risk_cols = st.columns(3)
    risk_items = [
        ("Risks", analysis.get("risks", [])),
        ("Assumptions", analysis.get("assumptions", [])),
        ("Constraints", analysis.get("constraints_and_dependencies", [])),
    ]
    for idx, (label, items) in enumerate(risk_items):
        with risk_cols[idx]:
            with st.expander(label, expanded=False):
                st.markdown(as_bullets(items))

    st.markdown('</div>', unsafe_allow_html=True)


# Header
st.markdown("""
<div class="hero">
  <div class="eyebrow">Cynbit / AI Solution Studio</div>
  <div class="hero-title">Inquiry <span>→</span> Intelligence <span>→</span> Blueprint</div>
  <div class="hero-sub">Groq requirement analysis · TF-IDF service matching · Human-reviewed project brief for enterprise delivery teams.</div>
</div>
""", unsafe_allow_html=True)

st.info(
    "Proof of concept: the catalogue and test inquiries are demo data. "
    "Do not enter confidential client information."
)

try:
    services = pd.read_csv(ROOT / "service_catalog.csv").fillna("")
except Exception as exc:
    st.error(f"Could not load service catalogue: {exc}")
    st.stop()


st.markdown('<div class="section-label">01 / CLIENT INQUIRY</div>', unsafe_allow_html=True)

with st.form("inquiry_form", border=True):
    inquiry = st.text_area(
        "Describe the business problem",
        placeholder="Example: We need an internal AI assistant that answers employee questions using documents and connects to our CRM.",
        height=100,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        budget = st.selectbox(
            "Budget",
            BUDGET_OPTIONS,
        )
    with c2:
        timeline = st.selectbox(
            "Target timeline",
            [None, 2, 4, 6, 8, 12, 16, 24],
            format_func=lambda x: "Not specified" if x is None else f"{x} weeks",
        )
    with c3:
        data_availability = st.selectbox(
            "Data availability",
            ["Data availability unknown", "No data yet", "Sample data available", "Existing production data"],
        )
    with c4:
        integration = st.selectbox(
            "Integration",
            ["None specified", "CRM", "Existing SaaS/API", "Cloud platform", "Database", "Multiple internal systems"],
        )

    c5, c6 = st.columns(2)
    with c5:
        security = st.selectbox(
            "Data sensitivity",
            ["Not specified", "Standard", "Sensitive business data", "Regulated/highly sensitive"],
        )
    with c6:
        urgency = st.selectbox("Urgency", ["Low", "Normal", "High", "Critical"], index=1)

    submitted = st.form_submit_button(
        "⚡ ANALYZE WITH GROQ",
        type="primary",
        use_container_width=True,
    )


if submitted:
    if not inquiry.strip():
        st.warning("Please enter a project inquiry first.")
        st.stop()

    with st.spinner("Matching services and asking Groq to analyze the requirements..."):
        matches = rank_services(inquiry, services, top_k=3)
        basic_questions = identify_missing_information(
            budget, data_availability, integration, security, timeline
        )

        project_details = {
            "budget": budget,
            "target_timeline_weeks": timeline,
            "data_availability": data_availability,
            "integration_context": integration,
            "data_sensitivity": security,
            "urgency": urgency,
        }

        try:
            analysis = sanitize_generated_analysis(analyze_with_groq(inquiry, project_details, matches))
            llm_ok = True
        except GroqConfigurationError as exc:
            analysis = None
            llm_ok = False
            llm_error = str(exc)

    if not llm_ok:
        st.error(
            "Groq analysis could not be completed. No AI-generated analysis "
            "is being presented as if it succeeded."
        )
        st.code(llm_error)
        st.info(
            "Check your API key configuration, selected model, network, and API usage. "
            "Then submit the inquiry again."
        )
        st.stop()

    # Merge rule-based missing fields with Groq's contextual questions.
    questions = basic_questions + analysis.get("discovery_questions", [])
    questions = list(dict.fromkeys(q.strip() for q in questions if q.strip()))
    analysis["discovery_questions"] = questions

    blueprint = build_blueprint(analysis, matches, timeline, project_details)

    st.divider()
    st.success("Groq analysis completed. Review the results before using them.")

    m1, m2, m3 = st.columns(3)
    m1.metric("Services ranked", len(matches))
    m2.metric("Discovery questions", len(questions))
    m3.metric("Timeline input", "Not set" if timeline is None else f"{timeline} weeks")

    if matches and matches[0]["similarity_score"] < 15:
        st.warning(
            "Weak catalogue match: the closest service has low text similarity. "
            "Validate the recommendation with a human reviewer."
        )

    tab_services, tab_analysis, tab_discovery, tab_blueprint = st.tabs([
        "✦ Service matches",
        "✧ AI analysis",
        "⌁ Discovery",
        "▤ Blueprint",
    ])

    with tab_services:
        st.markdown('<div class="section-label">02 / RECOMMENDED SERVICES</div>', unsafe_allow_html=True)
        cols = st.columns(len(matches) or 1)
        for col, item in zip(cols, matches):
            with col:
                st.markdown(f"""
                <div class="card">
                  <div class="card-rank">RANK #{item['rank']} / {item['category']}</div>
                  <div class="card-title">{item['service_name']}</div>
                  <div class="card-score">{item['similarity_score']:.2f}<span style="font-size:.75rem;color:#8fa2bd"> / 100</span></div>
                  <div class="card-desc">{item['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("Catalogue keywords"):
                    st.write(item["matching_keywords"].replace(";", ", "))

        st.caption(
            "Scores are text similarity after curated query expansion, not probability or confidence. "
            "Groq does not change the underlying TF-IDF score."
        )
        st.download_button(
            "↓ Download service matches (.csv)",
            data=pd.DataFrame(matches).to_csv(index=False).encode("utf-8"),
            file_name="service_matches.csv",
            mime="text/csv",
        )

    with tab_analysis:
        st.markdown('<div class="section-label">03 / GROQ REQUIREMENT ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown("### Requirement summary")
        st.write(analysis["requirement_summary"])
        st.markdown("### Business goal")
        st.write(analysis["business_goal"])

        left, right = st.columns(2)
        with left:
            st.markdown("#### Target users")
            st.markdown(as_bullets(analysis["target_users"]))
            st.markdown("#### Functional requirements")
            st.markdown(as_bullets(analysis["functional_requirements"]))
        with right:
            st.markdown("#### Proposed approach")
            st.markdown(as_bullets(analysis["solution_approach"]))
            st.markdown("#### Constraints and dependencies")
            st.markdown(as_bullets(analysis["constraints_and_dependencies"]))

        st.markdown("#### Assumptions to validate")
        st.markdown(as_bullets(analysis["assumptions"]))
        st.markdown("#### Proposed architecture")
        st.write(analysis.get("architecture_overview", "To be confirmed during discovery."))
        st.markdown("#### Recommended technology stack")
        st.markdown(as_bullets(analysis.get("recommended_technology_stack", [])))

    with tab_discovery:
        st.markdown('<div class="section-label">04 / DYNAMIC DISCOVERY CHECKLIST</div>', unsafe_allow_html=True)
        st.caption("Questions combine a transparent checklist with Groq's contextual analysis.")
        for i, question in enumerate(questions, start=1):
            st.markdown(f"**Q{i:02d}.** {question}")

        st.markdown("### Proposed success metrics")
        st.caption("All targets are preliminary and require client approval.")
        st.markdown(as_bullets(analysis["success_metrics"]))
        st.markdown("### Risks to review")
        st.markdown(as_bullets(analysis["risks"]))

    with tab_blueprint:
        st.markdown('<div class="section-label">05 / PRELIMINARY PROJECT BLUEPRINT</div>', unsafe_allow_html=True)
        st.warning("Draft for human review — not a quote, delivery commitment, or approved architecture.")
        render_blueprint_dashboard(analysis, matches, timeline, project_details)
        st.download_button(
            "↓ Download blueprint (.md)",
            data=blueprint,
            file_name="preliminary_project_blueprint.md",
            mime="text/markdown",
            use_container_width=True,
        )

with st.expander("About this proof of concept"):
    st.markdown("""
- **LLM:** Groq analyzes requirements and drafts context-specific discovery questions and project plans.
- **Service retrieval:** TF-IDF and cosine similarity rank the existing catalogue; curated query expansion bridges common client language to catalogue terms.
- **Guardrail:** Groq may select only from the candidate service IDs supplied to it; the output is validated.
- **Grounding:** Unconfirmed quantities, integrations, and delivery details must remain proposed or be captured as assumptions.
- **Human review:** Required before external sharing or implementation.
- **Limitations:** Synthetic evaluation, small catalogue, no CRM integration, and no real-client validation.
""")

st.markdown(
    '<div class="footer">CYNBIT AI BLUEPRINT STUDIO • GROQ-POWERED PROOF OF CONCEPT • HUMAN REVIEW REQUIRED</div>',
    unsafe_allow_html=True,
)
