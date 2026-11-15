import httpx
import calendar
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
import pymannkendall as mk
from scipy import stats

async def run_full_check():
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "T2M,PRECTOTCORR",
        "community": "RE",
        "longitude": "74.3436",
        "latitude": "31.5497",
        "start": "1991",
        "end": "2020",
        "format": "JSON"
    }
    async with httpx.AsyncClient(timeout=45) as client:
        r = await client.get(url, params=params)
        data = r.json()["properties"]["parameter"]

    for param in ["T2M", "PRECTOTCORR"]:
        print(f"\n==================== {param} ====================")
        years = list(range(1991, 2021))
        annual_day_weighted = []
        annual_unweighted = []
        nasa_annual_13 = []
        monthly_all = []

        for yr in years:
            months = [data[param][f"{yr}{m:02d}"] for m in range(1, 13)]
            monthly_all.extend(months)
            days = [calendar.monthrange(yr, m)[1] for m in range(1, 13)]
            total_days = sum(days)
            dw = sum(m * d for m, d in zip(months, days)) / total_days
            uw = sum(months) / 12.0
            annual_day_weighted.append(dw)
            annual_unweighted.append(uw)
            nasa_annual_13.append(data[param].get(f"{yr}13"))

        dw_arr = np.array(annual_day_weighted)
        uw_arr = np.array(annual_unweighted)
        m_arr = np.array(monthly_all)

        print(f"Sample size: {len(dw_arr)} years, {len(m_arr)} months")
        print(f"Mean Day-weighted: {np.mean(dw_arr):.4f}, Std: {np.std(dw_arr, ddof=1):.4f}")
        print(f"Mean Unweighted:   {np.mean(uw_arr):.4f}, Std: {np.std(uw_arr, ddof=1):.4f}")

        # Ljung-Box test on Day-weighted series at multiple lags
        # For N=30, test lags 1, 2, 3, 4
        lb_res = acorr_ljungbox(dw_arr, lags=[1, 2, 3, 4, 5], return_df=True)
        print("\nStatsmodels acorr_ljungbox results:")
        print(lb_res)

        # Autocorrelation coefficients at lags 1..5
        mean_v = np.mean(dw_arr)
        denom = np.sum((dw_arr - mean_v)**2)
        r_lags = []
        for k in range(1, 6):
            num = np.sum((dw_arr[k:] - mean_v) * (dw_arr[:-k] - mean_v))
            r_k = num / denom
            r_lags.append(r_k)
            print(f"  Lag-{k} r = {r_k:.4f}")

        # Mann-Kendall tests on Annual Day-Weighted
        mk_orig = mk.original_test(dw_arr)
        mk_hr_default = mk.hamed_rao_modification_test(dw_arr)
        mk_hr_lag3 = mk.hamed_rao_modification_test(dw_arr, lag=3)

        print("\n--- Annual Mann-Kendall Comparisons ---")
        print(f"Original MK:   trend={mk_orig.trend}, p={mk_orig.p:.6f}, tau={mk_orig.Tau:.4f}, slope={mk_orig.slope:.6f}, var_s={mk_orig.var_s:.2f}")
        print(f"Hamed-Rao def: trend={mk_hr_default.trend}, p={mk_hr_default.p:.6f}, tau={mk_hr_default.Tau:.4f}, slope={mk_hr_default.slope:.6f}, var_s={mk_hr_default.var_s:.2f}")
        print(f"Hamed-Rao l=3: trend={mk_hr_lag3.trend}, p={mk_hr_lag3.p:.6f}, tau={mk_hr_lag3.Tau:.4f}, slope={mk_hr_lag3.slope:.6f}, var_s={mk_hr_lag3.var_s:.2f}")
        var_factor_def = mk_hr_default.var_s / mk_orig.var_s
        print(f"Variance correction factor (V*/V): {var_factor_def:.4f}")

        # Seasonal Mann-Kendall on Monthly
        mk_seas = mk.seasonal_test(m_arr, period=12)
        print("\n--- Seasonal Mann-Kendall (Monthly, period=12) ---")
        print(f"Seasonal MK:   trend={mk_seas.trend}, p={mk_seas.p:.6e}, tau={mk_seas.Tau:.4f}, slope={mk_seas.slope:.6f}/yr, var_s={mk_seas.var_s:.2f}")

import asyncio
asyncio.run(run_full_check())
