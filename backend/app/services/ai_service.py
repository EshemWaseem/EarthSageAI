import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.providers.nasa_power import SUPPORTED_PARAMETERS

logger = logging.getLogger(__name__)

# Known climatological coordinate anchors for robust fallback parsing
LOCATION_PRESETS = {
    "lahore": {"lat": 31.5497, "lng": 74.3436, "name": "Lahore", "country": "Pakistan", "region": "Punjab"},
    "karachi": {"lat": 24.8607, "lng": 67.0011, "name": "Karachi", "country": "Pakistan", "region": "Sindh"},
    "islamabad": {"lat": 33.6844, "lng": 73.0479, "name": "Islamabad", "country": "Pakistan", "region": "Federal"},
    "geneva": {"lat": 46.2044, "lng": 6.1432, "name": "Geneva", "country": "Switzerland", "region": "Geneva"},
    "nairobi": {"lat": -1.2921, "lng": 36.8219, "name": "Nairobi", "country": "Kenya", "region": "Nairobi"}
}

class GeminiResearchAssistant:
    """
    Scientific AI Research Assistant powered by Google Gemini API.
    Adheres strictly to scientific integrity rules:
    - Never fabricates or recalculates numerical values.
    - AI is supplied with genuine backend outputs.
    - Explicitly distinguishes observations, findings, and hypotheses.
    - Never describes correlation as causation.
    - Discloses all reanalysis and grid-cell scope limitations.
    """

    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        self.provider = settings.AI_PROVIDER
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None

        if (self.provider == "gemini" or (self.provider != "none" and self.api_key)) and self.api_key:
            try:
                from google import genai
                from google.genai import types
                self._client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(timeout=30.0)
                )
                logger.info(f"Initialized Google Gen AI Client with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gen AI Client: {e}")
                self._client = None

    def is_available(self) -> bool:
        if self._client is None and settings.GEMINI_API_KEY and settings.AI_PROVIDER != "none":
            self._init_client()
        return self._client is not None

    def get_status(self) -> Dict[str, Any]:
        available = self.is_available()
        return {
            "available": available,
            "provider": self.provider if available else "none",
            "model": self.model_name if available else None,
            "message": (
                f"Gemini AI Research Assistant active ({self.model_name})"
                if available
                else "Gemini AI is currently inactive. Configure GEMINI_API_KEY (or GOOGLE_API_KEY) in Render/backend environment to enable."
            )
        }

    async def plan_investigation(self, research_question: str) -> Dict[str, Any]:
        """
        Translates natural language scientific inquiry into a formal research plan.
        """
        if not self.is_available():
            return self._fallback_plan(research_question)

        prompt = f"""
You are an expert Earth System scientist for NASA Space Apps Challenge.
A researcher has submitted the following inquiry:
"{research_question}"

Formulate a rigorous scientific investigation plan using available NASA POWER monthly parameters:
Supported Parameters:
- T2M: Temperature at 2 Meters (°C)
- T2M_MAX: Maximum Temperature at 2 Meters (°C)
- T2M_MIN: Minimum Temperature at 2 Meters (°C)
- PRECTOTCORR: Precipitation Corrected (mm/day)

Respond ONLY with a valid JSON object with the following exact keys:
{{
  "title": "Concise scientific study title",
  "research_question": "Refined formal scientific research question",
  "hypothesis": "Testable working hypothesis with directional prediction",
  "location_name": "Target location name",
  "country": "Country name",
  "latitude": 31.5497,
  "longitude": 74.3436,
  "start_year": 1991,
  "end_year": 2020,
  "parameters": ["T2M", "PRECTOTCORR"],
  "parameter_justifications": {{
    "T2M": "Why temperature matters for this research question",
    "PRECTOTCORR": "Why precipitation flux matters for this research question"
  }}
}}
Ensure latitude is between -90 and 90, longitude between -180 and 180, and years between 1981 and 2023.
"""
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=30.0)
            )
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=config
            )
            text = (response.text or "").strip()
            parsed = self._extract_json(text)
            parsed["is_ai_generated"] = True
            parsed["ai_model"] = self.model_name
            return parsed
        except Exception as e:
            logger.warning(f"Gemini plan generation error: {e}. Falling back to deterministic plan.")
            return self._fallback_plan(research_question)

    async def explain_findings(self, investigation_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets validated non-parametric statistical results into peer-review scientific narrative.
        """
        if not self.is_available():
            return self._fallback_explanation(investigation_summary)

        prompt = f"""
You are a senior climatologist reviewing the following empirical analysis generated by EarthSage AI:

Investigation Title: {investigation_summary.get('title')}
Target Location: {investigation_summary.get('location_name')} ({investigation_summary.get('coordinates', {}).get('latitude')}°N, {investigation_summary.get('coordinates', {}).get('longitude')}°E)
Temporal Window: {investigation_summary.get('start_year')}–{investigation_summary.get('end_year')} (30 Years, 360 Months)
Data Source: NASA POWER / MERRA-2 Atmospheric Reanalysis

Statistical Findings:
{json.dumps(investigation_summary.get('findings', []), indent=2)}

Statistical Metrics & Autocorrelation:
{json.dumps(investigation_summary.get('statistical_metrics', {}), indent=2)}

Strict Scientific Rules:
1. Do NOT invent, recalculate, or alter any numbers. Use only the provided p-values, Kendall's tau, and Sen's slopes.
2. Clearly distinguish statistical significance (p < 0.05) from non-significance (p >= 0.05).
3. If annual MK is not significant, state clearly that no net annual monotonic trend was detected at the 95% confidence level.
4. Never describe correlation as causation.
5. Explicitly disclose that this represents a single MERRA-2 grid cell (0.5° x 0.625°), not a regional or national average.
6. Plainly explain Kendall's Tau, Sen's slope, and p-values for researchers and judges.

Respond ONLY with a valid JSON object with the following keys:
{{
  "plain_language_summary": "Comprehensive scientific executive summary",
  "statistical_deep_dive": "Explanation of p-values, Kendall's tau, Sen's slope units, and autocorrelation results",
  "physical_mechanisms": "Hypothesized atmospheric or climate dynamics consistent with these observations",
  "scientific_limitations": "Observational scope, reanalysis vs ground truth, and sample size caveats",
  "recommended_follow_ups": ["Follow-up research suggestion 1", "Follow-up research suggestion 2"]
}}
"""
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=30.0)
            )
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=config
            )
            text = (response.text or "").strip()
            parsed = self._extract_json(text)
            parsed["is_ai_generated"] = True
            parsed["ai_model"] = self.model_name
            parsed["disclaimer"] = "AI-Generated Scientific Interpretation (Advisory Only). All findings are derived from backend non-parametric statistical calculations."
            return parsed
        except Exception as e:
            logger.warning(f"Gemini explanation generation error: {e}. Falling back to template explanation.")
            return self._fallback_explanation(investigation_summary)

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """Extract and parse JSON object from model output."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        return json.loads(cleaned)

    def _fallback_plan(self, question: str) -> Dict[str, Any]:
        """Deterministic plan generator when AI is disabled."""
        q_lower = question.lower()
        
        # Match location
        loc = LOCATION_PRESETS["lahore"]
        for key, preset in LOCATION_PRESETS.items():
            if key in q_lower:
                loc = preset
                break

        # Match parameters
        params = []
        if any(w in q_lower for w in ["temp", "heat", "warm", "t2m", "climate"]):
            params.append("T2M")
        if any(w in q_lower for w in ["rain", "precip", "flood", "monsoon", "water"]):
            params.append("PRECTOTCORR")
        if not params:
            params = ["T2M", "PRECTOTCORR"]

        justifications = {}
        if "T2M" in params:
            justifications["T2M"] = "Surface air temperature at 2 meters represents the fundamental thermal energy state of the boundary layer."
        if "PRECTOTCORR" in params:
            justifications["PRECTOTCORR"] = "Corrected precipitation rate quantifies hydrological mass flux, capturing monsoon seasonality and dry spells."

        return {
            "title": f"Empirical Climatological Analysis: {loc['name']} (1991–2020)",
            "research_question": question if len(question) > 15 else f"How have meteorological parameters evolved at {loc['name']} over 1991–2020?",
            "hypothesis": f"Monotonic trends in {', '.join(params)} over 1991–2020 deviate significantly from the long-term climatological baseline.",
            "location_name": loc["name"],
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "start_year": 1991,
            "end_year": 2020,
            "parameters": params,
            "parameter_justifications": justifications,
            "is_ai_generated": False,
            "note": "Generated via deterministic EarthSage scientific planner (Gemini AI assistant inactive)."
        }

    def _fallback_explanation(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic scientific summary when AI is disabled."""
        findings = summary.get("findings", [])
        finding_summaries = [f.get("summary", "") for f in findings]

        return {
            "plain_language_summary": (
                f"Evaluation for {summary.get('location_name', 'target grid')} covering {summary.get('start_year', 1991)}–{summary.get('end_year', 2020)}. "
                + " ".join(finding_summaries)
            ),
            "statistical_deep_dive": (
                "Trend significance is evaluated via non-parametric Mann-Kendall tests against arithmetic day-weighted annual series. "
                "Sen's slope provides a median rate of change resistant to outliers. Autocorrelation is evaluated using multi-lag Ljung-Box diagnostic tests."
            ),
            "physical_mechanisms": (
                "Regional surface temperature and precipitation flux in South Asia are modulated by planetary-scale monsoon circulations, "
                "aerosol optical depth variations, and land-surface thermal feedbacks."
            ),
            "scientific_limitations": (
                "Analysis reflects single MERRA-2 assimilation grid cell estimates (0.5° x 0.625°), not direct ground weather station thermistors. "
                "Point observations should not be extrapolated as regional or national spatial averages."
            ),
            "recommended_follow_ups": [
                "Execute spatial neighborhood correlation across adjacent grid cells.",
                "Perform seasonal decomposition separating monsoon (JJAS) and winter (DJF) precipitation regimes."
            ],
            "is_ai_generated": False,
            "disclaimer": "Rule-based scientific synthesis generated from backend statistical engine (Gemini AI assistant inactive)."
        }

