from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10

st.set_page_config(
    page_title="SalesGenie AI",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg:        #0A0F1E;
            --surface:   #131B2E;
            --surface-2: #182339;
            --border:    #253048;
            --text:      #EEF2F8;
            --text-dim:  #AAB4C8;
            --text-mute: #7C88A0;
            --cyan:      #2FD8E5;
            --amber:     #F4B740;
            --emerald:   #3ADC91;
            --coral:     #FF6B7A;
            --violet:    #9B8CFF;
        }

        html, body, .stApp {
            background-color: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', sans-serif;
        }

        /* ---------- Typography ---------- */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'Sora', sans-serif !important;
            color: var(--text) !important;
            letter-spacing: -0.01em;
        }

        h1 { font-weight: 800 !important; }
        h2, h3 { font-weight: 700 !important; }

        p, span, label, div, li {
            color: var(--text) !important;
        }

        .stCaption, [data-testid="stCaptionContainer"], small {
            color: var(--text-dim) !important;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background-color: var(--surface) !important;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] h1 {
            font-size: 1.4rem !important;
            background: linear-gradient(90deg, var(--cyan), var(--violet));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: var(--text-mute) !important;
            margin-bottom: 1.2rem;
        }

        [data-testid="stSidebar"] label {
            color: var(--text) !important;
        }

        /* Sidebar radio nav as pill list */
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background-color: transparent;
            border-radius: 8px;
            padding: 8px 10px !important;
            margin-bottom: 2px;
            transition: background-color 0.15s ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background-color: var(--surface-2);
        }

        /* ---------- Buttons ---------- */
        .stButton button, .stFormSubmitButton button,
        [data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button,
        button[kind="secondary"], button[kind="secondaryFormSubmit"],
        button[kind="primary"], button[kind="primaryFormSubmit"],
        button[data-testid^="baseButton"] {
            background-color: var(--cyan) !important;
            color: #08131A !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: transform 0.1s ease, box-shadow 0.15s ease;
        }

        .stButton button *, .stFormSubmitButton button *,
        [data-testid="stButton"] button *, [data-testid="stFormSubmitButton"] button *,
        button[kind="secondary"] *, button[kind="secondaryFormSubmit"] *,
        button[kind="primary"] *, button[kind="primaryFormSubmit"] *,
        button[data-testid^="baseButton"] * {
            color: #08131A !important;
        }

        .stButton button:hover, .stFormSubmitButton button:hover,
        [data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover,
        button[kind="secondary"]:hover, button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(47, 216, 229, 0.25);
        }

        /* ---------- Dropdown popovers (portaled outside .stApp) ---------- */
        [data-baseweb="popover"], [data-baseweb="menu"],
        ul[data-testid="stSelectboxVirtualDropdown"] {
            background-color: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        [data-baseweb="menu"] li, [role="option"], [role="listbox"] * {
            color: var(--text) !important;
            background-color: transparent !important;
        }

        [data-baseweb="menu"] li:hover, [role="option"]:hover {
            background-color: var(--surface) !important;
        }

        /* ---------- Inputs ---------- */
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div,
        .stDateInput input, .stNumberInput input {
            background-color: var(--surface-2) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: var(--text-mute) !important;
        }

        /* ---------- Dataframe ---------- */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }

        /* ---------- Alerts ---------- */
        [data-testid="stAlert"] {
            border-radius: 10px !important;
            border: 1px solid var(--border) !important;
        }

        /* ---------- Expander ---------- */
        [data-testid="stExpander"] {
            background-color: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
        }

        /* ---------- Custom signature metric cards ---------- */
        .sg-metric-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 8px;
            margin-bottom: 24px;
        }

        .sg-metric-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 18px 20px 16px 20px;
            position: relative;
            overflow: hidden;
        }

        .sg-metric-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent, var(--cyan));
        }

        .sg-metric-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--text-mute) !important;
            margin-bottom: 6px;
        }

        .sg-metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.1rem;
            font-weight: 700;
            color: var(--text) !important;
            line-height: 1;
        }

        /* ---------- Status badges ---------- */
        .sg-badge {
            display: inline-block;
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 999px;
            text-transform: capitalize;
        }

        /* ---------- Score readout (Lead Intelligence) ---------- */
        .sg-score-wrap {
            background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .sg-score-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 3rem;
            font-weight: 700;
            color: var(--amber) !important;
            line-height: 1;
        }

        .sg-score-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: var(--text-dim) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }

        .sg-insight-block {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent, var(--cyan));
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }

        .sg-insight-title {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--accent, var(--cyan)) !important;
            margin-bottom: 6px;
        }

        .sg-insight-text {
            color: var(--text) !important;
            font-size: 0.95rem;
            line-height: 1.5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label: str, value: int | str, accent: str = "cyan") -> str:
    """Return HTML for a single signature metric card."""
    return (
        f'<div class="sg-metric-card" style="--accent: var(--{accent})">'
        f'<div class="sg-metric-label">{label}</div>'
        f'<div class="sg-metric-value">{value}</div>'
        f"</div>"
    )


