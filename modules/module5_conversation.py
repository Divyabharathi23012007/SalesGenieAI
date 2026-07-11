"""modules/module5_conversation.py — STUB (Milestone 3). Not built yet."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/status")
def status():
    return {"module": "5 - Conversation Intelligence & CRM", "status": "not built yet (Milestone 3)"}
