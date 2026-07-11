"""
modules/module6_dashboard.py
Module 6 - Dashboard & Analytics

Implements backend routes to aggregate sales pipelines, segment metrics,
and retrieve top-scoring leads for the executive dashboard.
"""

import logging
from typing import Dict, List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import Lead, LeadScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("module6_dashboard")

router = APIRouter()

@router.get("/status")
def status():
    return {"module": "6 - Dashboard & Analytics", "status": "completed"}

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # 1. Total leads count
    total_leads = db.query(Lead).count()

    # 2. Segment counts
    segment_counts_raw = db.query(Lead.segment, func.count(Lead.lead_id)).group_by(Lead.segment).all()
    segment_metrics = {str(seg or "Unsegmented"): count for seg, count in segment_counts_raw}

    # 3. Stage counts
    stage_counts_raw = db.query(Lead.lead_status, func.count(Lead.lead_id)).group_by(Lead.lead_status).all()
    stage_metrics = {str(stage or "New"): count for stage, count in stage_counts_raw}

    # 4. Average score
    avg_score_raw = db.query(func.avg(LeadScore.total_score)).scalar()
    avg_score = round(float(avg_score_raw), 1) if avg_score_raw is not None else 0.0

    # 5. Top qualified prospects
    top_prospects_raw = (
        db.query(Lead, LeadScore)
        .join(LeadScore, Lead.lead_id == LeadScore.lead_id)
        .order_by(LeadScore.total_score.desc())
        .limit(5)
        .all()
    )
    
    top_prospects = []
    for lead, score in top_prospects_raw:
        top_prospects.append({
            "lead_id": lead.lead_id,
            "company_name": lead.company_name,
            "contact_name": lead.contact_name,
            "segment": lead.segment,
            "score": score.total_score,
            "strategy": score.recommended_strategy
        })

    return {
        "total_leads": total_leads,
        "segment_metrics": segment_metrics,
        "stage_metrics": stage_metrics,
        "average_lead_score": avg_score,
        "top_prospects": top_prospects
    }