def status_badge(status: str) -> str:
    """Return HTML for a colored status badge."""
    palette = {
        "new": ("#1E3A52", "#7DD3FC"),
        "qualified": ("#173B2E", "#3ADC91"),
        "proposal": ("#3A2E17", "#F4B740"),
        "negotiation": ("#332146", "#C4A6FF"),
        "closed_won": ("#123424", "#34D399"),
        "closed_lost": ("#3A1B22", "#FF6B7A"),
    }
    bg, fg = palette.get(status.strip().lower(), ("#232D45", "#AAB4C8"))
    return (
        f'<span class="sg-badge" style="background-color:{bg}; color:{fg} !important;">'
        f"{status}</span>"
    )




def api_request(
    method: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
) -> tuple[Any | None, str | None]:
    """Send a request to the FastAPI backend."""
    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return None, "Unable to connect to the FastAPI backend."

    if response.status_code == 204:
        return None, None

    try:
        response_data = response.json()
    except ValueError:
        response_data = None

    if response.ok:
        return response_data, None

    if isinstance(response_data, dict):
        detail = response_data.get("detail")
        if isinstance(detail, str):
            return None, detail

    return None, f"Request failed with status code {response.status_code}."


def get_leads() -> tuple[list[dict[str, Any]], str | None]:
    """Retrieve all leads from the backend."""
    data, error = api_request("GET", "/leads")

    if error:
        return [], error

    if isinstance(data, list):
        return data, None

    return [], "The backend returned an invalid lead response."


def get_interactions(
    lead_id: int,
) -> tuple[list[dict[str, Any]], str | None]:
    """Retrieve all interactions for a lead."""
    data, error = api_request("GET", f"/leads/{lead_id}/interactions")

    if error:
        return [], error

    if isinstance(data, list):
        return data, None

    return [], "The backend returned an invalid interaction response."


def get_insights(
    lead_id: int,
) -> tuple[list[dict[str, Any]], str | None]:
    """Retrieve all AI-generated insights for a lead."""
    data, error = api_request("GET", f"/leads/{lead_id}/insights")

    if error:
        # A 404 here just means "no insights yet" - not a real error
        if error == "No insights found for this lead":
            return [], None
        return [], error

    if isinstance(data, list):
        return data, None

    return [], "The backend returned an invalid insight response."


def render_dashboard() -> None:
    """Render the Module 1 lead management dashboard."""
    st.title("Lead Management Dashboard")
    st.caption("Module 1 · Lead Management & Prospect Database")

    with st.spinner("Loading lead metrics..."):
        leads, error = get_leads()

        if error:
            st.error(error)
            return

        total_interactions = 0
        interaction_error: str | None = None

        for lead in leads:
            lead_id = lead.get("lead_id")

            if not isinstance(lead_id, int):
                continue

            interactions, current_error = get_interactions(lead_id)

            if current_error:
                interaction_error = current_error
                break

            total_interactions += len(interactions)

    new_leads = sum(
        lead.get("lead_status", "").strip().lower() == "new"
        for lead in leads
    )
    qualified_leads = sum(
        lead.get("lead_status", "").strip().lower() == "qualified"
        for lead in leads
    )

    st.markdown(
        '<div class="sg-metric-row">'
        + metric_card("Total Leads", len(leads), "cyan")
        + metric_card("New Leads", new_leads, "violet")
        + metric_card("Qualified Leads", qualified_leads, "emerald")
        + metric_card("Total Interactions", total_interactions, "amber")
        + "</div>",
        unsafe_allow_html=True,
    )

    if interaction_error:
        st.warning(
            "Some interaction metrics could not be loaded. "
            f"{interaction_error}"
        )


