from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats

class ClimatologicalVariableComparator:
    """
    Rigorously compares multiple environmental time series over the identical temporal period:
    1. Temporal Alignment: Performs strict inner join on dates.
    2. Documented Normalization: Standardizes variables to dimensionless Z-scores (mu=0, sigma=1)
       for valid visual overlay without arbitrary axis scaling distortion.
    3. Parametric (Pearson r) and Non-Parametric (Spearman rho) co-variation testing with 2-tailed p-values.
    4. Strict Scientific Constraint: Explicitly disclaims causal inference.
    """

    @staticmethod
    def compare_variables(
        dates_a: List[pd.Timestamp],
        values_a: List[float],
        param_a_name: str,
        units_a: str,
        dates_b: List[pd.Timestamp],
        values_b: List[float],
        param_b_name: str,
        units_b: str
    ) -> Dict[str, Any]:
        df_a = pd.DataFrame({"date": dates_a, "val_a": values_a}).dropna()
        df_b = pd.DataFrame({"date": dates_b, "val_b": values_b}).dropna()

        # Align on date
        merged = pd.merge(df_a, df_b, on="date").sort_values("date").reset_index(drop=True)
        n = len(merged)

        if n < 12:
            return {
                "status": "insufficient_data",
                "message": f"Only {n} overlapping observations; minimum 12 required for co-variation evaluation."
            }

        arr_a = merged["val_a"].to_numpy(dtype=float)
        arr_b = merged["val_b"].to_numpy(dtype=float)

        # Statistical correlation evaluations
        pearson_r, pearson_p = stats.pearsonr(arr_a, arr_b)
        spearman_rho, spearman_p = stats.spearmanr(arr_a, arr_b)

        # Standardized Z-scores for normalized overlay
        std_a = np.std(arr_a, ddof=1)
        std_b = np.std(arr_b, ddof=1)

        z_a = (arr_a - np.mean(arr_a)) / std_a if std_a > 0 else np.zeros(n)
        z_b = (arr_b - np.mean(arr_b)) / std_b if std_b > 0 else np.zeros(n)

        # Format comparison time series
        comparison_series = []
        for idx, row in merged.iterrows():
            d_str = row["date"].strftime("%Y-%m") if hasattr(row["date"], "strftime") else str(row["date"])[:7]
            comparison_series.append({
                "timestamp": d_str,
                "val_a": round(float(row["val_a"]), 2),
                "val_b": round(float(row["val_b"]), 2),
                "norm_a": round(float(z_a[idx]), 3),
                "norm_b": round(float(z_b[idx]), 3)
            })

        correlation_direction = "positive" if spearman_rho > 0 else "negative"
        significance_desc = "statistically significant" if spearman_p < 0.05 else "not statistically significant"

        summary = (
            f"Over {n} concurrent monthly observations, {param_a_name} and {param_b_name} display a "
            f"{significance_desc} {correlation_direction} rank correlation "
            f"(Spearman rho = {spearman_rho:.3f}, p = {spearman_p:.4e}; Pearson r = {pearson_r:.3f}, p = {pearson_p:.4e})."
        )

        return {
            "status": "success",
            "param_a": {"name": param_a_name, "units": units_a, "mean": round(float(np.mean(arr_a)), 3), "std": round(float(std_a), 3)},
            "param_b": {"name": param_b_name, "units": units_b, "mean": round(float(np.mean(arr_b)), 3), "std": round(float(std_b), 3)},
            "sample_size": n,
            "pearson_correlation": {
                "coefficient_r": round(float(pearson_r), 4),
                "p_value": round(float(pearson_p), 6),
                "significant": bool(pearson_p < 0.05)
            },
            "spearman_rank_correlation": {
                "coefficient_rho": round(float(spearman_rho), 4),
                "p_value": round(float(spearman_p), 6),
                "significant": bool(spearman_p < 0.05)
            },
            "summary": summary,
            "scientific_disclaimer": (
                "CORRELATION DOES NOT IMPLY CAUSATION. Co-variation between atmospheric variables reflects "
                "coupled Earth system feedbacks and seasonal forcing, not a direct unidirectional causal mechanism."
            ),
            "comparison_series": comparison_series
        }

