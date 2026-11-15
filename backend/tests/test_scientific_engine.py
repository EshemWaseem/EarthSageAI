"""
Comprehensive Automated Test Suite for EarthSage AI Scientific Statistical Engine.
Covers:
1. Complete 12-month years validation
2. Missing months detection & year exclusion
3. Duplicate months detection
4. Leap years handling (Feb 29 vs 28 day weighting)
5. Day-weighted annual temperature calculation
6. Day-weighted annual precipitation rate (mm/day) & accumulation (mm/year)
7. Constant time series handling (zero variance)
8. Missing values (-999, NaN) handling
9. Autocorrelated annual series testing (statsmodels acorr_ljungbox)
10. Non-significant annual trend handling
11. Seasonal trend evaluation (Hirsch-Slack)
12. Correct Sen's slope units ({units}/yr)
13. PDF generation with special characters (&, <, >, ", ')
14. Failed statistical calculation handling (no silent fallbacks)
"""
import pytest
import datetime
import calendar
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

from app.scientific.cleaning import ScientificDataCleaner
from app.scientific.trend_analysis import analyze_trend, _perform_autocorrelation_audit
from app.services.pdf_generator import build_investigation_pdf, _esc
from app.database.models import InvestigationModel

# ---------------------------------------------------------
# 1. Complete 12-Month Years & Calendar Completeness
# ---------------------------------------------------------
def test_complete_12_month_years():
    """Verify clean 12-month series is detected as complete."""
    series = {}
    for yr in range(2000, 2010):
        for m in range(1, 13):
            series[f"{yr}{m:02d}"] = 20.0 + (m % 3)
    
    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "T2M")
    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "T2M")
    
    assert agg["total_years"] == 10
    assert agg["complete_years"] == 10
    assert len(agg["excluded_years"]) == 0
    assert agg["is_complete"] is True
    assert len(agg["annual_df"]) == 10

# ---------------------------------------------------------
# 2. Missing Months Detection & Year Exclusion
# ---------------------------------------------------------
def test_missing_months_detection():
    """Verify years missing any month (e.g. 11 months) are excluded from annual series."""
    series = {}
    # Year 2000 has only 11 months (missing December)
    for m in range(1, 12):
        series[f"2000{m:02d}"] = 22.0
    # Year 2001 has all 12 months
    for m in range(1, 13):
        series[f"2001{m:02d}"] = 23.0

    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "T2M")
    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "T2M")

    assert agg["total_years"] == 2
    assert agg["complete_years"] == 1
    assert len(agg["excluded_years"]) == 1
    assert agg["excluded_years"][0]["year"] == 2000
    assert "missing month(s)" in agg["excluded_years"][0]["reason"]
    assert len(agg["annual_df"]) == 1
    assert agg["annual_df"].iloc[0]["year"] == 2001

# ---------------------------------------------------------
# 3. Duplicate Months Detection
# ---------------------------------------------------------
def test_duplicate_months_detection():
    """Verify duplicate records for the same month cause year exclusion."""
    df = pd.DataFrame([
        {"date": "2005-01-01", "year": 2005, "month": 1, "T2M": 10.0},
        {"date": "2005-01-01", "year": 2005, "month": 1, "T2M": 12.0}, # duplicate month 1
    ] + [
        {"date": f"2005-{m:02d}-01", "year": 2005, "month": m, "T2M": 20.0} for m in range(2, 13)
    ])
    df["date"] = pd.to_datetime(df["date"])

    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "T2M")
    assert agg["complete_years"] == 0
    assert len(agg["excluded_years"]) == 1
    assert "Duplicate monthly observations" in agg["excluded_years"][0]["reason"]

