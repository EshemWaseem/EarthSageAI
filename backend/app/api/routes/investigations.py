from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import UserModel
from app.services.investigation_service import InvestigationService
from app.core.rate_limiter import heavy_computation_limiter
from app.api.deps import get_current_user, get_optional_current_user

router = APIRouter(prefix="/investigations", tags=["investigations"])

class InvestigationCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    research_question: str = Field(..., min_length=5, max_length=1000)
    hypothesis: Optional[str] = Field(None, max_length=1000)
    location_name: str = Field("Lahore", max_length=150)
    region: Optional[str] = Field("Punjab", max_length=150)
    country: str = Field("Pakistan", max_length=150)
    latitude: float = Field(31.5497, ge=-90.0, le=90.0)
    longitude: float = Field(74.3436, ge=-180.0, le=180.0)
    start_year: int = Field(1991, ge=1981, le=2024)
    end_year: int = Field(2020, ge=1981, le=2024)
    parameters: List[str] = Field(default_factory=lambda: ["T2M", "PRECTOTCORR"])

    @field_validator("end_year")
    @classmethod
    def validate_year_order(cls, v: int, info):
        start = info.data.get("start_year")
        if start is not None and v < start:
            raise ValueError("end_year must be greater than or equal to start_year")
        return v

@router.get("")
def list_investigations(
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = InvestigationService(db)
    items = service.get_all_investigations(user_id=current_user.id if current_user else None)
    
    # Format to match frontend expected schema
    res = []
    for inv in items:
        res.append({
            "id": inv.id,
            "userId": inv.user_id,
            "title": inv.title,
            "researchQuestion": inv.research_question,
            "hypothesis": inv.hypothesis,
            "status": inv.status,
            "createdAt": inv.created_at.isoformat() + "Z",
            "updatedAt": inv.updated_at.isoformat() + "Z",
            "primaryLocation": {
                "name": inv.location_name,
                "region": inv.region or "",
                "country": inv.country,
                "lat": inv.latitude,
                "lng": inv.longitude
            },
            "spatialExtent": inv.spatial_extent,
            "temporalRange": {
                "start": f"{inv.start_year}-01-01",
                "end": f"{inv.end_year}-12-31"
            },
            "datasetIds": inv.dataset_ids,
            "findings": inv.findings,
            "timeSeriesData": inv.time_series_data,
            "reportAvailable": inv.report_available,
            "errorMessage": inv.error_message
        })
    return res

@router.post("")
def create_investigation(
    payload: InvestigationCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = InvestigationService(db)
    user_id = current_user.id if current_user else None
    inv = service.create_investigation(payload.model_dump(), user_id=user_id)
    return {
        "id": inv.id,
        "userId": inv.user_id,
        "title": inv.title,
        "researchQuestion": inv.research_question,
        "hypothesis": inv.hypothesis,
        "status": inv.status,
        "createdAt": inv.created_at.isoformat() + "Z",
        "updatedAt": inv.updated_at.isoformat() + "Z",
        "primaryLocation": {
            "name": inv.location_name,
            "region": inv.region or "",
            "country": inv.country,
            "lat": inv.latitude,
            "lng": inv.longitude
        },
        "spatialExtent": inv.spatial_extent,
        "temporalRange": {
            "start": f"{inv.start_year}-01-01",
            "end": f"{inv.end_year}-12-31"
        },
        "datasetIds": inv.dataset_ids,
        "findings": inv.findings,
        "timeSeriesData": inv.time_series_data,
        "reportAvailable": inv.report_available
    }

@router.get("/{inv_id}")
def get_investigation(
    inv_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = InvestigationService(db)
    inv = service.get_investigation_by_id(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Ownership access check:
    # Baseline investigations (user_id is None) are public for all users.
    # User-created investigations can only be viewed by the owner.
    if inv.user_id is not None:
        if not current_user or current_user.id != inv.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to view this investigation."
            )
    
    return {
        "id": inv.id,
        "userId": inv.user_id,
        "title": inv.title,
        "researchQuestion": inv.research_question,
        "hypothesis": inv.hypothesis,
        "status": inv.status,
        "createdAt": inv.created_at.isoformat() + "Z",
        "updatedAt": inv.updated_at.isoformat() + "Z",
        "primaryLocation": {
            "name": inv.location_name,
            "region": inv.region or "",
            "country": inv.country,
            "lat": inv.latitude,
            "lng": inv.longitude
        },
        "spatialExtent": inv.spatial_extent,
        "temporalRange": {
            "start": f"{inv.start_year}-01-01",
            "end": f"{inv.end_year}-12-31"
        },
        "datasetIds": inv.dataset_ids,
        "findings": inv.findings,
        "timeSeriesData": inv.time_series_data,
        "reportAvailable": inv.report_available,
        "statisticalMetrics": inv.statistical_metrics,
        "rawDataSummary": inv.raw_data_summary,
        "errorMessage": inv.error_message
    }

@router.post("/{inv_id}/run", dependencies=[Depends(heavy_computation_limiter)])
async def run_investigation(
    inv_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = InvestigationService(db)
    inv = service.get_investigation_by_id(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Only owner can run user-created investigation; baseline can also be run
    if inv.user_id is not None and (not current_user or current_user.id != inv.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot execute analysis on an investigation owned by another researcher."
        )

    try:
        inv = await service.run_investigation_pipeline(inv_id)
        return {
            "id": inv.id,
            "userId": inv.user_id,
            "title": inv.title,
            "researchQuestion": inv.research_question,
            "hypothesis": inv.hypothesis,
            "status": inv.status,
            "createdAt": inv.created_at.isoformat() + "Z",
            "updatedAt": inv.updated_at.isoformat() + "Z",
            "primaryLocation": {
                "name": inv.location_name,
                "region": inv.region or "",
                "country": inv.country,
                "lat": inv.latitude,
                "lng": inv.longitude
            },
            "spatialExtent": inv.spatial_extent,
            "temporalRange": {
                "start": f"{inv.start_year}-01-01",
                "end": f"{inv.end_year}-12-31"
            },
            "datasetIds": inv.dataset_ids,
            "findings": inv.findings,
            "timeSeriesData": inv.time_series_data,
            "reportAvailable": inv.report_available,
            "statisticalMetrics": inv.statistical_metrics,
            "rawDataSummary": inv.raw_data_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

