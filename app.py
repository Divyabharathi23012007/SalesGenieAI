"""
app.py
Streamlit frontend for SalesGenie AI — Modules 1, 2, and 3 fully wired up.
Run with: streamlit run app.py --server.port 8502
(or via run_all.py which starts backend + frontend together)
"""

import os
import requests
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="SalesGenie AI", layout="wide", initial_sidebar_state="expanded")

# --------------------------------------------------------------------------
# DARK THEME STYLING (matches the reference screenshot)
# --------------------------------------------------------------------------
st.markdown("""
<style>
    body, .stApp { background-color: #0e1117; color: #e6e6e6; }
    section[data-testid="stSidebar"] {
        background-color: #12141c;
        border-right: 1px solid #262730;
    }
    .sg-title { font-size: 28px; font-weight: 800; color: #38bdf8; margin-bottom: 0px; }
    .sg-subtitle { font-size: 13px; color: #9ca3af; margin-top: 0px; margin-bottom: 24px; }
    .sg-nav-header {
        font-size: 12px; color: #6b7280; letter-spacing: 1px;
        text-transform: uppercase; margin: 18px 0 6px 0;
    }
    .sg-page-title { font-size: 42px; font-weight: 800; color: #f5f5f5; margin-bottom: 4px; }
    .sg-page-subtitle { font-size: 15px; color: #9ca3af; margin-bottom: 28px; }
    .sg-error-box {
        background-color: #3a1620; border: 1px solid #7f1d3a; color: #fca5a5;
        padding: 16px 20px; border-radius: 8px; font-size: 15px;
    }
    .sg-success-box {
        background-color: #10261c; border: 1px solid #16543a; color: #86efac;
        padding: 14px 18px; border-radius: 8px; font-size: 14px;
    }
    .sg-card {
        background-color: #161923; border: 1px solid #262730; border-radius: 10px;
        padding: 20px; margin-bottom: 16px;
    }
    .sg-badge {
        display: inline-block; background-color: #1e3a5f; color: #7dd3fc;
        font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px;
        letter-spacing: 0.5px;
    }
    .sg-factor { font-weight: 700; color: #f5f5f5; font-size: 14px; margin-bottom: 2px; }
    .sg-factor-detail { color: #9ca3af; font-size: 13px; margin-bottom: 14px; }
    div[data-testid="stRadio"] label { font-size: 15px; padding: 4px 0; }
    .stButton>button {
        background-color: #0ea5e9; color: white; border: none; border-radius: 6px;
        font-weight: 600;
    }
    .stButton>button:hover { background-color: #0284c7; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# API HELPERS
# --------------------------------------------------------------------------
def backend_alive() -> bool:
    try:
        r = requests.get(f"{FASTAPI_URL}/", timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def api_get(path, **kwargs):
    return requests.get(f"{FASTAPI_URL}{path}", timeout=kwargs.pop("timeout", 10), **kwargs)


def api_post(path, **kwargs):
    return requests.post(f"{FASTAPI_URL}{path}", timeout=kwargs.pop("timeout", 30), **kwargs)


def api_put(path, **kwargs):
    return requests.put(f"{FASTAPI_URL}{path}", timeout=kwargs.pop("timeout", 10), **kwargs)


def api_delete(path, **kwargs):
    return requests.delete(f"{FASTAPI_URL}{path}", timeout=kwargs.pop("timeout", 10), **kwargs)


def safe_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {"detail": resp.text.strip() or f"Empty response (HTTP {resp.status_code})"}


def score_gauge(total_score: int):
    """Returns a Plotly gauge indicator for the given total score (0-100)."""
    color = "#10b981" if total_score >= 70 else "#f59e0b" if total_score >= 40 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        number={"suffix": "/100", "font": {"size": 28, "color": "#f5f5f5"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#9ca3af", "tickfont": {"color": "#9ca3af"}},
            "bar": {"color": color},
            "bgcolor": "#1f2937",
            "bordercolor": "#374151",
            "steps": [
                {"range": [0, 40], "color": "#1f2937"},
                {"range": [40, 70], "color": "#1f2937"},
                {"range": [70, 100], "color": "#1f2937"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": total_score},
        },
        title={"text": "Prospect Fit Score", "font": {"size": 16, "color": "#9ca3af"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        margin=dict(t=40, b=10, l=20, r=20),
        height=230,
    )
    return fig


def fetch_leads(q: str = None):
    params = {"q": q} if q else {}
    resp = api_get("/leads", params=params)
    resp.raise_for_status()
    return resp.json()


def lead_label(l: dict) -> str:
    seg = f" · {l['segment']}" if l.get("segment") else ""
    return f"{l['company_name']} — {l.get('contact_name') or 'No contact'}{seg}"


TECH_STACK_OPTIONS = [
    "AWS", "GCP", "Azure", "Python", "Java", "Go", "Node.js", "React",
    "Kubernetes", "Docker", "PostgreSQL", "MongoDB", "Kafka", "TensorFlow", "Terraform",
]
SEGMENTS = ["Enterprise", "Mid-Market", "Startup"]


# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sg-title">SalesGenie AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-subtitle">Lead Management Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-nav-header">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        label="Navigation",
        options=[
            "Dashboard",
            "Lead Management",
            "Add Lead",
            "Lead Intelligence",
            "Lead Scoring",
            "AI Outreach",
            "Sales Interactions",
        ],
        index=1,
        label_visibility="collapsed",
    )

if not backend_alive():
    st.markdown(
        '<div class="sg-error-box">Unable to connect to the FastAPI backend. '
        f'Make sure it is running at <b>{FASTAPI_URL}</b> '
        '(<code>uvicorn main:app --reload --port 8000</code> or run <code>python run_all.py</code>).</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# --------------------------------------------------------------------------
# MODULE 1 — LEAD MANAGEMENT
# --------------------------------------------------------------------------
def render_lead_management():
    st.markdown('<div class="sg-page-title">Lead Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">View, search, edit, and remove prospects.</div>', unsafe_allow_html=True)

    search = st.text_input("Search by company, contact, or industry", placeholder="e.g. TechCorp")

    try:
        leads = fetch_leads(search or None)
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return

    if not leads:
        st.info("No leads found. Add one from the 'Add Lead' page, or run seed_data.py for sample data.")
        return

    st.caption(f"{len(leads)} lead(s) found")
    table_rows = [
        {
            "Company": l["company_name"],
            "Contact": l.get("contact_name") or "—",
            "Industry": l.get("industry") or "—",
            "Segment": l.get("segment") or "—",
            "Stage": l.get("lead_status") or "—",
            "Location": l.get("location") or "—",
        }
        for l in leads
    ]
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Edit or Delete a Lead")

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select a lead", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    try:
        stages_resp = api_get("/leads/stages")
        stages = stages_resp.json()["stages"] if stages_resp.status_code == 200 else \
            ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    except Exception:
        stages = ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

    with st.form(f"edit_lead_{lead['lead_id']}"):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company Name", value=lead["company_name"])
            contact_name = st.text_input("Contact Name", value=lead.get("contact_name") or "")
            title = st.text_input("Title", value=lead.get("title") or "")
            email = st.text_input("Email", value=lead.get("email") or "")
            phone = st.text_input("Phone", value=lead.get("phone") or "")
            industry = st.text_input("Industry", value=lead.get("industry") or "")
        with c2:
            company_size = st.text_input("Company Size", value=lead.get("company_size") or "")
            annual_revenue = st.text_input("Annual Revenue", value=lead.get("annual_revenue") or "")
            location = st.text_input("Location", value=lead.get("location") or "")
            funding_stage = st.text_input("Funding Stage", value=lead.get("funding_stage") or "")
            segment = st.selectbox("Segment", SEGMENTS,
                                    index=SEGMENTS.index(lead["segment"]) if lead.get("segment") in SEGMENTS else 0)
            lead_status = st.selectbox("Lead Stage", stages,
                                        index=stages.index(lead["lead_status"]) if lead.get("lead_status") in stages else 0)

        tech_stack = st.multiselect("Technology Stack", TECH_STACK_OPTIONS, default=lead.get("tech_stack") or [])

        col_save, col_delete = st.columns([1, 1])
        save_clicked = col_save.form_submit_button("💾 Save Changes", type="primary")
        delete_clicked = col_delete.form_submit_button("🗑️ Delete Lead")

    if save_clicked:
        payload = {
            "company_name": company_name, "contact_name": contact_name, "title": title,
            "email": email, "phone": phone, "industry": industry, "company_size": company_size,
            "annual_revenue": annual_revenue, "location": location, "funding_stage": funding_stage,
            "segment": segment, "lead_status": lead_status, "tech_stack": tech_stack,
        }
        resp = api_put(f"/leads/{lead['lead_id']}", json=payload)
        if resp.status_code == 200:
            st.markdown('<div class="sg-success-box">Lead updated successfully.</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error(f"Update failed: {resp.text}")

    if delete_clicked:
        resp = api_delete(f"/leads/{lead['lead_id']}")
        if resp.status_code == 200:
            st.markdown('<div class="sg-success-box">Lead deleted.</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error(f"Delete failed: {resp.text}")

    st.markdown("---")
    st.subheader("Engagement History")
    try:
        hist = api_get(f"/leads/{lead['lead_id']}/interactions").json()
    except Exception:
        hist = []

    if hist:
        for h in hist:
            with st.expander(f"{h['interaction_type']} · {h.get('interaction_date', '')[:10]}"):
                st.write(h.get("summary") or "No summary.")
                if h.get("action_items"):
                    st.caption(f"Action items: {h['action_items']}")
    else:
        st.caption("No interactions logged yet.")

    with st.expander("➕ Log a new interaction"):
        with st.form(f"log_interaction_{lead['lead_id']}"):
            itype = st.selectbox("Type", ["Call", "Email", "Meeting", "Note"])
            summary = st.text_area("Summary")
            action_items = st.text_input("Action items (optional)")
            logged = st.form_submit_button("Log Interaction")
        if logged:
            resp = api_post(f"/leads/{lead['lead_id']}/interactions",
                             json={"interaction_type": itype, "summary": summary, "action_items": action_items})
            if resp.status_code == 200:
                st.success("Interaction logged.")
                st.rerun()
            else:
                st.error(f"Failed: {resp.text}")


# --------------------------------------------------------------------------
# MODULE 1 — ADD LEAD
# --------------------------------------------------------------------------
def render_add_lead():
    st.markdown('<div class="sg-page-title">Add Lead</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Create a new prospect record.</div>', unsafe_allow_html=True)

    with st.form("add_lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company Name *")
            contact_name = st.text_input("Contact Name")
            title = st.text_input("Title")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            industry = st.text_input("Industry")
        with c2:
            company_size = st.text_input("Company Size", placeholder="e.g. 250-500 employees")
            annual_revenue = st.text_input("Annual Revenue", placeholder="e.g. $45M - $60M")
            location = st.text_input("Location")
            funding_stage = st.text_input("Funding Stage", placeholder="e.g. Series C - $28M")
            segment = st.selectbox("Segment", SEGMENTS)
            lead_status = st.selectbox("Initial Stage", ["New", "Contacted", "Qualified"])

        tech_stack = st.multiselect("Technology Stack", TECH_STACK_OPTIONS)

        submitted = st.form_submit_button("➕ Add Lead", type="primary")

    if submitted:
        if not company_name.strip():
            st.error("Company Name is required.")
            return
        payload = {
            "company_name": company_name, "contact_name": contact_name, "title": title,
            "email": email, "phone": phone, "industry": industry, "company_size": company_size,
            "annual_revenue": annual_revenue, "location": location, "funding_stage": funding_stage,
            "segment": segment, "lead_status": lead_status, "tech_stack": tech_stack,
        }
        resp = api_post("/leads", json=payload)
        if resp.status_code == 200:
            st.markdown(f'<div class="sg-success-box">Lead "{company_name}" added successfully.</div>',
                        unsafe_allow_html=True)
        else:
            st.error(f"Failed to add lead: {resp.text}")


# --------------------------------------------------------------------------
# MODULE 2 — LEAD INTELLIGENCE
# --------------------------------------------------------------------------
def score_gauge(score: int):
    color = "#22c55e" if score >= 75 else "#eab308" if score >= 45 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 40, "color": "#f5f5f5"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#6b7280"},
            "bar": {"color": color},
            "bgcolor": "#161923",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 45], "color": "#2a1a1a"},
                {"range": [45, 75], "color": "#2a2410"},
                {"range": [75, 100], "color": "#0f2a1a"},
            ],
        },
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#f5f5f5"},
    )
    return fig


def render_lead_intelligence():
    st.markdown('<div class="sg-page-title">Lead Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">AI-powered company analysis and qualification scoring.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.info("No leads yet. Add one from the 'Add Lead' page first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select a lead to analyze", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    col_profile, col_intel = st.columns([1, 1])

    with col_profile:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        st.markdown(f"### {lead['company_name']}")
        st.caption(f"{lead.get('industry') or 'Unknown industry'} · {lead.get('segment') or 'Unsegmented'}")
        st.write(f"**Company Size:** {lead.get('company_size') or '—'}")
        st.write(f"**Annual Revenue:** {lead.get('annual_revenue') or '—'}")
        st.write(f"**Location:** {lead.get('location') or '—'}")
        st.write(f"**Funding Stage:** {lead.get('funding_stage') or '—'}")
        if lead.get("tech_stack"):
            st.write("**Tech Stack:** " + ", ".join(lead["tech_stack"]))
        st.write(f"**Pipeline Stage:** {lead.get('lead_status') or '—'}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_intel:
        st.markdown('<span class="sg-badge">AI POWERED</span>', unsafe_allow_html=True)
        st.write("")

        try:
            insight_resp = api_get(f"/intelligence/{lead['lead_id']}")
            insight = insight_resp.json() if insight_resp.status_code == 200 else None
        except Exception:
            insight = None

        btn_label = "🔄 Regenerate Insights" if insight else "✨ Generate Lead Intelligence"
        if st.button(btn_label, type="primary"):
            with st.spinner("Analyzing company profile..."):
                gen_resp = api_post(f"/intelligence/generate/{lead['lead_id']}")
                if gen_resp.status_code == 200:
                    insight = gen_resp.json()
                    st.rerun()
                else:
                    st.error(f"Generation failed: {gen_resp.json().get('detail', gen_resp.text)}")

        if insight:
            st.plotly_chart(score_gauge(insight["qualification_score"]), use_container_width=True)
            st.markdown(f"**{insight['score_label']}**")
            st.progress(insight["qualification_score"] / 100)

            if insight.get("business_needs"):
                st.write(f"**Business Needs:** {insight['business_needs']}")
            if insight.get("opportunities"):
                st.write(f"**Opportunity:** {insight['opportunities']}")
            if insight.get("industry_analysis"):
                st.write(f"**Industry Fit:** {insight['industry_analysis']}")

            if insight.get("reasoning"):
                st.markdown("---")
                st.markdown("**Qualification Factors**")
                for item in insight["reasoning"]:
                    st.markdown(f'<div class="sg-factor">▸ {item["factor"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sg-factor-detail">{item["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.caption("No insights generated yet for this lead. Click the button above.")


# --------------------------------------------------------------------------
# MODULE 3 — AI OUTREACH GENERATION
# --------------------------------------------------------------------------
def render_outreach():
    st.markdown('<div class="sg-page-title">AI Outreach Generation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sg-page-subtitle">Generate personalized Cold Emails and Follow-up Emails using AI.</div>',
        unsafe_allow_html=True,
    )

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.warning("No leads found in the database yet. Add some leads first, "
                    "or run seed_data.py to insert sample leads.")
        return

    label_to_lead = {lead_label(l): l for l in leads}

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_label = st.selectbox("Select Lead", list(label_to_lead.keys()))
        selected_lead_id = label_to_lead[selected_label]["lead_id"]
    with col2:
        email_type = st.selectbox("Email Type", ["cold_email", "follow_up"],
                                   format_func=lambda x: "Cold Email" if x == "cold_email" else "Follow-up Email")

    col3, col4 = st.columns([1, 1])
    with col3:
        tone = st.selectbox("Tone", ["professional", "friendly", "direct", "consultative"])
    with col4:
        extra_context = st.text_input("Extra context (optional)", placeholder="e.g. mention their recent funding round")

    if "generated_email" not in st.session_state:
        st.session_state.generated_email = None

    if st.button("✨ Generate Email", type="primary"):
        with st.spinner("Generating personalized email..."):
            try:
                payload = {
                    "lead_id": selected_lead_id, "email_type": email_type,
                    "tone": tone, "extra_context": extra_context or None,
                }
                resp = api_post("/outreach/generate", json=payload)
                if resp.status_code != 200:
                    st.error(f"Generation failed: {safe_json(resp).get('detail', resp.text)}")
                else:
                    st.session_state.generated_email = safe_json(resp)
            except requests.exceptions.Timeout:
                st.error("The AI took too long to respond (timed out after 30s). Try again.")
            except requests.exceptions.ConnectionError:
                st.error("Lost connection to the backend mid-request. Is it still running?")
            except Exception as e:
                st.error(f"Request failed: {e}")

    if st.session_state.generated_email:
        st.markdown("---")
        st.subheader("Generated Email")
        subject = st.text_input("Subject", value=st.session_state.generated_email["subject"])
        body = st.text_area("Body", value=st.session_state.generated_email["body"], height=220)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save as Draft"):
                _save_campaign(selected_lead_id, email_type, tone, subject, body, "draft")
        with c2:
            if st.button("📤 Save & Mark Sent"):
                _save_campaign(selected_lead_id, email_type, tone, subject, body, "sent")

    st.markdown("---")
    st.subheader("Outreach History for this Lead")
    try:
        history = api_get(f"/outreach/history/{selected_lead_id}").json()
    except Exception:
        history = []

    if not history:
        st.caption("No outreach sent to this lead yet.")
    else:
        for c in history:
            status_emoji = "✅" if c["campaign_status"] == "sent" else "📝"
            with st.expander(f"{status_emoji} {c['email_subject']}  ·  {c['email_type']}  ·  {c['campaign_status']}"):
                st.write(c["email_content"])


def _save_campaign(lead_id, email_type, tone, subject, body, status):
    try:
        payload = {
            "lead_id": lead_id, "email_type": email_type, "tone": tone,
            "subject": subject, "body": body, "status": status,
        }
        resp = api_post("/outreach/save", json=payload)
        if resp.status_code == 200:
            st.markdown(f'<div class="sg-success-box">Saved as {status}.</div>', unsafe_allow_html=True)
        else:
            st.error(f"Save failed: {resp.text}")
    except Exception as e:
        st.error(f"Save failed: {e}")


# --------------------------------------------------------------------------
# MODULE 4 — LEAD SCORING UI
# --------------------------------------------------------------------------
def render_lead_scoring():
    st.markdown('<div class="sg-page-title">Lead Scoring & Playbooks</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Calculate prospect fit scores and AI engagement playbooks.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.info("No leads yet. Add one from the 'Add Lead' page first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select a lead to score", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    col_details, col_score = st.columns([1, 1])

    with col_details:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        st.markdown(f"### {lead['company_name']}")
        st.caption(f"{lead.get('industry') or 'Unknown industry'} · {lead.get('segment') or 'Unsegmented'}")
        st.write(f"**Company Size:** {lead.get('company_size') or '—'}")
        st.write(f"**Annual Revenue:** {lead.get('annual_revenue') or '—'}")
        st.write(f"**Location:** {lead.get('location') or '—'}")
        if lead.get("tech_stack"):
            st.write("**Tech Stack:** " + ", ".join(lead["tech_stack"]))
        st.write(f"**Pipeline Stage:** {lead.get('lead_status') or '—'}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_score:
        st.markdown('<span class="sg-badge">QUALIFICATION ENGINE</span>', unsafe_allow_html=True)
        st.write("")

        try:
            score_resp = api_get(f"/scoring/{lead['lead_id']}")
            score_data = score_resp.json() if score_resp.status_code == 200 else None
        except Exception:
            score_data = None

        btn_label = "🔄 Recalculate Fit Score" if score_data else "✨ Compute Fit Score"
        if st.button(btn_label, type="primary"):
            with st.spinner("Calculating lead score..."):
                gen_resp = api_post(f"/scoring/calculate/{lead['lead_id']}")
                if gen_resp.status_code == 200:
                    score_data = gen_resp.json()
                    st.rerun()
                else:
                    st.error(f"Scoring failed: {gen_resp.text}")

        if score_data:
            st.plotly_chart(score_gauge(score_data["total_score"]), use_container_width=True)
            st.markdown(f"**Strategy Recommendation**: `{score_data['recommended_strategy']}`")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Demographic Fit Score", f"{score_data['demographic_score']}/50")
                st.progress(score_data['demographic_score'] / 50.0)
            with c2:
                st.metric("Behavioral Engagement Score", f"{score_data['behavioral_score']}/50")
                st.progress(score_data['behavioral_score'] / 50.0)

            if score_data.get("engagement_playbook"):
                st.markdown("---")
                st.markdown("**AI Engagement Playbook**")
                for step in score_data["engagement_playbook"]:
                    st.write(step)
        else:
            st.caption("No scoring data calculated yet for this lead.")


# --------------------------------------------------------------------------
# MODULE 5 — CONVERSATION INTELLIGENCE & CRM SYNC UI
# --------------------------------------------------------------------------
def render_sales_interactions():
    st.markdown('<div class="sg-page-title">Conversation Intelligence & CRM Sync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Transcribe, summarize meetings, and synchronize leads with Salesforce & HubSpot.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.info("No leads yet. Add one from the 'Add Lead' page first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select target lead for logs & CRM sync", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📝 Log & Summarize Call", "📜 Interaction History", "🔄 CRM Sync Gateway"])

    with tab1:
        st.markdown("### Paste Meeting/Call Transcript")
        st.caption("Pasting raw meeting transcripts (Zoom/Teams exports) automatically extracts summaries, key action points, and customer sentiment.")
        
        sample_transcript = (
            "Agent: Hi, this is Sarah from SalesGenie. Thanks for joining.\n"
            "Client: Hi Sarah. We are currently looking for a B2B lead intelligence tool that supports custom API connections and tracks technology stacks. We run React and python on AWS.\n"
            "Agent: That fits perfectly. We support fully custom integrations. How many seats are you looking to start with?\n"
            "Client: We want to onboard about 40 users next month. But first we need a pricing quote and to see a copy of your SOC2 security report to check compatibility.\n"
            "Agent: Absolutely, I will email you the custom pricing and the SOC2 document by Tuesday. Let's schedule a deep-dive product demo for next Friday at 10 AM.\n"
            "Client: Perfect, that works for us. Thanks!"
        )
        
        transcript_input = st.text_area(
            "Call Transcript Details",
            value=sample_transcript,
            height=200,
            help="Paste the transcription text here."
        )

        if st.button("✨ Summarize & Log Interaction", type="primary"):
            with st.spinner("Extracting insights..."):
                payload = {"lead_id": lead["lead_id"], "transcript": transcript_input}
                resp = api_post("/conversation/summarize", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success("Successfully summarized call and logged to database!")
                    
                    # Display Extracted Summary
                    st.markdown("#### Summary Details")
                    st.write(data["summary"])
                    
                    st.markdown("#### Extracted Sentiment")
                    sentiment = data["sentiment"]
                    s_color = "green" if sentiment == "Positive" else "orange" if sentiment == "Neutral" else "red"
                    st.markdown(f'<span style="background-color: {s_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{sentiment}</span>', unsafe_allow_html=True)
                    
                    st.markdown("#### Action Items Checklist")
                    st.write(data["action_items"])
                else:
                    st.error(f"Summarizer failed: {resp.text}")

    with tab2:
        st.markdown("### Past Interactions Log")
        try:
            interact_resp = api_get(f"/leads/interactions/{lead['lead_id']}")
            interactions = interact_resp.json() if interact_resp.status_code == 200 else []
        except Exception:
            interactions = []

        if not interactions:
            st.caption("No interactions logged for this lead yet.")
        else:
            for idx, inter in enumerate(interactions):
                idate = inter.get("interaction_date", "")[:10]
                with st.expander(f"📞 Meeting/Call on {idate} — Lead ID {inter['lead_id']}"):
                    st.markdown("**Summary**")
                    st.write(inter.get("summary"))
                    st.markdown("**Action Items / Notes**")
                    st.write(inter.get("action_items"))

    with tab3:
        st.markdown("### CRM Synchronization Gateway")
        st.caption("Push lead demographics, enrichment parameters, and recent AI logs to HubSpot/Salesforce.")
        
        provider = st.selectbox("CRM Provider Target", ["HubSpot", "Salesforce", "Microsoft Dynamics"])
        
        if st.button(f"Sync lead to {provider}", type="primary"):
            with st.spinner(f"Initiating handshake with {provider} APIs..."):
                resp = api_post(f"/conversation/sync-crm/{lead['lead_id']}?provider={provider}")
                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown('<div class="sg-success-box">Lead synchronisation completed successfully.</div>', unsafe_allow_html=True)
                    st.write(f"**Synchronised at:** {data['synced_at']}")
                    st.write(f"**Sync Status:** `{data['sync_status']}`")
                    st.json(data["payload_sent"])
                else:
                    st.error(f"Sync failed: {resp.text}")


# --------------------------------------------------------------------------
# MODULE 6 — DASHBOARD UI
# --------------------------------------------------------------------------
def render_dashboard():
    st.markdown('<div class="sg-page-title">Executive Pipeline Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Real-time overview of qualification metrics, segments, and pipeline stages.</div>', unsafe_allow_html=True)

    try:
        resp = api_get("/dashboard/metrics")
        if resp.status_code != 200:
            st.error("Failed to load dashboard metrics from backend API.")
            return
        metrics = resp.json()
    except Exception as e:
        st.error(f"Backend offline or connection error: {e}")
        return

    # 1. KPI Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total Active Prospects", metrics["total_leads"])
    with kpi2:
        st.metric("Avg. Qualification Score", f"{metrics['average_lead_score']}/100")
    with kpi3:
        segments = metrics["segment_metrics"]
        top_seg = max(segments, key=segments.get) if segments else "N/A"
        st.metric("Dominant Segment", top_seg)

    st.write("")

    # 2. Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### Segment Distribution")
        seg_data = metrics["segment_metrics"]
        if not seg_data:
            st.caption("No segment data available.")
        else:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(seg_data.keys()),
                values=list(seg_data.values()),
                hole=0.4,
                marker=dict(colors=["#6366f1", "#10b981", "#f59e0b", "#ec4899"])
            )])
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f5f5f5"),
                showlegend=True,
                margin=dict(t=10, b=10, l=10, r=10),
                height=250
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("### Pipeline Stages")
        stage_data = metrics["stage_metrics"]
        if not stage_data:
            st.caption("No pipeline stage data available.")
        else:
            fig_bar = go.Figure(data=[go.Bar(
                x=list(stage_data.keys()),
                y=list(stage_data.values()),
                marker_color="#6366f1"
            )])
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f5f5f5"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=250,
                xaxis=dict(gridcolor="#374151"),
                yaxis=dict(gridcolor="#374151")
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Top Prospects Table
    st.markdown("### Top Scored Prospects")
    top_prospects = metrics["top_prospects"]
    if not top_prospects:
        st.caption("No lead scores calculated yet. Go to 'Lead Scoring' to calculate scores.")
    else:
        import pandas as pd
        df = pd.DataFrame(top_prospects)
        # Clean columns for display
        df.columns = ["Lead ID", "Company Name", "Contact Name", "Segment", "Fit Score", "Recommended Strategy"]
        st.dataframe(df, use_container_width=True, hide_index=True)


# --------------------------------------------------------------------------
# PLACEHOLDER PAGES (Milestones 2-4, not built yet)
# --------------------------------------------------------------------------
def render_placeholder(title: str, note: str):
    st.markdown(f'<div class="sg-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sg-page-subtitle">{note}</div>', unsafe_allow_html=True)
    st.info("Not part of Milestone 1's scope (Modules 1-3) — coming in a later milestone.")


# --------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------
if page == "Lead Management":
    render_lead_management()
elif page == "Add Lead":
    render_add_lead()
elif page == "Lead Intelligence":
    render_lead_intelligence()
elif page == "Lead Scoring":
    render_lead_scoring()
elif page == "AI Outreach":
    render_outreach()
elif page == "Dashboard":
    render_dashboard()
elif page == "Sales Interactions":
    render_sales_interactions()



