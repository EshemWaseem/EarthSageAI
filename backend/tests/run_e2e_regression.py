#!/usr/bin/env python3
"""
EarthSage AI — End-to-End Production & Scientific Regression Verification
Verifies all 14 mandatory validation points against the live environment.
"""

import sys
import json
import httpx

BASE_URL = "http://localhost:8020"

def log_test(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(f"       Details: {detail}")
    if not passed:
        sys.exit(1)

def run_regression_suite():
    print("=" * 70)
    print("EARTHSAGE AI — LIVE SCIENTIFIC & FUNCTIONAL REGRESSION TEST SUITE")
    print(f"Target Base URL: {BASE_URL}")
    print("=" * 70)

    client = httpx.Client(base_url=BASE_URL, timeout=45.0)

    # 1. Health & Config Endpoint
    res = client.get("/health")
    log_test(
        "API Health Check (/health)",
        res.status_code == 200 and res.json().get("status") == "healthy",
        f"HTTP {res.status_code}, payload: {res.json()}"
    )

    # 2. Datasets Catalog & Space Apps Challenge Resources
    res = client.get("/api/v1/datasets")
    data = res.json()
    dataset_ids = [d["id"] for d in data]
    has_power = "nasa-power-merra2" in dataset_ids
    has_giovanni = "nasa-giovanni" in dataset_ids
    has_appeears = "nasa-appeears" in dataset_ids
    log_test(
        "Challenge Datasets Catalog (/api/v1/datasets)",
        res.status_code == 200 and has_power and has_giovanni and has_appeears,
        f"Available: {dataset_ids}"
    )

    # 3. Existing Baseline Investigation Query
    res = client.get("/api/v1/investigations/inv-20261114-30c9a0")
    inv = res.json()
    log_test(
        "Database Persistence (Lahore Baseline inv-20261114-30c9a0)",
        res.status_code == 200 and inv["id"] == "inv-20261114-30c9a0" and inv["status"] == "completed",
        f"Status: {inv.get('status')}, Location: {inv.get('primaryLocation', {}).get('name')}"
    )

    # 4. Seasonal MK & Annual MK Slopes in Physical Units ({units}/yr)
    t2m_metrics = inv.get("statisticalMetrics", {}).get("T2M", {})
    t2m_trend = t2m_metrics.get("trend", {})
    seas_unit = t2m_trend.get("seasonal_mann_kendall", {}).get("slope_unit")
    ann_unit = t2m_trend.get("annual_mann_kendall", {}).get("selected_result", {}).get("slope_unit")
    log_test(
        "PyMannKendall Sen's Slope Unit Verification ({units}/yr)",
        seas_unit == "°C/yr" and ann_unit == "°C/yr",
        f"Seasonal Slope Unit: '{seas_unit}', Annual Slope Unit: '{ann_unit}'"
    )

    # 5. Autocorrelation & Hamed-Rao Audit
    autocorr = t2m_trend.get("autocorrelation_audit", {})
    has_lags = len(autocorr.get("tested_lags", [])) >= 4
    v_ratio = t2m_trend.get("annual_mann_kendall", {}).get("hamed_rao_modified", {}).get("variance_correction_factor")
    log_test(
        "Serial Autocorrelation & Hamed-Rao Ratio",
        has_lags and v_ratio == 1.0,
        f"Tested Lags: {autocorr.get('tested_lags')}, V*/V: {v_ratio}"
    )

    # 6. Live NASA POWER Data Retrieval Test
    query_body = {
        "latitude": 31.5497,
        "longitude": 74.3436,
        "start_year": 2019,
        "end_year": 2020,
        "parameters": ["T2M", "PRECTOTCORR"]
    }
    res = client.post("/api/v1/analysis/query-nasa", json=query_body)
    raw_nasa = res.json()
    t2m_series = raw_nasa.get("parameters", {}).get("T2M", {}).get("series", {})
    log_test(
        "Live NASA POWER Data Retrieval (/api/v1/analysis/query-nasa)",
        res.status_code == 200 and len(t2m_series) >= 24,
        f"Retrieved {len(t2m_series)} monthly points directly from NASA POWER"
    )

    # 7. Climatological Anomaly Detection (|Z| >= 2.0 sigma)
    res = client.get("/api/v1/analysis/investigations/inv-20261114-30c9a0/anomalies")
    anom_data = res.json()
    t2m_anom = anom_data.get("anomalies", {}).get("T2M", {})
    prect_anom = anom_data.get("anomalies", {}).get("PRECTOTCORR", {})
    has_caveat = "Statistical anomalies indicate mathematical departure" in t2m_anom.get("scientific_caveat", "")
    log_test(
        "Climatological Anomaly Detection & Disaster Caveat",
        res.status_code == 200 and t2m_anom.get("anomaly_count") == 7 and prect_anom.get("anomaly_count") == 16 and has_caveat,
        f"T2M anomalies: {t2m_anom.get('anomaly_count')}, PRECTOTCORR anomalies: {prect_anom.get('anomaly_count')}"
    )

    # 8. Variable Comparison & Non-Causality Banner
    res = client.get("/api/v1/analysis/investigations/inv-20261114-30c9a0/compare?param_a=T2M&param_b=PRECTOTCORR")
    comp_data = res.json()
    comp = comp_data.get("comparison", {})
    r_val = comp.get("pearson_correlation", {}).get("coefficient_r")
    rho_val = comp.get("spearman_rank_correlation", {}).get("coefficient_rho")
    has_disclaimer = "CORRELATION DOES NOT IMPLY CAUSATION" in comp.get("scientific_disclaimer", "")
    log_test(
        "Atmospheric Variable Comparison & Non-Causal Coupling",
        res.status_code == 200 and r_val == 0.3766 and rho_val == 0.4258 and has_disclaimer,
        f"Pearson r: {r_val}, Spearman rho: {rho_val}"
    )

    # 9. AI Graceful Inactive State & Deterministic Synthesis
    res = client.get("/api/v1/ai/status")
    ai_status = res.json()
    plan_res = client.post("/api/v1/ai/plan", json={"research_question": "How did temperature and rainfall evolve in Islamabad over 1991-2020?"})
    plan_data = plan_res.json()
    explain_res = client.post("/api/v1/ai/explain/inv-20261114-30c9a0")
    explain_data = explain_res.json()
    log_test(
        "AI Fallback State & Hallucination Prevention",
        ai_status["available"] is False and plan_data["is_ai_generated"] is False and explain_data["is_ai_generated"] is False,
        f"AI Provider: {ai_status.get('provider')}, Deterministic Planner Note: '{plan_data.get('note')}'"
    )

    # 10. PDF Report Generation & Binary Download
    pdf_gen_res = client.post("/api/v1/reports", json={"investigation_id": "inv-20261114-30c9a0", "file_format": "PDF"})
    pdf_meta = pdf_gen_res.json()
    pdf_id = pdf_meta["id"]
    pdf_dl_res = client.get(f"/api/v1/reports/{pdf_id}/download")
    is_valid_pdf = pdf_dl_res.content.startswith(b"%PDF")
    log_test(
        "Dynamic ReportLab PDF Report Generation",
        pdf_gen_res.status_code == 200 and pdf_dl_res.status_code == 200 and is_valid_pdf,
        f"Report ID: {pdf_id}, Size: {len(pdf_dl_res.content)} bytes, Magic: {pdf_dl_res.content[:5]}"
    )

    # 11. CSV Export Generation with Commented Headers
    csv_gen_res = client.post("/api/v1/reports", json={"investigation_id": "inv-20261114-30c9a0", "file_format": "CSV"})
    csv_meta = csv_gen_res.json()
    csv_id = csv_meta["id"]
    csv_dl_res = client.get(f"/api/v1/reports/{csv_id}/download")
    csv_text = csv_dl_res.text
    has_header = "# EARTHSAGE AI" in csv_text and "# Coordinates: 31.5497°N, 74.3436°E" in csv_text
    log_test(
        "FAIR-Compliant Commented Metadata CSV Export",
        csv_gen_res.status_code == 200 and csv_dl_res.status_code == 200 and has_header,
        f"Report ID: {csv_id}, Size: {len(csv_text)} chars"
    )

    # 12. Create New Investigation via API
    new_inv_payload = {
        "title": "Rawalpindi Temperature & Monsoon Study",
        "research_question": "Are monsoon precipitation fluctuations increasing in northern Punjab?",
        "hypothesis": "Extreme monsoonal precipitation frequency has shifted upwards.",
        "location_name": "Rawalpindi",
        "region": "Punjab",
        "country": "Pakistan",
        "latitude": 33.5651,
        "longitude": 73.0169,
        "start_year": 2010,
        "end_year": 2020,
        "parameters": ["T2M", "PRECTOTCORR"]
    }
    create_res = client.post("/api/v1/investigations", json=new_inv_payload)
    new_inv = create_res.json()
    new_id = new_inv["id"]
    log_test(
        "Investigation Registration Pipeline",
        create_res.status_code == 200 and new_id.startswith("inv-"),
        f"Created Investigation ID: {new_id}"
    )

    # 13. Execute Analytical Pipeline on New Investigation (Live NASA POWER ingestion)
    run_res = client.post(f"/api/v1/investigations/{new_id}/run")
    run_inv = run_res.json()
    has_findings = len(run_inv.get("findings", [])) >= 2
    has_time_series = len(run_inv.get("timeSeriesData", [])) >= 10
    log_test(
        "Live Pipeline Execution & Persistence (Rawalpindi)",
        run_res.status_code == 200 and run_inv["status"] == "completed" and has_findings and has_time_series,
        f"Status: {run_inv.get('status')}, Findings Generated: {len(run_inv.get('findings', []))}"
    )

    # 14. Input Validation & Security Rejection
    bad_res = client.post("/api/v1/investigations", json={
        "title": "X", # too short (<3)
        "research_question": "Bad",
        "latitude": 150.0, # invalid latitude (>90)
        "longitude": 74.0,
        "start_year": 2020,
        "end_year": 1990 # invalid year order
    })
    log_test(
        "Security Input Validation & Bound Checking",
        bad_res.status_code == 422,
        f"HTTP {bad_res.status_code} properly rejected invalid parameters"
    )

    print("=" * 70)
    print("ALL 14 E2E FUNCTIONAL & SCIENTIFIC REGRESSION TESTS PASSED (100% VERIFIED)")
    print("=" * 70)

if __name__ == "__main__":
    run_regression_suite()

