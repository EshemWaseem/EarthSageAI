from typing import List, Optional
from fastapi import APIRouter
from app.providers.nasa_power import SUPPORTED_PARAMETERS

router = APIRouter(prefix="/datasets", tags=["datasets"])

AVAILABLE_DATASETS = [
    {
        "id": "nasa-power-merra2",
        "name": "NASA POWER / MERRA-2 Modern-Era Retrospective Analysis",
        "provider": "NASA Langley Research Center",
        "collectionPeriod": "1981 - Present (Monthly Continuous)",
        "geographicCoverage": "Global grid (0.5° x 0.625° latitude/longitude)",
        "resolution": "Single Point / Spatial Grid (MERRA-2 atmospheric assimilation)",
        "url": "https://power.larc.nasa.gov",
        "doi": "10.5067/POWER/MERRA2_MONTHLY",
        "status": "active_live_ingestion",
        "retrievalTimestamp": "Continuous Automated Sync (REST API)",
        "limitations": "Model-assimilated reanalysis estimates derived from NASA satellite and atmospheric assimilation flux, not direct in-situ ground station thermistors."
    },
    {
        "id": "nasa-giovanni",
        "name": "NASA Giovanni (GES DISC Remote Sensing Infrastructure)",
        "provider": "NASA Goddard Earth Sciences Data & Information Services Center",
        "collectionPeriod": "Multi-Mission Archive (1979 - Present)",
        "geographicCoverage": "Global gridded remote sensing parameters",
        "resolution": "Multi-sensor (0.1° to 1.0° spatial resolution)",
        "url": "https://giovanni.gsfc.nasa.gov/giovanni/",
        "doi": "10.5067/GESDISC/GIOVANNI",
        "status": "challenge_resource_catalog",
        "retrievalTimestamp": "NASA Space Apps 2024 Challenge Resource",
        "limitations": "Official challenge listed resource for exploratory visual analysis. Programmatic API access requires NASA Earthdata Login (EDL) and asynchronous OPeNDAP extraction."
    },
    {
        "id": "nasa-appeears",
        "name": "NASA AppEEARS (Analysis Ready Samples Subsetting)",
        "provider": "NASA LP DAAC / USGS EROS Center",
        "collectionPeriod": "2000 - Present (MODIS, VIIRS, Landsat)",
        "geographicCoverage": "Global terrestrial points and polygons",
        "resolution": "250m to 1000m land products",
        "url": "https://appeears.earthdatacloud.nasa.gov/",
        "doi": "10.5067/APPEEARS/V1",
        "status": "challenge_resource_catalog",
        "retrievalTimestamp": "NASA Space Apps 2024 Challenge Resource",
        "limitations": "Official challenge listed resource for analysis-ready sample extraction. Operates as an asynchronous batch queue requiring Earthdata Login authentication and task polling."
    },
    {
        "id": "copernicus-era5",
        "name": "ECMWF ERA5 Atmospheric Reanalysis",
        "provider": "Copernicus Climate Change Service (C3S)",
        "collectionPeriod": "1979 - Present",
        "geographicCoverage": "Global (0.25° x 0.25° grid)",
        "resolution": "Hourly / Monthly aggregates, ~31km horizontal",
        "url": "https://cds.climate.copernicus.eu",
        "doi": "10.24381/cds.bd0915c6",
        "status": "reference_catalog",
        "retrievalTimestamp": "Reference Catalog Entry",
        "limitations": "Grid cell smoothing over complex mountainous topography."
    },
    {
        "id": "usgs-landsat9",
        "name": "USGS Landsat 9 OLI-2 / TIRS-2",
        "provider": "U.S. Geological Survey / NASA",
        "collectionPeriod": "2021 - Present",
        "geographicCoverage": "Global terrestrial surface",
        "resolution": "30m multispectral, 15m panchromatic",
        "url": "https://earthexplorer.usgs.gov",
        "doi": "10.5066/P9OGBGM6",
        "status": "reference_catalog",
        "retrievalTimestamp": "Reference Catalog Entry",
        "limitations": "Subject to cloud cover obscuration; 16-day revisit cadence."
    }
]

@router.get("")
def get_datasets():
    return AVAILABLE_DATASETS

@router.get("/nasa-power/parameters")
def get_nasa_power_parameters():
    return SUPPORTED_PARAMETERS

