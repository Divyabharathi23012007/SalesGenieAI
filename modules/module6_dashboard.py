"""
modules/module6_dashboard.py
Module 6 - Dashboard & Sales Analytics

Aggregates data already produced by modules 1-5 into the KPIs, pipeline
view, and follow-up recommendation feed shown on the Dashboard tab. This
module does not call the LLM directly — it reads what modules 2-5 already
generated and computes on top of it (rule-based), so it always returns
instantly and works even without an LLM key configured.

Mounted in main.py as:
    app.include_router(dashboard_router, prefix="/dashboard", tags=["Module 6 - Dashboard"])
"""

import logging
from typing import Optional, List, Dict
from collections import defaultdict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Lead, LeadScore, OutreachCampaign, CompanyInsight, SalesInteraction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("module6_dashboard")

router = APIRouter()

PIPELINE_STAGES = ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
CLOSED_WON = "Closed Won"
CLOSED_LOST = "Closed Lost"


# --------------------------------------------------------------------------
# SCHEMAS
# --------------------------------------------------------------------------
class OverviewOut(BaseModel):
    total_leads: int
    conversion_rate: float          # % of leads that are Closed Won
    pipeline_value: int             # sum of deal_value for open (not closed) leads
    total_pipeline_value: int       # sum of deal_value across all leads
    avg_qualification_score: Optional[float] = None
    avg_lead_score: Optional[float] = None
    campaigns_sent: int
    campaigns_draft: int
    interactions_logged: int
    leads_by_stage: Dict[str, int]


class PipelineLeadOut(BaseModel):
    lead_id: int
    company_name: str
    deal_value: Optional[int] = None
    score: Optional[int] = None
    classification: Optional[str] = None


class PipelineOut(BaseModel):
    stages: List[str]
    columns: Dict[str, List[PipelineLeadOut]]


class FollowUpOut(BaseModel):
    lead_id: int
    company_name: str
    lead_status: Optional[str] = None
    score: Optional[int] = None
    classification: Optional[str] = None
    reason: str
    priority: str  # High | Medium | Low


# --------------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------------
@router.get("/status")
def status():
    return {"module": "6 - Dashboard & Analytics", "status": "fully operational"}


@router.get("/overview", response_model=OverviewOut)
def overview(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    total_leads = len(leads)

    closed_won = sum(1 for l in leads if l.lead_status == CLOSED_WON)
    conversion_rate = round((closed_won / total_leads) * 100, 1) if total_leads else 0.0

    open_leads = [l for l in leads if l.lead_status not in (CLOSED_WON, CLOSED_LOST)]
    pipeline_value = sum(l.deal_value or 0 for l in open_leads)
    total_pipeline_value = sum(l.deal_value or 0 for l in leads)

    leads_by_stage = {stage: 0 for stage in PIPELINE_STAGES}
    for l in leads:
        stage = l.lead_status if l.lead_status in leads_by_stage else "New"
        leads_by_stage[stage] += 1

    insight_scores = [i.qualification_score for i in db.query(CompanyInsight).all() if i.qualification_score is not None]
    avg_qual = round(sum(insight_scores) / len(insight_scores), 1) if insight_scores else None

    lead_scores = [s.score for s in db.query(LeadScore).all() if s.score is not None]
    avg_score = round(sum(lead_scores) / len(lead_scores), 1) if lead_scores else None

    campaigns = db.query(OutreachCampaign).all()
    campaigns_sent = sum(1 for c in campaigns if c.campaign_status == "sent")
    campaigns_draft = sum(1 for c in campaigns if c.campaign_status == "draft")

    interactions_logged = db.query(SalesInteraction).count()

    return OverviewOut(
        total_leads=total_leads,
        conversion_rate=conversion_rate,
        pipeline_value=pipeline_value,
        total_pipeline_value=total_pipeline_value,
        avg_qualification_score=avg_qual,
        avg_lead_score=avg_score,
        campaigns_sent=campaigns_sent,
        campaigns_draft=campaigns_draft,
        interactions_logged=interactions_logged,
        leads_by_stage=leads_by_stage,
    )


@router.get("/pipeline", response_model=PipelineOut)
def pipeline(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    scores_by_lead = {s.lead_id: s for s in db.query(LeadScore).all()}

    columns: Dict[str, List[PipelineLeadOut]] = {stage: [] for stage in PIPELINE_STAGES}
    for l in leads:
        stage = l.lead_status if l.lead_status in columns else "New"
        score_rec = scores_by_lead.get(l.lead_id)
        columns[stage].append(PipelineLeadOut(
            lead_id=l.lead_id,
            company_name=l.company_name,
            deal_value=l.deal_value,
            score=score_rec.score if score_rec else None,
            classification=score_rec.classification if score_rec else None,
        ))

    for stage in columns:
        columns[stage].sort(key=lambda x: x.score or 0, reverse=True)

    return PipelineOut(stages=PIPELINE_STAGES, columns=columns)


@router.get("/followups", response_model=List[FollowUpOut])
def followups(db: Session = Depends(get_db)):
    """
    Rule-based automated follow-up feed: surfaces leads that look high-value
    but are at risk of going stale — no LLM call, so this always returns
    instantly. Reuses whatever Module 4 already scored and Module 1's
    interaction log, rather than generating anything new.
    """
    leads = db.query(Lead).filter(~Lead.lead_status.in_([CLOSED_WON, CLOSED_LOST])).all()
    scores_by_lead = {s.lead_id: s for s in db.query(LeadScore).all()}
    interaction_counts = defaultdict(int)
    for i in db.query(SalesInteraction).all():
        interaction_counts[i.lead_id] += 1

    results: List[FollowUpOut] = []
    for l in leads:
        score_rec = scores_by_lead.get(l.lead_id)
        score = score_rec.score if score_rec else None
        classification = score_rec.classification if score_rec else None
        touches = interaction_counts.get(l.lead_id, 0)

        if score is not None and score >= 80 and touches == 0:
            reason = f"Scored {score} ({classification}) but has zero logged interactions — reach out now."
            priority = "High"
        elif score is not None and score >= 65 and l.lead_status in ("New", "Contacted"):
            reason = f"Scored {score} ({classification}) and still early-stage ({l.lead_status}) — move it forward."
            priority = "Medium"
        elif score is None:
            reason = "No score generated yet — run Lead Scoring to prioritize this lead."
            priority = "Low"
        else:
            continue  # not follow-up-worthy right now

        results.append(FollowUpOut(
            lead_id=l.lead_id,
            company_name=l.company_name,
            lead_status=l.lead_status,
            score=score,
            classification=classification,
            reason=reason,
            priority=priority,
        ))

    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    results.sort(key=lambda r: (priority_rank.get(r.priority, 3), -(r.score or 0)))
    return results[:10]