# ---------------------------------------------------------
# 4. Leap Years Handling (Feb 29 vs 28 Days)
# ---------------------------------------------------------
def test_leap_years_handling():
    """Verify leap year 2000 (366 days, Feb=29) vs standard year 2001 (365 days, Feb=28)."""
    series = {}
    # Year 2000 (leap year)
    for m in range(1, 13):
        series[f"2000{m:02d}"] = 10.0 if m == 2 else 20.0
    # Year 2001 (standard year)
    for m in range(1, 13):
        series[f"2001{m:02d}"] = 10.0 if m == 2 else 20.0

    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "T2M")
    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "T2M")
    annual_df = agg["annual_df"]

    y2000 = annual_df[annual_df["year"] == 2000].iloc[0]
    y2001 = annual_df[annual_df["year"] == 2001].iloc[0]

    assert bool(y2000["is_leap_year"]) is True
    assert y2000["days_in_year"] == 366

    assert bool(y2001["is_leap_year"]) is False
    assert y2001["days_in_year"] == 365

    # Day-weight formula: (10 * 29 + 20 * 337) / 366 = (290 + 6740)/366 = 7030/366 = 19.20765
    expected_2000 = round((10.0 * 29 + 20.0 * 337) / 366.0, 4)
    # Day-weight formula 2001: (10 * 28 + 20 * 337) / 365 = (280 + 6740)/365 = 7020/365 = 19.23287
    expected_2001 = round((10.0 * 28 + 20.0 * 337) / 365.0, 4)

    assert abs(y2000["day_weighted_mean"] - expected_2000) < 1e-4
    assert abs(y2001["day_weighted_mean"] - expected_2001) < 1e-4

# ---------------------------------------------------------
# 5. Day-Weighted Annual Temperature vs Unweighted
# ---------------------------------------------------------
def test_day_weighted_annual_temperature():
    """Verify day-weighted temperature properly weights 31-day vs 28/29-day months."""
    series = {}
    # Cold February (0°C), warm other months (30°C)
    for m in range(1, 13):
        series[f"2019{m:02d}"] = 0.0 if m == 2 else 30.0

    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "T2M")
    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "T2M")
    row = agg["annual_df"].iloc[0]

    unweighted = (0.0 + 30.0 * 11) / 12.0 # 27.5000
    day_weighted = (0.0 * 28 + 30.0 * 337) / 365.0 # 27.6986
    
    assert abs(row["unweighted_mean"] - 27.5000) < 1e-4
    assert abs(row["day_weighted_mean"] - round(day_weighted, 4)) < 1e-4
    assert row["day_weighted_mean"] > row["unweighted_mean"]

# ---------------------------------------------------------
# 6. Day-Weighted Precipitation Rate & Annual Accumulation
# ---------------------------------------------------------
def test_day_weighted_precipitation_rate_and_accumulation():
    """Verify precipitation daily rate (mm/day) and accumulation (mm/year) preservation."""
    series = {}
    for m in range(1, 13):
        series[f"2010{m:02d}"] = 2.0 # 2 mm/day constant rate

    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "PRECTOTCORR")
    agg = ScientificDataCleaner.compute_day_weighted_annual_aggregates(df, "PRECTOTCORR", is_precipitation=True)
    row = agg["annual_df"].iloc[0]

    assert row["mean_daily_rate_mm_per_day"] == 2.0
    assert row["annual_accumulated_mm"] == 2.0 * 365.0 # 730 mm

# ---------------------------------------------------------
# 7. Constant Time Series Handling (Zero Variance)
# ---------------------------------------------------------
def test_constant_time_series_handling():
    """Verify constant series does not silently claim 'no trend' or crash."""
    dates = [pd.Timestamp("2000-01-01") + pd.DateOffset(months=i) for i in range(36)]
    values = [25.0] * 36

    res = analyze_trend(dates, values, "T2M", "°C")
    assert res["status"] == "constant_series"
    assert "identical" in res["error"] or "zero variance" in res["error"]

# ---------------------------------------------------------
# 8. Missing Values Handling (-999, NaN)
# ---------------------------------------------------------
def test_missing_values_handling():
    """Verify -999.0 and NaN are converted to None and handled without crash."""
    series = {
        "200001": 20.0,
        "200002": -999.0, # NASA missing value flag
        "200003": np.nan,
        "200004": 22.0
    }
    df = ScientificDataCleaner.monthly_dict_to_dataframe(series, "T2M")
    assert df["T2M"].isna().sum() == 2
    comp = ScientificDataCleaner.assess_completeness(df, "T2M")
    assert comp["missing_records"] == 2
    assert comp["valid_records"] == 2

