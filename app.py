"""
app.py
Streamlit frontend for SalesGenie AI — Modules 1, 2, and 3 fully wired up.
Run with: streamlit run app.py --server.port 8502
(or via run_all.py which starts backend + frontend together)
"""

import os
from collections import Counter
import requests
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="SalesGenie AI", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.session_state.theme

colors = {
    "dark": {
        "bg": "#0f172a",
        "fg": "#f8fafc",
        "muted": "#cbd5e1",
        "sidebar": "#111827",
        "border": "#334155",
        "card": "#111c2f",
        "widget": "#0b1220",
        "widget_border": "#475569",
        "widget_text": "#f8fafc",
        "accent": "#38bdf8",
        "accent_2": "#2563eb",
        "error_bg": "#2a1118",
        "error_fg": "#fecdd3",
        "error_border": "#be123c",
        "success_bg": "#10241d",
        "success_fg": "#bbf7d0",
        "success_border": "#16a34a",
        "badge_bg": "#1d4ed8",
        "badge_fg": "#dbeafe",
        "label": "#e2e8f0",
    },
    "light": {
        "bg": "#f8fafc",
        "fg": "#0f172a",
        "muted": "#475569",
        "sidebar": "#ffffff",
        "border": "#dbe4f0",
        "card": "#ffffff",
        "widget": "#f8fbff",
        "widget_border": "#cbd5e1",
        "widget_text": "#0f172a",
        "accent": "#2563eb",
        "accent_2": "#1d4ed8",
        "error_bg": "#fef2f2",
        "error_fg": "#b91c1c",
        "error_border": "#fecaca",
        "success_bg": "#f0fdf4",
        "success_fg": "#166534",
        "success_border": "#bbf7d0",
        "badge_bg": "#dbeafe",
        "badge_fg": "#1d4ed8",
        "label": "#334155",
    },
}

selected = colors[theme]

