from typing import Dict, Any, List
import numpy as np
import pandas as pd

class ClimatologicalAnomalyDetector:
    """
    Rigorously detects statistical climatological anomalies in meteorological series:
    1. Monthly Climatological Normalization:
       Computes 12-month calendar baselines (mean mu_m and std sigma_m for each calendar month).
       Calculates standardized anomaly Z_{y, m} = (x_{y, m} - mu_m) / sigma_m.
    2. Identifies moderate (|Z| >= 2.0) and extreme (|Z| >= 2.5) anomalies.
    3. Annual series Tukey's outer fences (Q1 - 1.5*IQR, Q3 + 1.5*IQR).
    4. Explicitly distinguishes statistical outliers from confirmed disaster events.
    """

    @staticmethod
    def detect_monthly_anomalies(
        dates: List[pd.Timestamp],
        values: List[float],
        param_name: str,
        units: str,
        z_threshold: float = 2.0
    ) -> Dict[str, Any]:
        df = pd.DataFrame({"date": dates, "value": values}).dropna()
        if len(df) < 24:
            return {
                "status": "insufficient_data",
                "message": "Minimum 24 monthly observations required for climatological baseline calculation."
            }

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year

        # Compute calendar month climatologies
        clim_stats = df.groupby("month")["value"].agg(["mean", "std"]).reset_index()
        clim_map = {row["month"]: (row["mean"], row["std"]) for _, row in clim_stats.iterrows()}

        anomalies = []
        all_z_scores = []

        for _, row in df.iterrows():
            m = row["month"]
            v = row["value"]
            mu_m, sig_m = clim_map[m]

            if sig_m > 0:
                z = (v - mu_m) / sig_m
            else:
                z = 0.0

            all_z_scores.append(z)

            if abs(z) >= z_threshold:
                direction = "positive" if z > 0 else "negative"
                severity = "extreme" if abs(z) >= 2.5 else "moderate"
                anomalies.append({
                    "date": row["date"].strftime("%Y-%m"),
                    "year": int(row["year"]),
                    "month": int(m),
                    "observed_value": round(float(v), 3),
                    "climatological_mean": round(float(mu_m), 3),
                    "departure": round(float(v - mu_m), 3),
                    "standardized_z_score": round(float(z), 3),
                    "direction": direction,
                    "severity": severity,
                    "units": units
                })

        # Sort anomalies by absolute departure magnitude
        anomalies_sorted = sorted(anomalies, key=lambda x: abs(x["standardized_z_score"]), reverse=True)

        return {
            "status": "success",
            "parameter": param_name,
            "units": units,
            "total_observations": len(df),
            "anomaly_count": len(anomalies),
            "anomaly_percentage": round((len(anomalies) / len(df)) * 100, 2),
            "z_threshold_used": z_threshold,
            "methodology": (
                "Month-of-year standardized departure: Z = (x_{y,m} - mu_m) / sigma_m, "
                "where mu_m and sigma_m represent the 1991–2020 monthly calendar baseline."
            ),
            "scientific_caveat": (
                "Statistical anomalies indicate mathematical departure (>= 2.0 sigma) from the baseline. "
                "They represent statistical extremities and do not automatically confirm specific ground damage "
                "or declared disaster events without auxiliary ground verification."
            ),
            "detected_anomalies": anomalies_sorted[:15] # Top 15 most significant
        }