# ---------------------------------------------------------
# 9. Autocorrelated Annual Series & Statsmodels Ljung-Box
# ---------------------------------------------------------
def test_autocorrelated_series_audit():
    """Verify statsmodels Ljung-Box audit on synthetic AR(1) series."""
    np.random.seed(42)
    # Synthetic strongly autocorrelated AR(1) process: x_t = 0.8 * x_{t-1} + e_t
    n = 30
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.85 * x[t-1] + np.random.normal(0, 1)

    audit = _perform_autocorrelation_audit(x)
    assert audit["status"] == "success"
    assert audit["sample_size"] == 30
    assert len(audit["tested_lags"]) >= 3
    # With rho=0.85, lag-1 should be strongly positive and significant
    assert audit["lags_detail"][0]["autocorrelation_r"] > 0.4
    assert audit["has_significant_autocorrelation"] is True
    assert "Small-sample limitation" in audit["small_sample_limitation"]

# ---------------------------------------------------------
# 10. Non-Significant Annual Trend Handling
# ---------------------------------------------------------
def test_non_significant_annual_trend():
    """Verify pure white noise produces no significant trend."""
    np.random.seed(123)
    dates = []
    values = []
    for yr in range(1991, 2021):
        for m in range(1, 13):
            dates.append(pd.Timestamp(f"{yr}-{m:02d}-01"))
            values.append(20.0 + np.random.normal(0, 0.5))

    res = analyze_trend(dates, values, "T2M", "°C")
    assert res["status"] == "success"
    ann_mk = res["annual_mann_kendall"]["selected_result"]
    assert ann_mk["hypothesis_rejected"] is False
    assert "No statistically significant monotonic trend detected" in res["summary"]

# ---------------------------------------------------------
# 11. Seasonal Trend Evaluation (Hirsch-Slack)
# ---------------------------------------------------------
def test_seasonal_trend_evaluation():
    """Verify strong positive trend across months is detected by Seasonal MK."""
    dates = []
    values = []
    for yr_idx, yr in enumerate(range(1991, 2021)):
        for m in range(1, 13):
            dates.append(pd.Timestamp(f"{yr}-{m:02d}-01"))
            # Strong trend: +0.1°C per year
            values.append(15.0 + 10.0 * np.sin(2 * np.pi * m / 12) + 0.1 * yr_idx)

    res = analyze_trend(dates, values, "T2M", "°C")
    assert res["status"] == "success"
    seas_mk = res["seasonal_mann_kendall"]
    assert seas_mk["status"] == "success"
    assert seas_mk["hypothesis_rejected"] is True
    assert seas_mk["trend"] == "increasing"
    assert seas_mk["slope_unit"] == "°C/yr"

# ---------------------------------------------------------
# 12. Correct Sen's Slope Units ({units}/yr)
# ---------------------------------------------------------
def test_sens_slope_units():
    """Verify that both Seasonal MK and Annual MK slopes have unit {units}/yr."""
    dates = []
    values = []
    for yr_idx, yr in enumerate(range(1991, 2011)):
        for m in range(1, 13):
            dates.append(pd.Timestamp(f"{yr}-{m:02d}-01"))
            values.append(10.0 + 0.05 * yr_idx)

    res = analyze_trend(dates, values, "PRECTOTCORR", "mm/day")
    assert res["annual_mann_kendall"]["selected_result"]["slope_unit"] == "mm/day/yr"
    assert res["seasonal_mann_kendall"]["slope_unit"] == "mm/day/yr"
    assert res["linear_regression_annual"]["slope_unit"] == "mm/day/yr"