def render_lead_management() -> None:
    """Render the lead listing, viewing, editing, and deletion interface."""
    st.title("Lead Management")
    st.caption("View, update, and manage prospect and customer records.")

    with st.spinner("Loading leads..."):
        leads, error = get_leads()

    if error:
        st.error(error)
        return

    if not leads:
        st.info("No leads found. Add your first lead from the Add Lead page.")
        return

    table_rows = [
        {
            "Company": lead.get("company_name", ""),
            "Industry": lead.get("industry", ""),
            "Contact": lead.get("contact_name", ""),
            "Email": lead.get("email", ""),
            "Phone": lead.get("phone", ""),
            "Status": lead.get("lead_status", ""),
        }
        for lead in leads
    ]

    st.dataframe(
        pd.DataFrame(table_rows),
        use_container_width=True,
        hide_index=True,
    )

    lead_ids = [
        lead["lead_id"]
        for lead in leads
        if isinstance(lead.get("lead_id"), int)
    ]

    if not lead_ids:
        st.error("No valid lead IDs were returned by the backend.")
        return

    selected_lead_id = st.selectbox(
        "Select a lead",
        options=lead_ids,
        format_func=lambda lead_id: next(
            (
                f"{lead['company_name']} — {lead['contact_name']}"
                for lead in leads
                if lead["lead_id"] == lead_id
            ),
            str(lead_id),
        ),
    )

    selected_lead = next(
        lead for lead in leads if lead["lead_id"] == selected_lead_id
    )

    view_column, update_column, delete_column = st.columns(3)

    with view_column:
        if st.button("View", use_container_width=True):
            st.session_state["view_lead_id"] = selected_lead_id

    with update_column:
        if st.button("Update", use_container_width=True):
            st.session_state["edit_lead_id"] = selected_lead_id

    with delete_column:
        if st.button("Delete", type="primary", use_container_width=True):
            _, delete_error = api_request(
                "DELETE",
                f"/leads/{selected_lead_id}",
            )

            if delete_error:
                st.error(delete_error)
            else:
                st.success("Lead deleted successfully.")
                st.session_state.pop("view_lead_id", None)
                st.session_state.pop("edit_lead_id", None)
                st.rerun()

    if st.session_state.get("view_lead_id") == selected_lead_id:
        st.subheader("Lead Details")
        badge_html = status_badge(selected_lead.get("lead_status", ""))
        st.markdown(
            f"""
            <div class="sg-metric-card" style="--accent: var(--cyan)">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                    <div>
                        <div class="sg-metric-label">Company</div>
                        <div style="font-family:'Sora',sans-serif; font-weight:700; font-size:1.3rem; color: var(--text) !important;">{selected_lead.get('company_name', '-')}</div>
                    </div>
                    {badge_html}
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px;">
                    <div><div class="sg-metric-label">Industry</div><div style="color: var(--text) !important;">{selected_lead.get('industry', '-')}</div></div>
                    <div><div class="sg-metric-label">Contact</div><div style="color: var(--text) !important;">{selected_lead.get('contact_name', '-')}</div></div>
                    <div><div class="sg-metric-label">Email</div><div style="color: var(--text) !important;">{selected_lead.get('email', '-')}</div></div>
                    <div><div class="sg-metric-label">Phone</div><div style="color: var(--text) !important;">{selected_lead.get('phone', '-')}</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.get("edit_lead_id") == selected_lead_id:
        st.subheader("Update Lead")

        with st.form(f"update_lead_form_{selected_lead_id}"):
            company_name = st.text_input(
                "Company Name",
                value=selected_lead.get("company_name", ""),
            )
            industry = st.text_input(
                "Industry",
                value=selected_lead.get("industry", ""),
            )
            contact_name = st.text_input(
                "Contact Name",
                value=selected_lead.get("contact_name", ""),
            )
            email = st.text_input(
                "Email",
                value=selected_lead.get("email", ""),
            )
            phone = st.text_input(
                "Phone",
                value=selected_lead.get("phone", ""),
            )
            lead_status = st.text_input(
                "Lead Status",
                value=selected_lead.get("lead_status", ""),
            )

            update_submitted = st.form_submit_button("Save Changes")

        if update_submitted:
            payload = {
                "company_name": company_name,
                "industry": industry,
                "contact_name": contact_name,
                "email": email,
                "phone": phone,
                "lead_status": lead_status,
            }

            with st.spinner("Updating lead..."):
                _, update_error = api_request(
                    "PUT",
                    f"/leads/{selected_lead_id}",
                    payload,
                )

            if update_error:
                st.error(update_error)
            else:
                st.success("Lead updated successfully.")
                st.session_state.pop("edit_lead_id", None)
                st.rerun()


def render_add_lead() -> None:
    """Render the form for creating a new lead."""
    st.title("Add Lead")
    st.caption("Create a new prospect or customer record.")

    with st.form("add_lead_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        industry = st.text_input("Industry")
        contact_name = st.text_input("Contact Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        lead_status = st.text_input("Lead Status")

        submitted = st.form_submit_button("Save Lead")

    if not submitted:
        return

    payload = {
        "company_name": company_name,
        "industry": industry,
        "contact_name": contact_name,
        "email": email,
        "phone": phone,
        "lead_status": lead_status,
    }

    with st.spinner("Saving lead..."):
        _, error = api_request("POST", "/leads", payload)

    if error:
        st.error(error)
    else:
        st.success("Lead saved successfully.")


def render_sales_interactions() -> None:
    """Render the interaction history and creation interface."""
    st.title("Sales Interactions")
    st.caption("View engagement history and add interactions for a lead.")

    with st.spinner("Loading leads..."):
        leads, error = get_leads()

    if error:
        st.error(error)
        return

    if not leads:
        st.info("Add a lead before recording sales interactions.")
        return

    lead_ids = [
        lead["lead_id"]
        for lead in leads
        if isinstance(lead.get("lead_id"), int)
    ]

    selected_lead_id = st.selectbox(
        "Select Lead",
        options=lead_ids,
        format_func=lambda lead_id: next(
            (
                f"{lead['company_name']} — {lead['contact_name']}"
                for lead in leads
                if lead["lead_id"] == lead_id
            ),
            str(lead_id),
        ),
    )

    with st.spinner("Loading interaction history..."):
        interactions, interaction_error = get_interactions(selected_lead_id)

    st.subheader("Interaction History")

    if interaction_error:
        st.error(interaction_error)
    elif not interactions:
        st.info("No interactions recorded for this lead.")
    else:
        interaction_table = pd.DataFrame(
            [
                {
                    "Type": interaction.get("interaction_type", ""),
                    "Summary": interaction.get("summary", ""),
                    "Action Items": interaction.get("action_items", ""),
                    "Date": interaction.get("interaction_date", ""),
                }
                for interaction in interactions
            ]
        )
        st.dataframe(
            interaction_table,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Add New Interaction")

    with st.form(f"add_interaction_form_{selected_lead_id}", clear_on_submit=True):
        interaction_type = st.text_input("Interaction Type")
        summary = st.text_area("Summary")
        action_items = st.text_area("Action Items")
        interaction_date = st.date_input("Interaction Date")

        submitted = st.form_submit_button("Save Interaction")

    if not submitted:
        return

    interaction_timestamp = datetime.combine(
        interaction_date,
        time.min,
        tzinfo=timezone.utc,
    ).isoformat()

    payload = {
        "interaction_type": interaction_type,
        "summary": summary,
        "action_items": action_items,
        "interaction_date": interaction_timestamp,
    }

    with st.spinner("Saving interaction..."):
        _, save_error = api_request(
            "POST",
            f"/leads/{selected_lead_id}/interactions",
            payload,
        )

    if save_error:
        st.error(save_error)
    else:
        st.success("Sales interaction saved successfully.")
        st.rerun()


def render_lead_intelligence() -> None:
    """Render the AI lead analysis interface (Module 2)."""
    st.title("Lead Intelligence")
    st.caption("Run AI analysis on a lead to surface business needs, opportunities, and a qualification score.")

    with st.spinner("Loading leads..."):
        leads, error = get_leads()

    if error:
        st.error(error)
        return

    if not leads:
        st.info("Add a lead before running intelligence analysis.")
        return

    lead_ids = [
        lead["lead_id"]
        for lead in leads
        if isinstance(lead.get("lead_id"), int)
    ]

    selected_lead_id = st.selectbox(
        "Select Lead",
        options=lead_ids,
        format_func=lambda lead_id: next(
            (
                f"{lead['company_name']} — {lead['industry']}"
                for lead in leads
                if lead["lead_id"] == lead_id
            ),
            str(lead_id),
        ),
    )

    if st.button("Analyze Company", type="primary"):
        with st.spinner("Running AI analysis..."):
            _, analyze_error = api_request(
                "POST", f"/leads/{selected_lead_id}/analyze"
            )
        if analyze_error:
            st.error(analyze_error)
        else:
            st.success("Analysis complete.")
            st.rerun()

    st.subheader("Latest Insight")

    with st.spinner("Loading insights..."):
        insights, insight_error = get_insights(selected_lead_id)

    if insight_error:
        st.error(insight_error)
        return

    if not insights:
        st.info("No analysis yet for this lead. Click 'Analyze Company' above.")
        return

    latest = insights[0]
    score = latest.get("qualification_score", 0)
    score_color = "emerald" if score >= 70 else "amber" if score >= 40 else "coral"

    st.markdown(
        f"""
        <div class="sg-score-wrap">
            <div>
                <div class="sg-score-label">Qualification Score</div>
                <div class="sg-score-number" style="color: var(--{score_color}) !important;">{score}<span style="font-size:1.3rem; color: var(--text-mute) !important;">/100</span></div>
            </div>
            <div style="flex:1; height:10px; background-color: var(--surface-2); border-radius:999px; overflow:hidden; border: 1px solid var(--border);">
                <div style="width:{score}%; height:100%; background: linear-gradient(90deg, var(--cyan), var(--{score_color}));"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="sg-insight-block" style="--accent: var(--cyan)">'
        f'<div class="sg-insight-title">Business Needs</div>'
        f'<div class="sg-insight-text">{latest.get("business_needs", "-")}</div>'
        f"</div>"
        f'<div class="sg-insight-block" style="--accent: var(--emerald)">'
        f'<div class="sg-insight-title">Opportunities</div>'
        f'<div class="sg-insight-text">{latest.get("opportunities", "-")}</div>'
        f"</div>"
        f'<div class="sg-insight-block" style="--accent: var(--violet)">'
        f'<div class="sg-insight-title">Industry Analysis</div>'
        f'<div class="sg-insight-text">{latest.get("industry_analysis", "-")}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(insights) > 1:
        with st.expander(f"View {len(insights) - 1} earlier analysis run(s)"):
            history_table = pd.DataFrame(
                [
                    {
                        "Score": i.get("qualification_score", ""),
                        "Business Needs": i.get("business_needs", ""),
                        "Generated At": i.get("generated_at", ""),
                    }
                    for i in insights[1:]
                ]
            )
            st.dataframe(history_table, use_container_width=True, hide_index=True)


with st.sidebar:
    st.title("SalesGenie AI")
    st.caption("Lead Management Platform")
    page = st.radio(
        "Navigation",
        options=[
            "Dashboard",
            "Lead Management",
            "Add Lead",
            "Lead Intelligence",
            "Sales Interactions",
        ],
    )

if page == "Dashboard":
    render_dashboard()
elif page == "Lead Management":
    render_lead_management()
elif page == "Add Lead":
    render_add_lead()
elif page == "Lead Intelligence":
    render_lead_intelligence()
else:
    render_sales_interactions()
