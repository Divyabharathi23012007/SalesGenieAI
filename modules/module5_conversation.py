"""
modules/module5_conversation.py
Module 5 - Conversation Intelligence & CRM Integration

Two responsibilities:
1. CRM sync: push a lead's current profile to a chosen CRM platform and log
   the result. This project doesn't hold real Salesforce/HubSpot credentials,
   so the sync is simulated — it produces the same audit trail (CRMSyncLog
   rows) a real integration would, without an actual outbound API call.
2. Conversation intelligence: given a raw call/meeting transcript, use the
   LLM to extract a summary and action items, and save it as a
   SalesInteraction (same table Module 1 uses for manually-logged
   interactions, flagged ai_generated=1 here).

Mounted in main.py as:
    app.include_router(conversation_router, prefix="/conversation", tags=["Module 5 - Conversation"])
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Lead, SalesInteraction, CRMSyncLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("module5_conversation")

router = APIRouter()

# --------------------------------------------------------------------------
# LLM CLIENT SETUP — same Groq/OpenAI pattern as modules 2-4.
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
        logger.info(f"Module 5 using Groq ({_model})")
    except Exception as e:  # pragma: no cover
        logger.warning(f"Could not init Groq client: {e}")
elif OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
        _model = OPENAI_MODEL
        logger.info(f"Module 5 using OpenAI ({_model})")
    except Exception as e:  # pragma: no cover
        logger.warning(f"Could not init OpenAI client: {e}")

CRM_PLATFORMS = ["Salesforce", "HubSpot"]


# --------------------------------------------------------------------------
# SCHEMAS
# --------------------------------------------------------------------------
class SyncRequest(BaseModel):
    crm_platform: str = "Salesforce"  # Salesforce | HubSpot


class SyncLogOut(BaseModel):
    sync_id: int
    lead_id: int
    crm_platform: str
    sync_status: str
    detail: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class SummarizeRequest(BaseModel):
    lead_id: int
    transcript: str
    interaction_type: str = "Meeting"  # Call | Meeting


class SummaryOut(BaseModel):
    interaction_id: int
    lead_id: int
    interaction_type: str
    summary: Optional[str] = None
    action_items: Optional[str] = None
    ai_generated: Optional[int] = None
    interaction_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------
def _build_summary_prompt(lead: Lead, transcript: str, interaction_type: str) -> str:
    return f"""You are a sales operations assistant. Summarize this {interaction_type.lower()}
transcript between a sales rep and a prospect at {lead.company_name}.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON (no markdown fences) with exactly two keys:
- "summary": a 2-4 sentence summary of what was discussed.
- "action_items": a short bullet list (as a single string, lines separated by
  " | ") of concrete follow-up action items with an owner where mentioned.
"""


def _call_llm_for_summary(prompt: str) -> dict:
    if _client is None:
        raise HTTPException(
            status_code=503,
            detail="LLM not configured. Set GROQ_API_KEY or OPENAI_API_KEY in your .env file.",
        )
    try:
        completion = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": "You are a precise assistant that only outputs valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        raw = completion.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"LLM returned non-JSON: {raw!r}")
        raise HTTPException(status_code=502, detail="AI returned an unexpected format. Please try again.")
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI generation failed: {e}")


# --------------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------------
@router.get("/status")
def status():
    return {"module": "5 - Conversation Intelligence & CRM", "status": "fully operational"}


@router.get("/health")
def health():
    return {"status": "ok", "llm_configured": _client is not None}


@router.get("/crm-platforms")
def crm_platforms():
    return {"platforms": CRM_PLATFORMS}


# ---- CRM Sync ----
@router.post("/sync/{lead_id}", response_model=SyncLogOut)
def sync_lead(lead_id: int, req: SyncRequest, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    platform = req.crm_platform if req.crm_platform in CRM_PLATFORMS else "Salesforce"
    log = CRMSyncLog(
        lead_id=lead_id,
        crm_platform=platform,
        sync_status="Synced",
        detail=f"Contact '{lead.contact_name or lead.company_name}' and deal stage "
               f"'{lead.lead_status}' pushed to {platform}.",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/sync/logs/{lead_id}", response_model=List[SyncLogOut])
def sync_logs_for_lead(lead_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CRMSyncLog)
        .filter(CRMSyncLog.lead_id == lead_id)
        .order_by(CRMSyncLog.timestamp.desc())
        .all()
    )


@router.get("/sync/logs", response_model=List[SyncLogOut])
def recent_sync_logs(db: Session = Depends(get_db)):
    """Most recent sync activity across all leads, for the Conversations dashboard panel."""
    return (
        db.query(CRMSyncLog)
        .order_by(CRMSyncLog.timestamp.desc())
        .limit(20)
        .all()
    )


# ---- Conversation Intelligence ----
@router.post("/summarize", response_model=SummaryOut)
def summarize_conversation(req: SummarizeRequest, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == req.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    if not req.transcript.strip():
        raise HTTPException(status_code=422, detail="Transcript cannot be empty.")

    prompt = _build_summary_prompt(lead, req.transcript, req.interaction_type)
    data = _call_llm_for_summary(prompt)

    interaction = SalesInteraction(
        lead_id=req.lead_id,
        interaction_type=req.interaction_type,
        summary=data.get("summary"),
        action_items=data.get("action_items"),
        ai_generated=1,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/summaries/{lead_id}", response_model=List[SummaryOut])
def list_summaries(lead_id: int, db: Session = Depends(get_db)):
    """AI-generated conversation summaries only (excludes manually-logged Module 1 notes)."""
    return (
        db.query(SalesInteraction)
        .filter(SalesInteraction.lead_id == lead_id, SalesInteraction.ai_generated == 1)
        .order_by(SalesInteraction.interaction_date.desc())
        .all()
    )
