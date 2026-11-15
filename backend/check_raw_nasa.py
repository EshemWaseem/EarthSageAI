import httpx
import calendar

async def test_raw():
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "T2M,PRECTOTCORR",
        "community": "RE",
        "longitude": "74.3436",
        "latitude": "31.5497",
        "start": "1991",
        "end": "1995",
        "format": "JSON"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params)
        data = r.json()["properties"]["parameter"]

    for param in ["T2M", "PRECTOTCORR"]:
        print(f"\n=== {param} ===")
        for yr in [1991, 1992]:
            months = [data[param][f"{yr}{m:02d}"] for m in range(1, 13)]
            nasa_ann = data[param].get(f"{yr}13")
            unweighted = sum(months) / 12.0
            days = [calendar.monthrange(yr, m)[1] for m in range(1, 13)]
            total_days = sum(days)
            day_weighted = sum(m * d for m, d in zip(months, days)) / total_days
            print(f"Year {yr} ({'leap' if total_days==366 else 'standard'}, days={total_days}):")
            print(f"  NASA YYYY13:     {nasa_ann:.4f}")
            print(f"  Day-weighted:    {day_weighted:.4f} (diff vs NASA: {day_weighted - nasa_ann:+.6f})")
            print(f"  Unweighted mean: {unweighted:.4f} (diff vs NASA: {unweighted - nasa_ann:+.6f})")

import asyncio
asyncio.run(test_raw())
