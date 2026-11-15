from typing import Dict, Any, List
import pandas as pd

class ScientificValidator:
    @staticmethod
    def validate_investigation_inputs(
        latitude: float,
        longitude: float,
        start_year: int,
        end_year: int,
        parameters: List[str]
    ) -> List[str]:
        errors = []
        if not (-90.0 <= latitude <= 90.0):
            errors.append(f"Latitude must be between -90 and 90. Given: {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            errors.append(f"Longitude must be between -180 and 180. Given: {longitude}")
        if start_year < 1981:
            errors.append(f"Start year cannot precede 1981 (NASA POWER baseline). Given: {start_year}")
        if start_year > end_year:
            errors.append(f"Start year ({start_year}) must precede or equal end year ({end_year})")
        if not parameters:
            errors.append("At least one meteorological variable must be selected.")
        return errors

