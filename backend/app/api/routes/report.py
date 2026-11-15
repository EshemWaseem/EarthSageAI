import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import UserModel, InvestigationModel
from app.services.report_service import ReportService
from app.services.investigation_service import InvestigationService
from app.services.pdf_generator import build_investigation_pdf
from app.services.csv_generator import build_investigation_csv
from app.core.rate_limiter import report_generation_limiter
from app.api.deps import get_current_user, get_optional_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportGenerateRequest(BaseModel):
    investigation_id: str = Field(..., min_length=3, max_length=100)
    file_format: str = Field("PDF", max_length=10)

    @field_validator("file_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        fmt = v.strip().upper()
        if fmt not in ("PDF", "CSV", "GEOJSON"):
            raise ValueError("Supported report formats are 'PDF', 'CSV', and 'GEOJSON'")
        return fmt

@router.get("")
def list_reports(
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = ReportService(db)
    items = service.get_all_reports()
    
    # Filter reports if current_user is authenticated: include baseline + user's investigations
    if current_user:
        user_inv_ids = {
            inv.id for inv in db.query(InvestigationModel.id).filter(
                (InvestigationModel.user_id == current_user.id) | (InvestigationModel.user_id.is_(None))
            ).all()
        }
        items = [r for r in items if r.investigation_id in user_inv_ids]
    else:
        # Unauthenticated: only reports for baseline investigations (user_id is None)
        baseline_inv_ids = {
            inv.id for inv in db.query(InvestigationModel.id).filter(
                InvestigationModel.user_id.is_(None)
            ).all()
        }
        items = [r for r in items if r.investigation_id in baseline_inv_ids]

    return [
        {
            "id": r.id,
            "investigationId": r.investigation_id,
            "title": r.title,
            "author": r.author,
            "generatedAt": r.generated_at.isoformat() + "Z",
            "fileFormat": r.file_format,
            "fileSize": r.file_size,
            "summary": r.summary,
            "downloadUrl": f"/api/v1/reports/{r.id}/download"
        }
        for r in items
    ]

@router.post("", dependencies=[Depends(report_generation_limiter)])
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    # Verify access to the target investigation
    inv = db.query(InvestigationModel).filter(InvestigationModel.id == payload.investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if inv.user_id is not None and (not current_user or inv.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot generate reports for investigations owned by another researcher."
        )

    service = ReportService(db)
    author_name = current_user.full_name if current_user else "EarthSage Research Engine"
    try:
        report = service.generate_report(
            inv_id=payload.investigation_id,
            file_format=payload.file_format,
            author=author_name
        )
        return {
            "id": report.id,
            "investigationId": report.investigation_id,
            "title": report.title,
            "author": report.author,
            "generatedAt": report.generated_at.isoformat() + "Z",
            "fileFormat": report.file_format,
            "fileSize": report.file_size,
            "summary": report.summary,
            "downloadUrl": f"/api/v1/reports/{report.id}/download"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    service = ReportService(db)
    report = service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Ownership and authorization check for underlying investigation
    inv = db.query(InvestigationModel).filter(InvestigationModel.id == report.investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Underlying investigation not found")

    if inv.user_id is not None and (not current_user or inv.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to download reports belonging to another researcher."
        )
    
    fmt = (report.file_format or "PDF").upper()
    ext = "csv" if fmt == "CSV" else "pdf"
    media_type = "text/csv" if fmt == "CSV" else "application/pdf"

    file_path = report.content
    if file_path:
        # Prevent path traversal: ensure target is within allowed storage directories
        abs_path = os.path.abspath(file_path)
        allowed_dir = os.path.abspath("/app/data/reports")
        if abs_path.startswith(allowed_dir) and os.path.exists(abs_path):
            return FileResponse(
                path=abs_path,
                filename=f"{report.id}.{ext}",
                media_type=media_type
            )
    
    # If file was not written to disk, generate on the fly
    inv_svc = InvestigationService(db)
    inv = inv_svc.get_investigation_by_id(report.investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Underlying investigation not found")
    
    if fmt == "CSV":
        csv_str = build_investigation_csv(inv)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report.id}.csv"}
        )
    else:
        pdf_bytes = build_investigation_pdf(inv)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report.id}.pdf"}
        )
