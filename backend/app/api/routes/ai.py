from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import UserModel
from app.api.deps import get_optional_current_user
from app.services.investigation_service import InvestigationService
from app.services.ai_service import GeminiResearchAssistant
from app.core.rate_limiter import heavy_computation_limiter

router = APIRouter(prefix="/ai", tags=["ai"])
ai_assistant = GeminiResearchAssistant()

class PlanRequest(BaseModel):
    research_question: str = Field(..., min_length=5, max_length=1000)

@router.get("/status")
def get_ai_status():
    """
    Check availability of the Gemini AI Research Assistant.
    """
    return ai_assistant.get_status()

@router.post("/plan", dependencies=[Depends(heavy_computation_limiter)])
async def plan_investigation_with_ai(payload: PlanRequest):
    """
    Formulate a scientific investigation plan from a natural-language research question.
    """
    if not payload.research_question or len(payload.research_question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Research question must be at least 5 characters.")

    plan = await ai_assistant.plan_investigation(payload.research_question)
    return plan

@router.post("/explain/{inv_id}", dependencies=[Depends(heavy_computation_limiter)])
async def explain_investigation_findings(
    inv_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """
    Generate peer-review scientific interpretation of verified empirical findings.
    Supplies the AI exclusively with genuine calculated results.
    """
    svc = InvestigationService(db)
    inv = svc.get_investigation_by_id(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation {inv_id} not found.")

    if inv.user_id is not None and (not current_user or inv.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to request AI interpretations for investigations belonging to another researcher."
        )

    if inv.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot generate interpretation for uncompleted investigation. Execute the analysis pipeline first."
        )

    summary_payload = {
        "id": inv.id,
        "title": inv.title,
        "location_name": inv.location_name,
        "country": inv.country,
        "coordinates": {"latitude": inv.latitude, "longitude": inv.longitude},
        "start_year": inv.start_year,
        "end_year": inv.end_year,
        "findings": inv.findings,
        "statistical_metrics": inv.statistical_metrics
    }

    explanation = await ai_assistant.explain_findings(summary_payload)
    return explanation

