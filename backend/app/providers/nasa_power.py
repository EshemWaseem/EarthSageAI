import datetime
from typing import Dict, Any, List
import httpx
from app.core.config import settings

# Supported NASA POWER monthly parameters with rigorous scientific descriptions
SUPPORTED_PARAMETERS = {
    "T2M": {
        "name": "Temperature at 2 Meters",
        "description": "MERRA-2 monthly mean air temperature estimated at 2 meters above surface level",
        "units": "°C",
        "estimate_type": "NASA POWER / MERRA-2 assimilation estimate",
        "missing_value": -999.0
    },
    "T2M_MAX": {
        "name": "Maximum Temperature at 2 Meters",
        "description": "MERRA-2 monthly maximum of daily maximum air temperature at 2 meters",
        "units": "°C",
        "estimate_type": "NASA POWER / MERRA-2 assimilation estimate",
        "missing_value": -999.0
    },
    "T2M_MIN": {
        "name": "Minimum Temperature at 2 Meters",
        "description": "MERRA-2 monthly minimum of daily minimum air temperature at 2 meters",
        "units": "°C",
        "estimate_type": "NASA POWER / MERRA-2 assimilation estimate",
        "missing_value": -999.0
    },
    "PRECTOTCORR": {
        "name": "Precipitation Corrected",
        "description": "Bias-corrected total monthly precipitation flux derived from MERRA-2 / GPCP satellite products",
        "units": "mm/day",
        "estimate_type": "NASA POWER / MERRA-2 assimilation estimate",
        "missing_value": -999.0
    }
}

class NASAPowerError(Exception):
    pass

class NASAPowerProvider:
    """
    NASA POWER Monthly API client.
    Fetches genuine monthly meteorological series (MERRA-2 reanalysis based).
    """

    @staticmethod
    def validate_coordinates(lat: float, lon: float):
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude {lat} out of valid range [-90, +90].")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(f"Longitude {lon} out of valid range [-180, +180].")

    @staticmethod
    def validate_years(start_year: int, end_year: int):
        current_year = datetime.datetime.utcnow().year
        if start_year < 1981:
            raise ValueError("NASA POWER monthly record starts in 1981.")
        if end_year > current_year:
            raise ValueError(f"End year cannot exceed current year ({current_year}).")
        if start_year > end_year:
            raise ValueError(f"Start year ({start_year}) cannot be after end year ({end_year}).")

    async def fetch_monthly_data(
        self,
        latitude: float,
        longitude: float,
        start_year: int,
        end_year: int,
        parameters: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query NASA POWER monthly point API.
        """
        self.validate_coordinates(latitude, longitude)
        self.validate_years(start_year, end_year)

        if not parameters:
            parameters = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"]
        else:
            invalid = [p for p in parameters if p not in SUPPORTED_PARAMETERS]
            if invalid:
                raise ValueError(f"Unsupported NASA POWER parameter(s): {invalid}")

        params = {
            "parameters": ",".join(parameters),
            "community": "RE",
            "longitude": f"{longitude:.4f}",
            "latitude": f"{latitude:.4f}",
            "start": str(start_year),
            "end": str(end_year),
            "format": "JSON"
        }

        retrieval_timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        try:
            async with httpx.AsyncClient(timeout=settings.NASA_POWER_TIMEOUT) as client:
                response = await client.get(settings.NASA_POWER_BASE_URL, params=params)
                
                if response.status_code != 200:
                    raise NASAPowerError(
                        f"NASA POWER API returned HTTP {response.status_code}: {response.text[:200]}"
                    )
                
                data = response.json()
        except httpx.RequestError as e:
            raise NASAPowerError(f"Network error contacting NASA POWER service: {str(e)}")

        # Extract features and properties
        properties = data.get("properties", {})
        parameter_data = properties.get("parameter", {})

        cleaned_data: Dict[str, Dict[str, float]] = {}
        missing_count: Dict[str, int] = {}
        nasa_annual_aggregates: Dict[str, Dict[int, float]] = {}

        for param in parameters:
            raw_series = parameter_data.get(param, {})
            cleaned_series = {}
            annual_13 = {}
            missings = 0
            
            for key, val in raw_series.items():
                # NASA POWER monthly format: YYYYMM (13 is annual aggregate, e.g. 202013)
                if len(key) == 6:
                    if key.endswith("13"):
                        try:
                            f_val = float(val)
                            if f_val > -900.0:
                                annual_13[int(key[:4])] = round(f_val, 4)
                        except (ValueError, TypeError):
                            pass
                    else:
                        if val is None or float(val) <= -900.0:
                            cleaned_series[key] = None
                            missings += 1
                        else:
                            cleaned_series[key] = round(float(val), 3)

            cleaned_data[param] = cleaned_series
            missing_count[param] = missings
            nasa_annual_aggregates[param] = annual_13

        return {
            "source": "NASA POWER / MERRA-2 (Monthly Aggregations)",
            "provider": "NASA Langley Research Center",
            "retrieval_timestamp": retrieval_timestamp,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "temporal_coverage": {"start_year": start_year, "end_year": end_year},
            "parameters": {
                p: {
                    **SUPPORTED_PARAMETERS[p],
                    "missing_observations": missing_count[p],
                    "total_months": len(cleaned_data[p]),
                    "series": cleaned_data[p],
                    "nasa_annual_aggregates": nasa_annual_aggregates[p]
                }
                for p in parameters
            },
            "citation": "NASA Prediction of Worldwide Energy Resources (POWER) Project, NASA Langley Research Center."
        }