# ---------------------------------------------------------
# 13. PDF Generation with Special Characters (&, <, >, ", ')
# ---------------------------------------------------------
def test_pdf_generation_with_special_characters():
    """Verify PDF builds cleanly when user fields contain XML/HTML special characters."""
    inv = InvestigationModel(
        id="inv-test-xml-escape",
        title="Impact of Drought & Floods: <Critical Analysis> \"Special Characters\" 'Quotes'",
        research_question="Does T2M > 35°C & precipitation < 1.0 mm/day induce thermal stress?",
        hypothesis="H1: T2M & PRECTOTCORR show divergent trends (p < 0.05).",
        status="completed",
        location_name="Dera Ghazi Khan & Cholistan",
        region="Punjab & Sindh",
        country="Pakistan",
        latitude=30.05,
        longitude=70.63,
        spatial_extent={"north": 30.2, "south": 29.9, "east": 70.8, "west": 70.4},
        start_year="1991",
        end_year="2020",
        parameters=["T2M"],
        dataset_ids=["nasa-power-merra2"],
        findings=[
            {
                "id": "f-t2m-1",
                "title": "Temperature & Radiation: p < 0.01 & slope > 0.02 °C/yr",
                "classification": "statistical",
                "summary": "Verified: T2M has p < 0.05 & Kendall's Tau > 0.2.",
                "measurements": [
                    {
                        "id": "m1",
                        "label": "Annual Sen's Slope",
                        "value": "0.025",
                        "unit": "°C/yr",
                        "uncertainty": "p < 0.05"
                    }
                ]
            }
        ],
        time_series_data=[],
        statistical_metrics={
            "T2M": {
                "completeness": {"total_records": 360, "valid_records": 360, "completeness_percentage": 100.0},
                "trend": {
                    "sample_size_months": 360,
                    "autocorrelation_audit": {
                        "status": "success",
                        "sample_size": 30,
                        "tested_lags": [1, 2],
                        "lags_detail": [
                            {"lag": 1, "autocorrelation_r": 0.35, "p_value": 0.04},
                            {"lag": 2, "autocorrelation_r": 0.15, "p_value": 0.09}
                        ]
                    },
                    "annual_mann_kendall": {
                        "uncorrected_mann_kendall": {"p_value": 0.15, "kendall_tau": -0.18, "variance_s": 3141.67},
                        "hamed_rao_modified": {"p_value": 0.15, "modified_variance_s": 3141.67, "variance_correction_factor": 1.0}
                    }
                }
            }
        },
        raw_data_summary={"provider": "NASA & Partners", "source": "NASA POWER <MERRA-2>"},
        report_available=True
    )

    pdf_bytes = build_investigation_pdf(inv)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

# ---------------------------------------------------------
# 14. Failed Statistical Calculation Handling
# ---------------------------------------------------------
def test_failed_statistical_calculation_handling():
    """Verify that insufficient data returns structured failure metadata without fallback to p=1.0, slope=0.0."""
    dates = [pd.Timestamp(f"2020-0{m}-01") for m in range(1, 6)] # only 5 months
    values = [20.0, 21.0, 22.0, 23.0, 24.0]

    res = analyze_trend(dates, values, "T2M", "°C")
    assert res["status"] == "insufficient_data"
    assert "insufficient" in res["error"]
    assert "summary" not in res # Must NOT formulate a false scientific conclusion

# ---------------------------------------------------------
# 15. Climatological Anomaly Detection
# ---------------------------------------------------------
def test_climatological_anomaly_detection():
    """Verify detection of monthly Z-score departures >= 2.0 sigma."""
    from app.scientific.anomalies import ClimatologicalAnomalyDetector
    dates = []
    values = []
    for yr in range(2000, 2010):
        for m in range(1, 13):
            dates.append(pd.Timestamp(f"{yr}-{m:02d}-01"))
            # Standard month temperature
            base = 20.0 + (m * 1.5)
            # Inject extreme anomaly in June 2005
            if yr == 2005 and m == 6:
                base += 15.0
            values.append(base)

    res = ClimatologicalAnomalyDetector.detect_monthly_anomalies(dates, values, "T2M", "°C", z_threshold=2.0)
    assert res["status"] == "success"
    assert res["anomaly_count"] >= 1
    top = res["detected_anomalies"][0]
    assert top["date"] == "2005-06"
    assert top["standardized_z_score"] >= 2.0
    assert "Statistical anomalies indicate mathematical departure" in res["scientific_caveat"]