st.markdown(f"""
<style>
    :root {{
        --bg: {selected['bg']};
        --fg: {selected['fg']};
        --muted: {selected['muted']};
        --sidebar: {selected['sidebar']};
        --border: {selected['border']};
        --card: {selected['card']};
        --widget: {selected['widget']};
        --widget-border: {selected['widget_border']};
        --widget-text: {selected['widget_text']};
        --accent: {selected['accent']};
        --accent-2: {selected['accent_2']};
        --error-bg: {selected['error_bg']};
        --error-fg: {selected['error_fg']};
        --error-border: {selected['error_border']};
        --success-bg: {selected['success_bg']};
        --success-fg: {selected['success_fg']};
        --success-border: {selected['success_border']};
        --badge-bg: {selected['badge_bg']};
        --badge-fg: {selected['badge_fg']};
        --label: {selected['label']};
    }}
    * {{ color: var(--fg); }}
    body, .stApp {{ background-color: var(--bg); color: var(--fg); }}
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar);
        border-right: 1px solid var(--border);
    }}
    /* Navigation & Labels */
    label {{ color: var(--label) !important; font-weight: 500; }}
    .stRadio label {{ color: var(--fg) !important; }}
    .stCheckbox label {{ color: var(--fg) !important; }}
    
    /* Sidebar elements */
    .sg-title {{ font-size: 28px; font-weight: 800; color: var(--accent); margin-bottom: 0px; }}
    .sg-subtitle {{ font-size: 13px; color: var(--muted); margin-top: 0px; margin-bottom: 24px; }}
    .sg-nav-header {{
        font-size: 12px; color: var(--muted); letter-spacing: 1px;
        text-transform: uppercase; margin: 18px 0 6px 0; font-weight: 600;
    }}
    
    /* Page headers */
    .sg-page-title {{ font-size: 42px; font-weight: 800; color: var(--fg); margin-bottom: 4px; }}
    .sg-page-subtitle {{ font-size: 15px; color: var(--muted); margin-bottom: 28px; }}
    
    /* Alerts & Messages */
    .sg-error-box {{
        background-color: var(--error-bg); border: 1px solid var(--error-border); color: var(--error-fg);
        padding: 16px 20px; border-radius: 8px; font-size: 15px;
    }}
    .sg-success-box {{
        background-color: var(--success-bg); border: 1px solid var(--success-border); color: var(--success-fg);
        padding: 14px 18px; border-radius: 8px; font-size: 14px;
    }}
    
    /* Cards & Containers */
    .sg-card {{
        background-color: var(--card); border: 1px solid var(--border); border-radius: 14px;
        padding: 20px; margin-bottom: 16px; color: var(--fg);
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
    }}
    .sg-badge {{
        display: inline-block; background-color: var(--badge-bg); color: var(--badge-fg);
        font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px;
        letter-spacing: 0.5px;
    }}
    .sg-hero {{
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 55%, #ec4899 100%);
        color: white; padding: 24px 28px; border-radius: 18px; margin-bottom: 20px;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.2);
    }}
    .sg-hero-title {{ font-size: 28px; font-weight: 800; margin-bottom: 6px; }}
    .sg-hero-subtitle {{ font-size: 15px; opacity: 0.95; }}
    .sg-pill {{
        display: inline-block; background: rgba(255,255,255,0.2); padding: 6px 12px;
        border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}
    .stMetric {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 12px; }}
    
    /* Qualification factors */
    .sg-factor {{ font-weight: 700; color: var(--fg); font-size: 14px; margin-bottom: 2px; }}
    .sg-factor-detail {{ color: var(--muted); font-size: 13px; margin-bottom: 14px; }}
    
    /* Form inputs - comprehensive styling */
    input[type="text"],
    input[type="number"],
    input[type="email"],
    input[type="password"],
    textarea,
    select {{
        background-color: var(--widget) !important;
        color: var(--widget-text) !important;
        border: 1px solid var(--widget-border) !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
    }}
    input[type="text"]::placeholder,
    textarea::placeholder {{
        color: var(--muted) !important;
    }}
    
    /* Streamlit components */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {{
        background-color: var(--widget) !important;
        color: var(--widget-text) !important;
        border: 1px solid var(--widget-border) !important;
    }}
    .stSelectbox>div>div>div,
    .stMultiSelect>div>div>div {{
        background-color: var(--widget) !important;
        border: 1px solid var(--widget-border) !important;
    }}
    .stSelectbox [data-testid="selectbox-popper"],
    .stMultiSelect [data-testid="multiselect-popper"] {{
        background-color: var(--card) !important;
    }}
    
    /* Radio buttons */
    div[data-testid="stRadio"] label {{ 
        font-size: 15px; padding: 4px 0; color: var(--fg) !important; 
    }}
    div[data-testid="stRadio"] {{ color: var(--fg) !important; }}
    
    /* Buttons */
    .stButton>button {{
        background-color: var(--accent-2); color: white; border: none; border-radius: 6px;
        font-weight: 600; padding: 8px 24px;
    }}
    .stButton>button:hover {{ background-color: var(--accent); }}
    
    /* Dataframe */
    .stDataFrame {{ background-color: transparent; }}
    [data-testid="stDataFrame"] {{ background-color: var(--card); }}
    
    /* Dividers */
    hr {{ border-color: var(--border); }}
    
    /* Captions & help text */
    .stCaption, .stHelp {{ color: var(--muted) !important; }}
    
    /* Expanders */
    .streamlit-expanderHeader {{ color: var(--fg) !important; }}
    
    /* Subheaders */
    h1, h2, h3, h4, h5, h6 {{ color: var(--fg) !important; }}
    
    /* Tabs */
    .stTabs [data-testid="stTab"] {{ color: var(--muted); }}
    .stTabs [aria-selected="true"] {{ color: var(--accent) !important; }}
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

def fetch_leads(q: str = None):
    params = {"q": q} if q else {}
    resp = api_get("/leads", params=params)
    resp.raise_for_status()
    return resp.json()


def lead_label(l: dict) -> str:
    seg = f" · {l['segment']}" if l.get("segment") else ""
    return f"{l['company_name']} — {l.get('contact_name') or 'No contact'}{seg}"


def fmt_money(v) -> str:
    return f"${v:,}" if v else "—"


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

    theme_toggle = st.radio(
        "Theme",
        ["dark", "light"],
        horizontal=True,
        index=0 if st.session_state.theme == "dark" else 1,
        label_visibility="visible",
    )
    if theme_toggle != st.session_state.theme:
        st.session_state.theme = theme_toggle
        st.rerun()

    st.markdown('<div class="sg-nav-header">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        label="Navigation",
        options=[
            "Dashboard",
            "Lead Management",
            "Add Lead",
            "Lead Intelligence",
            "AI Outreach",
            "Lead Scoring",
            "Conversations",
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
            "Deal Value": f"${l['deal_value']:,}" if l.get("deal_value") else "—",
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
            deal_value = st.number_input("Est. Deal Value ($)", min_value=0, step=5000,
                                          value=int(lead.get("deal_value") or 0))
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
            "deal_value": int(deal_value) if deal_value else None,
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
            deal_value = st.number_input("Est. Deal Value ($)", min_value=0, step=5000, value=0)
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
            "deal_value": int(deal_value) if deal_value else None,
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
def score_gauge(score: int, theme_name: str = None):
    theme_name = theme_name or st.session_state.get("theme", "dark")
    is_light = theme_name == "light"

    color = "#22c55e" if score >= 75 else "#eab308" if score >= 45 else "#ef4444"
    text_color = "#0f172a" if is_light else "#f8fafc"
    background_color = "#ffffff" if is_light else "#111c2f"
    axis_color = "#64748b" if is_light else "#94a3b8"
    step_colors = [
        ("#fee2e2", "#fda4af") if is_light else ("#2a1a1a", "#7f1d1d"),
        ("#fef3c7", "#f59e0b") if is_light else ("#2a2410", "#a16207"),
        ("#dcfce7", "#22c55e") if is_light else ("#0f2a1a", "#15803d"),
    ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 40, "color": text_color}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": axis_color, "tickfont": {"color": text_color}},
            "bar": {"color": color},
            "bgcolor": background_color,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 45], "color": step_colors[0][0]},
                {"range": [45, 75], "color": step_colors[1][0]},
                {"range": [75, 100], "color": step_colors[2][0]},
            ],
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": text_color},
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
        st.write(f"**Est. Deal Value:** {fmt_money(lead.get('deal_value'))}")
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
            st.plotly_chart(score_gauge(insight["qualification_score"], theme_name=theme), use_container_width=True)
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
# MODULE 4 — LEAD SCORING & RECOMMENDATIONS
# --------------------------------------------------------------------------
def render_lead_scoring():
    st.markdown('<div class="sg-page-title">Lead Scoring & Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Rank prospects and run simulated What-If analyses.</div>', unsafe_allow_html=True)

    tab_rank, tab_score, tab_sim = st.tabs([
        "🏆 Priority Rankings",
        "📊 Score & AI Recommendations",
        "🧪 What-If Simulator"
    ])

    with tab_rank:
        st.subheader("Lead Priority Pipeline")
        try:
            rankings = api_get("/scoring/ranking/list").json()
        except Exception as e:
            st.error(f"Could not load rankings: {e}")
            rankings = []
        
        if rankings:
            table_rows = [
                {
                    "Company": r["company_name"],
                    "Score": r["score"],
                    "Classification": r["classification"],
                    "Industry": r.get("industry") or "—",
                    "Status": r.get("lead_status") or "—",
                }
                for r in rankings
            ]
            st.dataframe(table_rows, use_container_width=True, hide_index=True)
        else:
            st.info("No scores available. Recalculate scoring for a lead under the 'Score & AI Recommendations' tab.")

    with tab_score:
        try:
            leads = fetch_leads()
        except Exception as e:
            st.error(f"Could not load leads: {e}")
            return
        if not leads:
            st.warning("No leads found. Add some leads first.")
            return

        label_to_lead = {lead_label(l): l for l in leads}
        selected_label = st.selectbox("Select Lead to Score", list(label_to_lead.keys()), key="score_lead_select")
        lead = label_to_lead[selected_label]
        lead_id = lead["lead_id"]

        col_profile, col_score = st.columns([1, 1])

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
            st.write(f"**Est. Deal Value:** {fmt_money(lead.get('deal_value'))}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_score:
            try:
                score_resp = api_get(f"/scoring/{lead_id}")
                score_data = score_resp.json() if score_resp.status_code == 200 else None
            except Exception:
                score_data = None

            btn_label = "🔄 Recalculate Score" if score_data else "✨ Calculate Lead Score"
            if st.button(btn_label, type="primary", key="calc_score_btn"):
                with st.spinner("Calculating score and generating recommendations..."):
                    gen_resp = api_post(f"/scoring/generate/{lead_id}")
                    if gen_resp.status_code == 200:
                        st.success("Lead score generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {gen_resp.text}")

            if score_data:
                st.plotly_chart(score_gauge(score_data["score"], theme_name=theme), use_container_width=True, key=f"score_gauge_{lead_id}")
                st.markdown(f"**Priority Level:** `{score_data['classification']}`")
                
                conf = score_data.get("confidence_score", 0)
                st.markdown(f"**Data Confidence Score:** {conf}%")
                st.progress(conf / 100)

                st.markdown("---")
                st.markdown("**Scoring Breakdown**")
                explanation = score_data.get("explanation", {})
                for factor, points in explanation.items():
                    st.write(f"**{factor}:** {points} pts")

                st.markdown("---")
                st.markdown("**AI Recommendations & Next Steps**")
                st.markdown(score_data.get("recommendations", "No recommendations found."))
            else:
                st.caption("No score generated yet. Click the button above.")

    with tab_sim:
        st.subheader("What-If Score Simulator")
        st.caption("Adjust the parameters below to see how they impact the lead score in real time. This will not modify the database.")
        
        sim_label_to_lead = {lead_label(l): l for l in leads}
        sim_selected_label = st.selectbox("Select Lead to Simulate", list(sim_label_to_lead.keys()), key="sim_lead_select")
        sim_lead = sim_label_to_lead[sim_selected_label]
        sim_lead_id = sim_lead["lead_id"]

        with st.form("what_if_simulator_form"):
            c1, c2 = st.columns(2)
            with c1:
                comp_size = st.text_input("Company Size", value=sim_lead.get("company_size") or "")
                ann_rev = st.text_input("Annual Revenue", value=sim_lead.get("annual_revenue") or "")
                funding = st.text_input("Funding Stage", value=sim_lead.get("funding_stage") or "")
                industry = st.text_input("Industry", value=sim_lead.get("industry") or "")
                
                hiring_trend = st.selectbox("Hiring Trend", ["Stable", "Growing", "Declining"])
                website_eng = st.selectbox("Website Engagement", ["Low", "Medium", "High"])

            with c2:
                email_open = st.selectbox("Email Open Rate", ["No Outreach", "Sent but Not Opened", "Opened"])
                email_reply = st.selectbox("Email Reply Status", ["No Reply", "Replied"])
                linkedin_eng = st.selectbox("LinkedIn Engagement", ["No Engagement", "Engaged"])
                recent_news = st.selectbox("Recent News", ["No News", "Positive News"])
                demo_booked = st.checkbox("Demo/Meeting Booked", value=False)

            run_sim = st.form_submit_button("🧪 Run Simulation", type="primary")

        if run_sim:
            payload = {
                "lead_id": sim_lead_id,
                "company_size": comp_size or None,
                "annual_revenue": ann_rev or None,
                "funding_stage": funding or None,
                "industry": industry or None,
                "hiring_trend": hiring_trend,
                "website_engagement": website_eng,
                "email_open_rate": email_open,
                "email_reply": email_reply,
                "linkedin_engagement": linkedin_eng,
                "recent_news": recent_news,
                "demo_booked": demo_booked
            }
            with st.spinner("Simulating..."):
                sim_resp = api_post("/scoring/simulate", json=payload)
                if sim_resp.status_code == 200:
                    sim_data = sim_resp.json()
                    st.success("Simulation Complete!")
                    
                    sc1, sc2 = st.columns([1, 1])
                    with sc1:
                        st.plotly_chart(score_gauge(sim_data["score"], theme_name=theme), use_container_width=True, key=f"sim_gauge_{sim_lead_id}")
                        st.markdown(f"**Simulated Classification:** `{sim_data['classification']}`")
                        st.markdown(f"**Simulated Data Confidence:** {sim_data.get('confidence_score', 0)}%")
                    with sc2:
                        st.markdown("**Simulated Scoring Explanation**")
                        for factor, points in sim_data.get("explanation", {}).items():
                            st.write(f"**{factor}:** {points} pts")
                        st.markdown("---")
                        st.markdown("**Simulated AI recommendations**")
                        st.markdown(sim_data.get("recommendations", ""))
                else:
                    st.error(f"Simulation failed: {sim_resp.text}")


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
# MODULE 6 — DASHBOARD & SALES ANALYTICS
# --------------------------------------------------------------------------
PRIORITY_COLORS = {"High": "#7f1d3a", "Medium": "#7a5b12", "Low": "#1e3a5f"}
PRIORITY_TEXT = {"High": "#fca5a5", "Medium": "#fcd34d", "Low": "#7dd3fc"}
CLASS_COLORS = {
    "Platinum": ("#3a2f6b", "#c4b5fd"),
    "Gold": ("#7a5b12", "#fcd34d"),
    "Silver": ("#3a3f4b", "#d1d5db"),
    "Bronze": ("#5c3a1e", "#fdba74"),
    "Low Priority": ("#262730", "#9ca3af"),
}


def badge(text: str, bg: str, fg: str) -> str:
    return (f'<span style="display:inline-block;background-color:{bg};color:{fg};'
            f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:12px;'
            f'letter-spacing:0.5px;">{text}</span>')


def build_stage_chart(pipeline):
    stages = pipeline.get("stages", [])
    counts = [len(pipeline.get("columns", {}).get(stage, [])) for stage in stages]
    colors = ["#60a5fa", "#34d399", "#f59e0b", "#f472b6", "#a78bfa", "#fb7185", "#2dd4bf"]
    fig = go.Figure(data=[go.Bar(x=stages, y=counts, marker_color=colors[:len(stages)])])
    fig.update_layout(
        title="Leads by Sales Stage",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=280,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.2)"),
    )
    return fig


def build_segment_chart(leads):
    counts = Counter((lead.get("segment") or "Unspecified") for lead in leads)
    labels = list(counts.keys())
    values = list(counts.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.45, marker_colors=["#60a5fa", "#34d399", "#f59e0b", "#f472b6", "#a78bfa"])])
    fig.update_layout(
        title="Lead Mix by Segment",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=280,
    )
    return fig


def render_dashboard():
    st.markdown('<div class="sg-page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Sales pipeline, conversion, and follow-up recommendations across all leads.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-hero"><div class="sg-pill">LIVE SALES INSIGHTS</div><div class="sg-hero-title">Turn your pipeline into a colorful, actionable view.</div><div class="sg-hero-subtitle">Monitor momentum, spot hot accounts, and keep the team aligned with live charts and recommendations.</div></div>', unsafe_allow_html=True)

    try:
        overview = api_get("/dashboard/overview").json()
    except Exception as e:
        st.error(f"Could not load dashboard: {e}")
        return

    try:
        leads = fetch_leads()
    except Exception:
        leads = []

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Leads", overview["total_leads"])
    c2.metric("Conversion Rate", f"{overview['conversion_rate']}%")
    c3.metric("Open Pipeline Value", fmt_money(overview["pipeline_value"]))
    c4.metric("Avg Lead Score", overview["avg_lead_score"] if overview["avg_lead_score"] is not None else "—")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Qualification Score", overview["avg_qualification_score"] if overview["avg_qualification_score"] is not None else "—")
    c6.metric("Campaigns Sent", overview["campaigns_sent"])
    c7.metric("Campaigns Drafted", overview["campaigns_draft"])
    c8.metric("Interactions Logged", overview["interactions_logged"])

    st.markdown("---")
    try:
        pipeline = api_get("/dashboard/pipeline").json()
    except Exception as e:
        st.error(f"Could not load pipeline: {e}")
        pipeline = None

    chart_col1, chart_col2 = st.columns([1.1, 0.9])
    with chart_col1:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        if pipeline:
            st.plotly_chart(build_stage_chart(pipeline), use_container_width=True)
        else:
            st.caption("Pipeline chart unavailable")
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        st.plotly_chart(build_segment_chart(leads), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Sales Pipeline")

    if pipeline:
        cols = st.columns(len(pipeline["stages"]))
        for col, stage in zip(cols, pipeline["stages"]):
            leads_in_stage = pipeline["columns"][stage]
            with col:
                st.markdown(f"**{stage}**")
                st.caption(f"{len(leads_in_stage)} lead(s)")
                for l in leads_in_stage:
                    cls = l.get("classification")
                    bg, fg = CLASS_COLORS.get(cls, ("#262730", "#9ca3af"))
                    cls_badge = badge(cls, bg, fg) if cls else ""
                    st.markdown(
                        f'<div class="sg-card" style="padding:12px;margin-bottom:10px;">'
                        f'<div style="font-weight:700;font-size:13px;">{l["company_name"]}</div>'
                        f'<div style="color:#9ca3af;font-size:12px;margin:4px 0;">{fmt_money(l.get("deal_value"))}</div>'
                        f'{cls_badge}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("---")
    st.subheader("Automated Follow-Up Recommendations")
    try:
        followups = api_get("/dashboard/followups").json()
    except Exception as e:
        st.error(f"Could not load follow-ups: {e}")
        followups = []

    if not followups:
        st.info("No follow-ups flagged right now — score more leads under Lead Scoring to populate this feed.")
    for f in followups:
        bg = PRIORITY_COLORS.get(f["priority"], "#262730")
        fg = PRIORITY_TEXT.get(f["priority"], "#9ca3af")
        st.markdown(
            f'<div class="sg-card" style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-weight:700;">{f["company_name"]} <span style="color:#6b7280;font-weight:400;">· {f.get("lead_status") or "—"}</span></div>'
            f'<div style="color:#9ca3af;font-size:13px;margin-top:4px;">{f["reason"]}</div>'
            f'</div>'
            f'{badge(f["priority"] + " Priority", bg, fg)}'
            f'</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# MODULE 5 — CONVERSATION INTELLIGENCE & CRM INTEGRATION
# --------------------------------------------------------------------------
def render_conversations():
    st.markdown('<div class="sg-page-title">Conversations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">CRM sync status and AI-powered meeting/call summarization.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.warning("No leads found. Add some leads first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select Lead", list(label_to_lead.keys()), key="conv_lead_select")
    lead = label_to_lead[selected_label]
    lead_id = lead["lead_id"]

    tab_crm, tab_summary, tab_activity = st.tabs(["🔄 CRM Sync Status", "🧠 Meeting Summary (AI Powered)", "📋 Recent Activity"])

    with tab_crm:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        st.markdown(f"**{lead['company_name']}** — sync this lead's current profile to a CRM platform.")
        st.caption("Simulated integration: no live Salesforce/HubSpot credentials are configured for this "
                   "project, so this logs the same sync record a real integration would produce.")
        platform = st.selectbox("CRM Platform", ["Salesforce", "HubSpot"], key="crm_platform_select")
        if st.button("Sync Now", key="crm_sync_btn"):
            try:
                resp = api_post(f"/conversation/sync/{lead_id}", json={"crm_platform": platform})
                if resp.status_code == 200:
                    log = resp.json()
                    st.markdown(f'<div class="sg-success-box">Synced to {log["crm_platform"]} at {log["timestamp"]}.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="sg-error-box">Sync failed: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Sync History**")
        try:
            logs = api_get(f"/conversation/sync/logs/{lead_id}").json()
        except Exception as e:
            st.error(f"Could not load sync history: {e}")
            logs = []
        if logs:
            st.dataframe(
                [{"Platform": l["crm_platform"], "Status": l["sync_status"],
                  "Detail": l.get("detail") or "—", "Timestamp": l["timestamp"]} for l in logs],
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("No sync history yet for this lead.")

    with tab_summary:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        interaction_type = st.radio("Type", ["Call", "Meeting"], horizontal=True, key="conv_type_radio")
        transcript = st.text_area(
            "Paste the call/meeting transcript",
            height=180,
            placeholder="Rep: Hi Sarah, thanks for joining...\nSarah: We're looking for better data pipeline monitoring...",
            key="conv_transcript_input",
        )
        if st.button("Generate Summary", key="conv_summarize_btn"):
            if not transcript.strip():
                st.warning("Paste a transcript first.")
            else:
                with st.spinner("Summarizing with AI..."):
                    try:
                        resp = api_post("/conversation/summarize", json={
                            "lead_id": lead_id, "transcript": transcript, "interaction_type": interaction_type,
                        })
                        if resp.status_code == 200:
                            st.session_state["last_summary"] = resp.json()
                            st.markdown('<div class="sg-success-box">Summary generated.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="sg-error-box">Summarization failed: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        summary = st.session_state.get("last_summary")
        if summary and summary.get("lead_id") == lead_id:
            st.markdown('<div class="sg-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="sg-badge">AI POWERED</span>', unsafe_allow_html=True)
            st.markdown(f"**{summary['interaction_type']} Summary**")
            st.write(summary.get("summary") or "—")
            st.markdown("**Action Items**")
            items = (summary.get("action_items") or "").split(" | ")
            for item in items:
                if item.strip():
                    st.markdown(f"- {item.strip()}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Past AI Summaries for this Lead**")
        try:
            summaries = api_get(f"/conversation/summaries/{lead_id}").json()
        except Exception as e:
            st.error(f"Could not load past summaries: {e}")
            summaries = []
        if summaries:
            for s in summaries:
                with st.expander(f"{s['interaction_type']} — {s['interaction_date']}"):
                    st.write(s.get("summary") or "—")
                    st.caption(s.get("action_items") or "No action items recorded.")
        else:
            st.caption("No AI summaries generated yet for this lead.")

    with tab_activity:
        st.markdown("**Recent CRM Sync Activity (all leads)**")
        try:
            recent = api_get("/conversation/sync/logs").json()
        except Exception as e:
            st.error(f"Could not load recent activity: {e}")
            recent = []
        if recent:
            lead_names = {l["lead_id"]: l["company_name"] for l in leads}
            st.dataframe(
                [{"Company": lead_names.get(r["lead_id"], f"Lead #{r['lead_id']}"),
                  "Platform": r["crm_platform"], "Status": r["sync_status"],
                  "Timestamp": r["timestamp"]} for r in recent],
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("No sync activity yet across any lead.")


# --------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------
if page == "Lead Management":
    render_lead_management()
elif page == "Add Lead":
    render_add_lead()
elif page == "Lead Intelligence":
    render_lead_intelligence()
elif page == "AI Outreach":
    render_outreach()
elif page == "Lead Scoring":
    render_lead_scoring()
elif page == "Dashboard":
    render_dashboard()
elif page == "Conversations":
    render_conversations()
