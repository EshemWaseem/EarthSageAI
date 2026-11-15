import asyncio
from app.providers.nasa_power import NASAPowerProvider
import calendar

async def test():
    prov = NASAPowerProvider()
    data = await prov.fetch_monthly_data(31.5497, 74.3436, 1991, 2020, ['T2M', 'PRECTOTCORR'])
    for p in ['T2M', 'PRECTOTCORR']:
        series = data['parameters'][p]['series']
        raw_keys = list(series.keys())
        m13_keys = [k for k in raw_keys if k.endswith('13')]
        print(f"=== {p} ===")
        print(f"Total keys: {len(raw_keys)}, Month 13 keys: {len(m13_keys)}")
        
        # Compare 1991 (non-leap) and 1992 (leap) NASA YYYY13 vs unweighted mean vs day-weighted mean
        for yr in [1991, 1992]:
            months_vals = [series[f"{yr}{m:02d}"] for m in range(1, 13)]
            nasa_13 = series.get(f"{yr}13")
            unweighted = sum(months_vals) / 12.0
            
            # day-weighted
            days_in_months = [calendar.monthrange(yr, m)[1] for m in range(1, 13)]
            total_days = sum(days_in_months)
            day_weighted = sum(v * d for v, d in zip(months_vals, days_in_months)) / total_days
            
            print(f"Year {yr} (days={total_days}):")
            print(f"  NASA YYYY13:   {nasa_13}")
            print(f"  Day-weighted:  {day_weighted:.4f}")
            print(f"  Unweighted:    {unweighted:.4f}")
            print(f"  Diff (NASA - DayWeighted): {nasa_13 - day_weighted:.6f}")
            print(f"  Diff (NASA - Unweighted):  {nasa_13 - unweighted:.6f}")

asyncio.run(test())

