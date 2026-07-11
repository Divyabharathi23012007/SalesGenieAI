"""modules/module6_dashboard.py — STUB (Milestone 4). Not built yet."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/status")
def status():
    return {"module": "6 - Dashboard & Analytics", "status": "not built yet (Milestone 4)"}
