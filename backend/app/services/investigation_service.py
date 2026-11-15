import datetime
import uuid
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.database.models import InvestigationModel
from app.providers.nasa_power import NASAPowerProvider
from app.scientific.cleaning import ScientificDataCleaner
from app.scientific.statistics import compute_descriptive_statistics
from app.scientific.trend_analysis import analyze_trend

class InvestigationService:
    def __init__(self, db: Session):
        self.db = db
        self.nasa_provider = NASAPowerProvider()

    def get_all_investigations(self, user_id: Optional[str] = None) -> List[InvestigationModel]:
        query = self.db.query(InvestigationModel)
        if user_id:
            query = query.filter((InvestigationModel.user_id == user_id) | (InvestigationModel.user_id.is_(None)))
        return query.order_by(InvestigationModel.created_at.desc()).all()

    def get_investigation_by_id(self, inv_id: str) -> Optional[InvestigationModel]:
        return self.db.query(InvestigationModel).filter(InvestigationModel.id == inv_id).first()

    def create_investigation(self, payload: Dict[str, Any], user_id: Optional[str] = None) -> InvestigationModel:
        inv_id = f"inv-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        lat = float(payload.get("latitude", 31.5497))
        lng = float(payload.get("longitude", 74.3436))
        
        model = InvestigationModel(
            id=inv_id,
            user_id=user_id,
            title=payload.get("title", "Untitled Investigation"),
            research_question=payload.get("research_question", ""),
            hypothesis=payload.get("hypothesis"),
            status="queued",
            location_name=payload.get("location_name", "Lahore"),
            region=payload.get("region", "Punjab"),
            country=payload.get("country", "Pakistan"),
            latitude=lat,
            longitude=lng,
            spatial_extent={
                "north": lat + 0.15,
                "south": lat - 0.15,
                "east": lng + 0.15,
                "west": lng - 0.15
            },
            start_year=str(payload.get("start_year", 1991)),
            end_year=str(payload.get("end_year", 2020)),
            parameters=payload.get("parameters", ["T2M", "PRECTOTCORR"]),
            dataset_ids=["nasa-power-merra2"],
            findings=[],
            time_series_data=[],
            report_available=False
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    async def run_investigation_pipeline(self, inv_id: str) -> InvestigationModel:
        inv = self.get_investigation_by_id(inv_id)
        if not inv:
            raise ValueError(f"Investigation {inv_id} not found.")

        inv.status = "running"
        self.db.commit()

        try:
            start_yr = int(inv.start_year)
            end_yr = int(inv.end_year)
            params = inv.parameters if inv.parameters else ["T2M", "PRECTOTCORR"]

            # 1. Fetch authentic data from NASA POWER Monthly API
            raw_nasa = await self.nasa_provider.fetch_monthly_data(
                latitude=inv.latitude,
                longitude=inv.longitude,
                start_year=start_yr,
                end_year=end_yr,
                parameters=params
            )

            # 2. Process each parameter with actual scientific statistical engine
            findings: List[Dict[str, Any]] = []
            combined_time_series: List[Dict[str, Any]] = []
            statistical_summary: Dict[str, Any] = {}
            aggregation_summaries: Dict[str, Any] = {}

            primary_param = "T2M" if "T2M" in params else params[0]
            successful_params = 0

            for param in params:
                param_meta = raw_nasa["parameters"][param]
                series_dict = param_meta["series"]
                df = ScientificDataCleaner.monthly_dict_to_dataframe(series_dict, param)
                
                # Assess monthly completeness
                comp_meta = ScientificDataCleaner.assess_completeness(df, param)

                # Day-weighted annual aggregation with leap year duration handling
                is_precip = (param == "PRECTOTCORR")
                agg_res = ScientificDataCleaner.compute_day_weighted_annual_aggregates(
                    df=df,
                    param_name=param,
                    is_precipitation=is_precip
                )
                aggregation_summaries[param] = {
                    "total_years": agg_res["total_years"],
                    "complete_years": agg_res["complete_years"],
                    "excluded_years": agg_res["excluded_years"],
                    "completeness_ratio": agg_res["completeness_ratio"]
                }

                # Descriptive Statistics on monthly records
                stats_res = compute_descriptive_statistics(df[param], param, param_meta["units"])
                
                # Trend Analysis (Seasonal & Day-Weighted Annual Mann-Kendall + OLS + Autocorrelation Audit)
                trend_res = analyze_trend(
                    dates=df["date"].tolist(),
                    values=df[param].tolist(),
                    param_name=param,
                    units=param_meta["units"],
                    seasonal=True
                )

                statistical_summary[param] = {
                    "descriptive": stats_res,
                    "trend": trend_res,
                    "aggregation": aggregation_summaries[param],
                    "completeness": comp_meta
                }

                # Check for calculation failure: do not generate false findings
                if trend_res.get("status") != "success":
                    continue

                successful_params += 1

                # Construct scientific finding with explicit empirical evidence
                ann_section = trend_res.get("annual_mann_kendall", {})
                ann_mk = ann_section.get("selected_result", {})
                seas_mk = trend_res.get("seasonal_mann_kendall", {})
                is_sig_ann = ann_mk.get("hypothesis_rejected", False)
                is_sig_seas = seas_mk.get("hypothesis_rejected", False)

                if is_sig_ann:
                    classification = "statistical"
                    direction = "Increasing" if ann_mk.get("sens_slope", 0) > 0 else "Decreasing"
                    finding_title = f"{param_meta['name']}: Significant {direction} Annual Trend ({start_yr}–{end_yr})"
                elif is_sig_seas:
                    classification = "statistical"
                    direction = "Increasing" if seas_mk.get("sens_slope", 0) > 0 else "Decreasing"
                    finding_title = f"{param_meta['name']}: Significant Monotonic Signal in Monthly Series ({start_yr}–{end_yr})"
                else:
                    classification = "observed"
                    finding_title = f"{param_meta['name']}: No Significant Trend Detected ({start_yr}–{end_yr})"

                # Explicit statistical measurements (no fabricated confidence scores)
                finding_obj = {
                    "id": f"f-{param}-{uuid.uuid4().hex[:4]}",
                    "title": finding_title,
                    "classification": classification,
                    "summary": trend_res["summary"],
                    "evidenceReferences": ["nasa-power-merra2"],
                    "measurements": [
                        {
                            "id": f"m-{param}-mean",
                            "label": f"Mean Monthly {param}",
                            "value": str(stats_res["mean"]),
                            "unit": param_meta["units"],
                            "uncertainty": f"±{stats_res['standard_deviation']} (1σ)",
                            "type": "observed"
                        },
                        {
                            "id": f"m-{param}-annual-slope",
                            "label": "Annual Sen's Slope",
                            "value": f"{ann_mk.get('sens_slope', 0):.4f}",
                            "unit": f"{param_meta['units']}/yr",
                            "uncertainty": f"p = {ann_mk.get('p_value', 1.0):.4f}",
                            "type": "statistical"
                        },
                        {
                            "id": f"m-{param}-annual-tau",
                            "label": "Annual Kendall's Tau",
                            "value": f"{ann_mk.get('kendall_tau', 0):.4f}",
                            "unit": "tau",
                            "uncertainty": f"N = {trend_res.get('sample_size_years', 0)} yrs",
                            "type": "statistical"
                        },
                        {
                            "id": f"m-{param}-seas-p",
                            "label": "Seasonal MK p-value",
                            "value": f"{seas_mk.get('p_value', 1.0):.4e}",
                            "unit": "prob",
                            "uncertainty": f"slope = {seas_mk.get('sens_slope', 0):.4f} {param_meta['units']}/yr",
                            "type": "statistical"
                        }
                    ]
                }
                findings.append(finding_obj)

                # Build Annual Observed Day-Weighted Aggregates for Charting
                if param == primary_param:
                    annual_df = agg_res.get("annual_df", pd.DataFrame())
                    ols = trend_res.get("linear_regression_annual", {})
                    slope = ols.get("slope_per_year", 0.0) if ols.get("status") == "success" else 0.0
                    intercept = ols.get("intercept", 0.0) if ols.get("status") == "success" else 0.0

                    if not annual_df.empty:
                        for idx, row in annual_df.iterrows():
                            yr = int(row["year"])
                            observed_val = round(float(row["day_weighted_mean"]), 2)
                            fit_val = round(float(intercept + slope * idx), 2)
                            
                            combined_time_series.append({
                                "timestamp": str(yr),
                                "observed": observed_val,
                                "predicted": fit_val,
                                "uncertaintyLower": None,
                                "uncertaintyUpper": None
                            })

            # Consistency check between parameter status and investigation status
            if successful_params == 0 and len(params) > 0:
                inv.status = "failed"
                inv.error_message = "All meteorological parameter trend evaluations failed or contained invalid data."
            else:
                inv.status = "completed"
                inv.error_message = None

            inv.findings = findings
            inv.time_series_data = combined_time_series
            inv.statistical_metrics = statistical_summary
            inv.raw_data_summary = {
                "source": raw_nasa["source"],
                "provider": raw_nasa["provider"],
                "retrieval_timestamp": raw_nasa["retrieval_timestamp"],
                "coordinates": raw_nasa["coordinates"],
                "citation": raw_nasa["citation"],
                "annual_aggregation_method": "day-weighted annual mean with leap year handling"
            }
            inv.report_available = (inv.status == "completed")
            inv.updated_at = datetime.datetime.utcnow()

            self.db.commit()
            self.db.refresh(inv)
            return inv

        except Exception as e:
            inv.status = "failed"
            inv.error_message = str(e)
            inv.updated_at = datetime.datetime.utcnow()
            self.db.commit()
            raise e
