"""modules/module4_scoring.py — STUB (Milestone 2). Not built yet."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/status")
def status():
    return {"module": "4 - Lead Scoring & Recommendations", "status": "not built yet (Milestone 2)"}