# ---------------------------------------------------------
# 16. Variable Comparison & Non-Causal Correlation
# ---------------------------------------------------------
def test_variable_comparison_and_correlation():
    """Verify co-variation comparison computes Pearson and Spearman without inferring causation."""
    from app.scientific.comparison import ClimatologicalVariableComparator
    dates = [pd.Timestamp(f"2010-{m:02d}-01") for m in range(1, 13)]
    vals_a = [10.0 + m for m in range(1, 13)]
    vals_b = [5.0 + 2.0 * m for m in range(1, 13)] # perfectly positively correlated

    res = ClimatologicalVariableComparator.compare_variables(
        dates, vals_a, "T2M", "°C",
        dates, vals_b, "PRECTOTCORR", "mm/day"
    )
    assert res["status"] == "success"
    assert res["sample_size"] == 12
    assert res["spearman_rank_correlation"]["coefficient_rho"] == 1.0
    assert res["pearson_correlation"]["coefficient_r"] == 1.0
    assert "CORRELATION DOES NOT IMPLY CAUSATION" in res["scientific_disclaimer"]

# ---------------------------------------------------------
# 17. Scientific CSV Export Generation
# ---------------------------------------------------------
def test_csv_export_generation():
    """Verify CSV export contains metadata header comments and time series rows."""
    from app.services.csv_generator import build_investigation_csv
    inv = InvestigationModel(
        id="inv-csv-test",
        title="Lahore Climatological Test",
        research_question="Does precipitation correlate with temperature?",
        hypothesis="Monsoon variance shifts",
        status="completed",
        location_name="Lahore",
        region="Punjab",
        country="Pakistan",
        latitude=31.5497,
        longitude=74.3436,
        start_year="1991",
        end_year="2020",
        parameters=["T2M", "PRECTOTCORR"],
        findings=[
            {
                "title": "T2M: Baseline",
                "classification": "statistical",
                "summary": "Verified baseline stability",
                "measurements": [{"label": "Sen's Slope", "value": "-0.03", "unit": "°C/yr", "uncertainty": "p = 0.15"}]
            }
        ],
        time_series_data=[
            {"timestamp": "1991", "observed": 26.30, "predicted": 26.25, "uncertaintyLower": None, "uncertaintyUpper": None},
            {"timestamp": "1992", "observed": 24.95, "predicted": 24.90, "uncertaintyLower": None, "uncertaintyUpper": None}
        ]
    )
    csv_str = build_investigation_csv(inv)
    assert "# EARTHSAGE AI" in csv_str
    assert "# Investigation ID: inv-csv-test" in csv_str
    assert "Year,Observed_Annual_Mean,OLS_Linear_Trend_Fit" in csv_str
    assert "1991,26.3,26.25" in csv_str

# ---------------------------------------------------------
# 18. Gemini AI Assistant Graceful Inactive State
# ---------------------------------------------------------
@pytest.mark.anyio
async def test_ai_assistant_graceful_state():
    """Verify that when AI_PROVIDER is inactive or unconfigured, the app falls back deterministically."""
    from app.services.ai_service import GeminiResearchAssistant
    assistant = GeminiResearchAssistant()
    status = assistant.get_status()
    assert "available" in status
    assert "provider" in status

    # Plan formulation must not crash
    plan = await assistant.plan_investigation("How has temperature evolved in Lahore?")
    assert plan["title"] is not None
    assert "Lahore" in plan["location_name"]
    assert "T2M" in plan["parameters"]

    # Explanation must not crash
    explanation = await assistant.explain_findings({
        "title": "Lahore Test",
        "location_name": "Lahore",
        "start_year": 1991,
        "end_year": 2020,
        "findings": [{"title": "T2M trend", "summary": "No trend detected"}]
    })
    assert explanation["plain_language_summary"] is not None
    assert "scientific_limitations" in explanation
