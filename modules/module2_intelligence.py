"""
modules/module2_intelligence.py

MODULE 2: Lead Intelligence & Company Analysis

Analyzes an existing lead (created via Module 1) using Groq's LLM API
and stores the result: business needs, opportunities, industry
analysis, and a qualification score (0-100).
"""

from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from groq import Groq
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import CompanyInsight, Lead

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_NAME = "llama-3.3-70b-versatile"

router = APIRouter(prefix="/leads", tags=["Lead Intelligence"])


PROMPT_TEMPLATE = """You are a B2B sales intelligence analyst. Analyze the \
following company as a potential sales lead and respond with ONLY a raw \
JSON object (no markdown fences, no extra text) in exactly this shape:

{{
  "business_needs": "2-3 sentences on likely pain points/needs this company has",
  "opportunities": "2-3 sentences on how our product/service could help them",
  "industry_analysis": "2-3 sentences on relevant trends in their industry",
  "qualification_score": <integer 0-100, how promising this lead is>
}}

Company name: {company_name}
Industry: {industry}
Lead status: {lead_status}
"""


def _call_groq(lead: Lead) -> dict:
    if not _client:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://console.groq.com/keys"
        )

    prompt = PROMPT_TEMPLATE.format(
        company_name=lead.company_name,
        industry=lead.industry,
        lead_status=lead.lead_status,
    )

    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.choices[0].message.content.strip()

    # Groq sometimes wraps JSON in ```json ... ``` even when told not to
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse AI response as JSON: {raw_text}") from e

    required_keys = {"business_needs", "opportunities", "industry_analysis", "qualification_score"}
    if not required_keys.issubset(data.keys()):
        raise ValueError(f"AI response missing required fields: {data}")

    data["qualification_score"] = max(0, min(100, int(data["qualification_score"])))
    return data


def analyze_lead(db: Session, lead_id: int) -> CompanyInsight:
    """Fetches a lead, runs AI analysis via Groq, saves and returns the insight."""
    lead = db.get(Lead, lead_id)
    if not lead:
        raise ValueError(f"No lead found with lead_id={lead_id}")

    result = _call_groq(lead)

    insight = CompanyInsight(
        lead_id=lead.lead_id,
        business_needs=result["business_needs"],
        opportunities=result["opportunities"],
        industry_analysis=result["industry_analysis"],
        qualification_score=result["qualification_score"],
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


# ---------------------------------------------------------------------
# Pydantic schemas (matches Module 1's ConfigDict / Field style)
# ---------------------------------------------------------------------

class InsightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insight_id: int
    lead_id: int
    business_needs: str
    opportunities: str
    industry_analysis: str
    qualification_score: int = Field(ge=0, le=100)


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@router.post(
    "/{lead_id}/analyze",
    response_model=InsightRead,
    status_code=status.HTTP_201_CREATED,
)
def analyze_lead_endpoint(lead_id: int, db: Session = Depends(get_db)) -> CompanyInsight:
    """Runs AI analysis on a lead and stores the resulting insight."""
    try:
        return analyze_lead(db, lead_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{lead_id}/insights", response_model=list[InsightRead])
def get_insights_endpoint(lead_id: int, db: Session = Depends(get_db)) -> list[CompanyInsight]:
    """Returns all previously generated insights for a lead."""
    insights = (
        db.query(CompanyInsight)
        .filter(CompanyInsight.lead_id == lead_id)
        .order_by(CompanyInsight.generated_at.desc())
        .all()
    )
    if not insights:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No insights found for this lead")
    return insights
