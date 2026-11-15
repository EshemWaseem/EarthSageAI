import os
import datetime
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import ReportModel, InvestigationModel
from app.services.pdf_generator import build_investigation_pdf
from app.services.csv_generator import build_investigation_csv

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_reports(self) -> List[ReportModel]:
        return self.db.query(ReportModel).order_by(ReportModel.generated_at.desc()).all()

    def get_report_by_id(self, report_id: str) -> ReportModel:
        return self.db.query(ReportModel).filter(ReportModel.id == report_id).first()

    def generate_report(self, inv_id: str, file_format: str = "PDF", author: Optional[str] = None) -> ReportModel:
        inv = self.db.query(InvestigationModel).filter(InvestigationModel.id == inv_id).first()
        if not inv:
            raise ValueError(f"Investigation {inv_id} not found.")

        fmt = file_format.upper()
        if fmt not in ["PDF", "CSV"]:
            fmt = "PDF"

        rep_id = f"rep-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        os.makedirs("/app/data/reports", exist_ok=True)

        if fmt == "CSV":
            csv_path = f"/app/data/reports/{rep_id}.csv"
            csv_content = build_investigation_csv(inv)
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(csv_content)

            file_size_kb = round(len(csv_content.encode("utf-8")) / 1024, 1)
            summary_text = (
                f"Scientific CSV dataset export for {inv.title}. "
                f"Contains full metadata headers, {len(inv.findings)} empirical findings, and annual day-weighted time series."
            )
            content_path = csv_path
        else:
            pdf_path = f"/app/data/reports/{rep_id}.pdf"
            pdf_bytes = build_investigation_pdf(inv)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            file_size_kb = round(len(pdf_bytes) / 1024, 1)
            summary_text = (
                f"Formal scientific technical report for {inv.title}. "
                f"Contains {len(inv.findings)} verified empirical findings, NASA POWER reanalysis source metadata, "
                f"and Seasonal + Annual Mann-Kendall test parameters."
            )
            content_path = pdf_path

        report = ReportModel(
            id=rep_id,
            investigation_id=inv.id,
            title=f"Scientific Report ({fmt}): {inv.title}",
            author=author or "EarthSage Research Engine",
            file_format=fmt,
            file_size=f"{file_size_kb} KB",
            summary=summary_text,
            content=content_path,
            generated_at=datetime.datetime.utcnow()
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
