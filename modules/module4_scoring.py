"""
modules/module4_scoring.py
Module 4 - Lead Scoring & Recommendations

Implements rule-based calculation for demographic fit and behavioral engagement,
combined with an LLM-driven recommendation engine that outputs tailored B2B
sales engagement playbooks and prioritization strategies.
"""

import os
import json
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Lead, SalesInteraction, LeadScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("module4_scoring")

router = APIRouter()

# --------------------------------------------------------------------------
# LLM CLIENT INITIALIZATION
# --------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client = None
_model = None
if GROQ_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        _model = GROQ_MODEL
        logger.info(f"Module 4 using Groq ({_model})")
    except Exception as e:
        logger.warning(f"Could not init Groq client in Module 4: {e}")
elif OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
        _model = OPENAI_MODEL
        logger.info(f"Module 4 using OpenAI ({_model})")
    except Exception as e:
        logger.warning(f"Could not init OpenAI client in Module 4: {e}")

# --------------------------------------------------------------------------
# SCHEMAS
# --------------------------------------------------------------------------
class ScoringResponse(BaseModel):
    score_id: int
    lead_id: int
    demographic_score: int
    behavioral_score: int
    total_score: int
    recommended_strategy: str
    engagement_playbook: List[str]
    calculated_at: datetime

    class Config:
        from_attributes = True

# --------------------------------------------------------------------------
# RULE CALCULATIONS
# --------------------------------------------------------------------------
def calculate_demographic_score(lead: Lead) -> int:
    """Demographic score (max 50 points)."""
    score = 0

    # 1. Segment (max 20 pts)
    segment = (lead.segment or "").lower()
    if segment == "enterprise":
        score += 20
    elif segment == "mid-market":
        score += 12
    elif segment == "startup":
        score += 6
    else:
        score += 2

    # 2. Company Size (max 15 pts)
    size = (lead.company_size or "").lower()
    if "500" in size or "1000" in size:
        score += 15
    elif "250" in size or "100" in size:
        score += 10
    elif "50" in size or "10" in size:
        score += 5
    else:
        score += 2

    # 3. Tech Stack alignment (max 15 pts)
    # Target stacks show better fit for B2B data/AI SaaS platform
    fit_technologies = {"aws", "gcp", "azure", "kubernetes", "postgres", "kafka", "tensorflow", "python", "go"}
    if lead.tech_stack:
        matches = 0
        for tech in lead.tech_stack:
            if tech.lower() in fit_technologies:
                matches += 1
        score += min(15, matches * 3)
    else:
        score += 2

    return min(50, score)


def calculate_behavioral_score(interactions: List[SalesInteraction]) -> int:
    """Behavioral engagement score based on interactions history (max 50 points)."""
    if not interactions:
        return 0

    score = 0
    for interaction in interactions:
        itype = (interaction.interaction_type or "").lower()
        if itype == "meeting":
            score += 15
        elif itype == "call":
            score += 10
        elif itype == "email":
            score += 8
        elif itype == "note":
            score += 4
        else:
            score += 2

    return min(50, score)

