from typing import Dict, Any, List, Tuple, Optional
import calendar
import pandas as pd
import numpy as np

class ScientificDataCleaner:
    @staticmethod
    def monthly_dict_to_dataframe(series_dict: Dict[str, Optional[float]], param_name: str) -> pd.DataFrame:
        """
        Convert {YYYYMM: value} dict to structured Pandas DataFrame with datetime index.
        Validates date keys and sorts chronologically.
        """
        records = []
        for key, val in series_dict.items():
            if len(key) != 6 or not key.isdigit():
                continue
            year = int(key[:4])
            month = int(key[4:])
            if not (1 <= month <= 12):
                continue
            date_str = f"{year:04d}-{month:02d}-01"
            
            clean_val = None
            if val is not None:
                try:
                    f_val = float(val)
                    if f_val > -900.0 and not np.isnan(f_val):
                        clean_val = f_val
                except (ValueError, TypeError):
                    clean_val = None

            records.append({
                "date": date_str,
                "year": year,
                "month": month,
                param_name: clean_val
            })
        
        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(columns=["date", "year", "month", param_name])
            
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @staticmethod
    def assess_completeness(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        total = len(df)
        valid = int(df[column].notna().sum()) if total > 0 and column in df.columns else 0
        missing = total - valid
        completeness_pct = round((valid / total) * 100, 2) if total > 0 else 0.0

        return {
            "total_records": int(total),
            "valid_records": int(valid),
            "missing_records": int(missing),
            "completeness_percentage": completeness_pct,
            "meets_scientific_threshold": completeness_pct >= 85.0
        }

    @staticmethod
    def compute_day_weighted_annual_aggregates(
        df: pd.DataFrame,
        param_name: str,
        is_precipitation: bool = False
    ) -> Dict[str, Any]:
        """
        Performs rigorous climatological annual aggregation:
        1. Checks every calendar year for complete 12-month series (months 1-12).
        2. Detects duplicate months, missing months, and invalid observations.
        3. Excludes incomplete years from annual series with explicit documentation.
        4. Applies day-weighting based on exact calendar month duration:
           - Correctly handles leap years (Feb = 29 days, total = 366 days).
           - T2M day-weighted mean: sum(T_m * days_m) / total_days.
           - PRECTOTCORR mean daily rate: sum(P_m * days_m) / total_days (mm/day).
           - PRECTOTCORR annual accumulation: sum(P_m * days_m) (mm/year).
        """
        if df.empty or param_name not in df.columns:
            return {
                "annual_df": pd.DataFrame(),
                "total_years": 0,
                "complete_years": 0,
                "excluded_years": [],
                "completeness_ratio": 0.0,
                "error": "Input dataframe is empty or missing parameter column."
            }

        grouped = df.groupby("year")
        annual_records = []
        excluded_years = []

        all_years = sorted(df["year"].unique())

        for yr in all_years:
            yr_df = df[df["year"] == yr]
            
            # Check 1: Detect duplicate months
            month_counts = yr_df["month"].value_counts()
            duplicates = month_counts[month_counts > 1].index.tolist()
            if duplicates:
                excluded_years.append({
                    "year": int(yr),
                    "reason": f"Duplicate monthly observations detected for month(s): {duplicates}"
                })
                continue

            # Check 2: Verify all 12 calendar months exist
            present_months = set(yr_df["month"].tolist())
            required_months = set(range(1, 13))
            missing_months = sorted(list(required_months - present_months))
            if missing_months:
                excluded_years.append({
                    "year": int(yr),
                    "reason": f"Incomplete annual record; missing month(s): {missing_months}"
                })
                continue

            # Check 3: Verify all 12 months have valid non-null values
            valid_months_df = yr_df.dropna(subset=[param_name])
            if len(valid_months_df) < 12:
                invalid_months = yr_df[yr_df[param_name].isna()]["month"].tolist()
                excluded_years.append({
                    "year": int(yr),
                    "reason": f"Missing or invalid observation in month(s): {invalid_months}"
                })
                continue

            # Sort by month 1..12
            yr_df_sorted = yr_df.sort_values("month").reset_index(drop=True)

            # Calculate exact days per month, handling leap years
            days_in_months = []
            for m in range(1, 13):
                _, num_days = calendar.monthrange(int(yr), m)
                days_in_months.append(num_days)

            total_days_in_year = sum(days_in_months)
            is_leap = calendar.isleap(int(yr))

            monthly_values = yr_df_sorted[param_name].to_numpy()
            days_array = np.array(days_in_months, dtype=float)

            # Day-weighted annual mean
            day_weighted_mean = float(np.sum(monthly_values * days_array) / total_days_in_year)
            
            # Unweighted arithmetic mean (for audit comparison)
            unweighted_mean = float(np.mean(monthly_values))

            record = {
                "year": int(yr),
                "day_weighted_mean": round(day_weighted_mean, 4),
                "unweighted_mean": round(unweighted_mean, 4),
                "days_in_year": total_days_in_year,
                "is_leap_year": is_leap,
                "unweighted_diff": round(day_weighted_mean - unweighted_mean, 6)
            }

            if is_precipitation:
                # Annual cumulative precipitation in mm
                accumulated_precip_mm = float(np.sum(monthly_values * days_array))
                record["annual_accumulated_mm"] = round(accumulated_precip_mm, 2)
                record["mean_daily_rate_mm_per_day"] = round(day_weighted_mean, 4)

            annual_records.append(record)

        annual_df = pd.DataFrame(annual_records)
        total_yrs = len(all_years)
        complete_yrs = len(annual_records)
        ratio = round(complete_yrs / total_yrs, 4) if total_yrs > 0 else 0.0

        return {
            "annual_df": annual_df,
            "total_years": total_yrs,
            "complete_years": complete_yrs,
            "excluded_years": excluded_years,
            "completeness_ratio": ratio,
            "is_complete": len(excluded_years) == 0
        }
