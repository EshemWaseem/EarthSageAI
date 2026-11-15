from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy import stats

def compute_descriptive_statistics(series: pd.Series, param_name: str, units: str) -> Dict[str, Any]:
    """
    Computes rigorous descriptive metrics on valid observations.
    """
    clean_series = series.dropna()
    n = len(clean_series)
    if n == 0:
        return {"error": "Insufficient valid observations for statistical evaluation."}

    mean_val = float(np.mean(clean_series))
    median_val = float(np.median(clean_series))
    std_val = float(np.std(clean_series, ddof=1)) if n > 1 else 0.0
    var_val = float(np.var(clean_series, ddof=1)) if n > 1 else 0.0
    min_val = float(np.min(clean_series))
    max_val = float(np.max(clean_series))
    q25 = float(np.percentile(clean_series, 25))
    q75 = float(np.percentile(clean_series, 75))
    iqr = q75 - q25

    # 95% Confidence Interval for mean using Student's t distribution
    if n > 1 and std_val > 0:
        sem = std_val / np.sqrt(n)
        ci_lower, ci_upper = stats.t.interval(0.95, df=n - 1, loc=mean_val, scale=sem)
    else:
        ci_lower, ci_upper = mean_val, mean_val

    return {
        "parameter": param_name,
        "units": units,
        "sample_size": n,
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "standard_deviation": round(std_val, 4),
        "variance": round(var_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "q25": round(q25, 4),
        "q75": round(q75, 4),
        "iqr": round(iqr, 4),
        "ci_95": {
            "lower": round(float(ci_lower), 4),
            "upper": round(float(ci_upper), 4)
        }
    }

