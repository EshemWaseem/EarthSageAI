from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import UserModel
from app.api.deps import get_optional_current_user
from app.services.investigation_service import InvestigationService
from app.providers.nasa_power import NASAPowerProvider
from app.scientific.cleaning import ScientificDataCleaner
from app.scientific.statistics import compute_descriptive_statistics
from app.scientific.trend_analysis import analyze_trend
from app.scientific.anomalies import ClimatologicalAnomalyDetector
from app.scientific.comparison import ClimatologicalVariableComparator
from app.core.rate_limiter import heavy_computation_limiter

router = APIRouter(prefix="/analysis", tags=["analysis"])

class DirectAnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    start_year: int
    end_year: int
    parameters: List[str] = ["T2M", "PRECTOTCORR"]

@router.post("/query-nasa")
async def query_nasa_data(req: DirectAnalysisRequest):
    provider = NASAPowerProvider()
    try:
        data = await provider.fetch_monthly_data(
            latitude=req.latitude,
            longitude=req.longitude,
            start_year=req.start_year,
            end_year=req.end_year,
            parameters=req.parameters
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compute-trends", dependencies=[Depends(heavy_computation_limiter)])
async def compute_direct_trends(req: DirectAnalysisRequest):
    provider = NASAPowerProvider()
    try:
        raw = await provider.fetch_monthly_data(
            latitude=req.latitude,
            longitude=req.longitude,
            start_year=req.start_year,
            end_year=req.end_year,
            parameters=req.parameters
        )

        results = {}
        for param in req.parameters:
            meta = raw["parameters"][param]
            df = ScientificDataCleaner.monthly_dict_to_dataframe(meta["series"], param)
            stats = compute_descriptive_statistics(df[param], param, meta["units"])
            trend = analyze_trend(df["date"].tolist(), df[param].tolist(), param, meta["units"], seasonal=True)
            results[param] = {
                "metadata": meta,
                "descriptive": stats,
                "trend": trend
            }

        return {
            "source": raw["source"],
            "retrieval_timestamp": raw["retrieval_timestamp"],
            "coordinates": raw["coordinates"],
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/investigations/{inv_id}/anomalies", dependencies=[Depends(heavy_computation_limiter)])
async def get_investigation_anomalies(
    inv_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """
    Detects climatological monthly departures (Z >= 2.0 sigma) from long-term baselines.
    """
    svc = InvestigationService(db)
    inv = svc.get_investigation_by_id(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if inv.user_id is not None and (not current_user or inv.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to analyze investigations belonging to another researcher."
        )

    provider = NASAPowerProvider()
    raw = await provider.fetch_monthly_data(
        latitude=inv.latitude,
        longitude=inv.longitude,
        start_year=int(inv.start_year),
        end_year=int(inv.end_year),
        parameters=inv.parameters
    )

    anomalies_by_param = {}
    for param in inv.parameters:
        meta = raw["parameters"][param]
        df = ScientificDataCleaner.monthly_dict_to_dataframe(meta["series"], param)
        res = ClimatologicalAnomalyDetector.detect_monthly_anomalies(
            dates=df["date"].tolist(),
            values=df[param].tolist(),
            param_name=param,
            units=meta["units"],
            z_threshold=2.0
        )
        anomalies_by_param[param] = res

    return {
        "investigation_id": inv.id,
        "location": f"{inv.location_name}, {inv.country}",
        "coordinates": {"latitude": inv.latitude, "longitude": inv.longitude},
        "anomalies": anomalies_by_param
    }

@router.get("/investigations/{inv_id}/compare", dependencies=[Depends(heavy_computation_limiter)])
async def compare_investigation_variables(
    inv_id: str,
    param_a: str = "T2M",
    param_b: str = "PRECTOTCORR",
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """
    Performs normalized co-variation comparison and correlation testing between two parameters.
    """
    svc = InvestigationService(db)
    inv = svc.get_investigation_by_id(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if inv.user_id is not None and (not current_user or inv.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to analyze investigations belonging to another researcher."
        )

    provider = NASAPowerProvider()
    raw = await provider.fetch_monthly_data(
        latitude=inv.latitude,
        longitude=inv.longitude,
        start_year=int(inv.start_year),
        end_year=int(inv.end_year),
        parameters=[param_a, param_b]
    )

    meta_a = raw["parameters"][param_a]
    meta_b = raw["parameters"][param_b]

    df_a = ScientificDataCleaner.monthly_dict_to_dataframe(meta_a["series"], param_a)
    df_b = ScientificDataCleaner.monthly_dict_to_dataframe(meta_b["series"], param_b)

    res = ClimatologicalVariableComparator.compare_variables(
        dates_a=df_a["date"].tolist(),
        values_a=df_a[param_a].tolist(),
        param_a_name=param_a,
        units_a=meta_a["units"],
        dates_b=df_b["date"].tolist(),
        values_b=df_b[param_b].tolist(),
        param_b_name=param_b,
        units_b=meta_b["units"]
    )

    return {
        "investigation_id": inv.id,
        "location": f"{inv.location_name}, {inv.country}",
        "comparison": res
    }