# --------------------------------------------------------------------------
# HELPERS FOR AI GENERATION
# --------------------------------------------------------------------------
def _build_scoring_prompt(lead: Lead, demo_score: int, behav_score: int, total_score: int, interactions: List[SalesInteraction]) -> str:
    profile_lines = [
        f"Company: {lead.company_name}",
        f"Industry: {lead.industry or 'Unknown'}",
        f"Contact: {lead.contact_name or 'Unknown'} ({lead.title or 'Unknown title'})",
        f"Segment: {lead.segment or 'Unsegmented'}",
        f"Company Size: {lead.company_size or 'Unknown'}",
        f"Tech Stack: {', '.join(lead.tech_stack) if lead.tech_stack else 'Unknown'}",
        f"Computed Fit Metrics: Demographic Score={demo_score}/50, Behavioral Score={behav_score}/50, Total Score={total_score}/100",
    ]

    history_lines = []
    for idx, interact in enumerate(interactions[:5]):
        history_lines.append(f"- [{interact.interaction_date.strftime('%Y-%m-%d')}] {interact.interaction_type}: {interact.summary}")

    history_text = "\n".join(history_lines) if history_lines else "No sales interactions logged yet."

    return f"""You are a senior B2B sales development strategist. Your job is to analyze a sales prospect, verify their qualification metrics, and output a highly customized engagement playbook and recommended closing strategy.

Lead Profile:
{chr(10).join('- ' + l for l in profile_lines)}

Recent Interaction Logs:
{history_text}

Rules:
1. Provide a recommended closing strategy summary (under 15 words) like: "Direct outbound to CTO", "Nurture with tech case studies", or "Initiate trial conversation".
2. Provide an engagement playbook containing EXACTLY 3-4 specific sequential steps. Make the steps actionable and tailored to the lead's tech stack and size. Do not use generic placeholders.
3. Return ONLY valid JSON (no markdown fences) with exactly two keys: "recommended_strategy" and "engagement_playbook" (which is an array of strings).
"""


def _call_llm_for_playbook(prompt: str) -> dict:
    if _client is None:
        # Default mock response when LLM is offline
        return {
            "recommended_strategy": "Warm follow-up and platform demonstration",
            "engagement_playbook": [
                "1. Send a personalized email referencing their specific tech stack and cloud integrations.",
                "2. Schedule a 15-minute discovery call to identify core data pipeline bottlenecks.",
                "3. Provide a tailored sandbox demo showcasing database connectivity options."
            ]
        }

    try:
        completion = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": "You are a precise assistant that only outputs valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        raw = completion.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return data
    except Exception as e:
        logger.error(f"LLM call failed in scoring: {e}")
        # Fallback response
        return {
            "recommended_strategy": "Direct outbound discovery call",
            "engagement_playbook": [
                "1. Connect with the primary technical contact via LinkedIn.",
                "2. Share relevant industry case study matching their business size.",
                "3. Propose a brief introductory meeting to discuss infrastructure optimization."
            ]
        }

# --------------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------------
@router.get("/status")
def status():
    return {"module": "4 - Lead Scoring & Recommendations", "status": "completed"}


@router.post("/calculate/{lead_id}", response_model=ScoringResponse)
def calculate_lead_score(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    # 1. Fetch sales interactions to determine engagement
    interactions = (
        db.query(SalesInteraction)
        .filter(SalesInteraction.lead_id == lead_id)
        .order_by(SalesInteraction.interaction_date.desc())
        .all()
    )

    # 2. Compute Rule Scores
    demo_score = calculate_demographic_score(lead)
    behav_score = calculate_behavioral_score(interactions)
    total_score = demo_score + behav_score

    # 3. Call AI for Engagement Playbook and Strategy
    prompt = _build_scoring_prompt(lead, demo_score, behav_score, total_score, interactions)
    ai_data = _call_llm_for_playbook(prompt)

    # 4. Save or update score
    score_record = db.query(LeadScore).filter(LeadScore.lead_id == lead_id).first()
    if not score_record:
        score_record = LeadScore(lead_id=lead_id)
        db.add(score_record)

    score_record.demographic_score = demo_score
    score_record.behavioral_score = behav_score
    score_record.total_score = total_score
    score_record.recommended_strategy = ai_data.get("recommended_strategy", "Nurture lead")
    score_record.engagement_playbook = ai_data.get("engagement_playbook", [])
    score_record.calculated_at = datetime.utcnow()

    db.commit()
    db.refresh(score_record)
    return score_record


@router.get("/{lead_id}", response_model=ScoringResponse)
def get_lead_score(lead_id: int, db: Session = Depends(get_db)):
    score_record = (
        db.query(LeadScore)
        .filter(LeadScore.lead_id == lead_id)
        .order_by(LeadScore.calculated_at.desc())
        .first()
    )
    if not score_record:
        raise HTTPException(status_code=404, detail="No score calculated for this lead yet.")
    return score_record
