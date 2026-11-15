import csv
import io
import datetime
from app.database.models import InvestigationModel

def build_investigation_csv(inv: InvestigationModel) -> str:
    """
    Builds a scientific, peer-reviewable CSV export containing:
    1. Structured provenance and methodology metadata in commented header lines (#).
    2. Exact geographic coordinates, grid resolution disclosure, and limitations.
    3. Tabular empirical observations (annual day-weighted series & monthly observations).
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Scientific Header Comments
    output.write("# =============================================================================\n")
    output.write("# EARTHSAGE AI — SCIENTIFIC RESEARCH & GEOSPATIAL AUDIT DATA EXPORT\n")
    output.write(f"# Investigation ID: {inv.id}\n")
    output.write(f"# Title: {inv.title}\n")
    output.write(f"# Research Question: {inv.research_question}\n")
    if inv.hypothesis:
        output.write(f"# Working Hypothesis: {inv.hypothesis}\n")
    output.write(f"# Target Location: {inv.location_name}, {inv.country}\n")
    lat_str = f"{abs(inv.latitude):.4f}°{'N' if inv.latitude >= 0 else 'S'}"
    lon_str = f"{abs(inv.longitude):.4f}°{'E' if inv.longitude >= 0 else 'W'}"
    output.write(f"# Coordinates: {lat_str}, {lon_str} (WGS84)\n")
    output.write(f"# Temporal Window: {inv.start_year}–{inv.end_year}\n")
    output.write("# Primary Provider: NASA Langley Research Center\n")
    output.write("# Data Source: NASA POWER / MERRA-2 Reanalysis (0.5° x 0.625° assimilation grid)\n")
    output.write("# Methodology: Day-weighted annual aggregation, Seasonal Mann-Kendall (p=12), Ljung-Box autocorrelation test\n")
    output.write("# Limitations: Single grid cell estimate; model-assimilated reanalysis, not direct in-situ ground station measurements.\n")
    output.write(f"# Export Timestamp: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    output.write("# =============================================================================\n#\n")

    # 2. Findings & Statistical Summary Section
    output.write("# --- EMPIRICAL FINDINGS & STATISTICAL METRICS ---\n")
    for f in inv.findings:
        output.write(f"# Finding: {f.get('title')} [{f.get('classification', '').upper()}]\n")
        output.write(f"# Summary: {f.get('summary')}\n")
        for m in f.get("measurements", []):
            output.write(f"#   Measurement: {m.get('label')} = {m.get('value')} {m.get('unit')} ({m.get('uncertainty', '')})\n")
    output.write("# ------------------------------------------------\n#\n")

    # 3. Time Series Data Section
    output.write("# --- ANNUAL TIME SERIES DATA (DAY-WEIGHTED OBSERVATIONS & OLS TREND) ---\n")
    ts_data = inv.time_series_data or []
    writer.writerow(["Year", "Observed_Annual_Mean", "OLS_Linear_Trend_Fit", "Uncertainty_Lower", "Uncertainty_Upper"])
    
    for row in ts_data:
        writer.writerow([
            row.get("timestamp"),
            row.get("observed"),
            row.get("predicted"),
            row.get("uncertaintyLower"),
            row.get("uncertaintyUpper")
        ])

    return output.getvalue()

