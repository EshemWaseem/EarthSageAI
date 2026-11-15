import os
import asyncio
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.services.ai_service import GeminiResearchAssistant

client = TestClient(app)

def test_settings_gemini_precedence_and_autodetect():
    """Verify settings correctly detect GEMINI_API_KEY or GOOGLE_API_KEY and auto-enable provider."""
    # Scenario A: GEMINI_API_KEY is present
    s1 = Settings(_env_file=None, GEMINI_API_KEY="test-gemini-key", GOOGLE_API_KEY=None, AI_PROVIDER=None, JWT_SECRET_KEY="test")
    assert s1.GEMINI_API_KEY == "test-gemini-key"
    assert s1.AI_PROVIDER == "gemini"
    assert s1.GEMINI_MODEL == "gemini-3.8-flash"

    # Scenario B: GOOGLE_API_KEY is present, GEMINI_API_KEY is absent
    s2 = Settings(_env_file=None, GEMINI_API_KEY=None, GOOGLE_API_KEY="test-google-key", AI_PROVIDER=None, JWT_SECRET_KEY="test")
    assert s2.GEMINI_API_KEY == "test-google-key"
    assert s2.AI_PROVIDER == "gemini"

    # Scenario C: API key present, but AI_PROVIDER explicitly set to none
    s3 = Settings(_env_file=None, GEMINI_API_KEY="test-gemini-key", AI_PROVIDER="none", JWT_SECRET_KEY="test")
    assert s3.GEMINI_API_KEY == "test-gemini-key"
    assert s3.AI_PROVIDER == "none"

    # Scenario D: No keys configured
    s4 = Settings(_env_file=None, GEMINI_API_KEY=None, GOOGLE_API_KEY=None, AI_PROVIDER=None, JWT_SECRET_KEY="test")
    assert s4.GEMINI_API_KEY is None
    assert s4.AI_PROVIDER == "none"

def test_ai_status_endpoint_never_leaks_secrets():
    """Verify GET /api/v1/ai/status returns status structure and never leaks API keys."""
    res = client.get("/api/v1/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "available" in data
    assert "provider" in data
    assert "message" in data
    
    # Assert no secret tokens exist in response
    raw_text = res.text
    assert "AIzaSy" not in raw_text

def test_extract_json_helper():
    """Verify _extract_json parses raw JSON, fenced markdown, and surrounded prose."""
    # Clean json
    assert GeminiResearchAssistant._extract_json('{"key": "val"}') == {"key": "val"}
    
    # Markdown fence
    fence = "```json\n{\"title\": \"Study 1\", \"val\": 42}\n```"
    assert GeminiResearchAssistant._extract_json(fence) == {"title": "Study 1", "val": 42}
    
    # Surrounding commentary
    commentary = "Here is the formulated plan:\n{\"parameters\": [\"T2M\"]}\nLet me know if you need more!"
    assert GeminiResearchAssistant._extract_json(commentary) == {"parameters": ["T2M"]}

def test_fallback_plan_deterministic():
    """Verify offline / missing key planner generates complete valid research plan."""
    assistant = GeminiResearchAssistant()
    assistant._client = None
    
    plan = asyncio.run(assistant.plan_investigation("How has extreme heat and rainfall changed in Lahore?"))
    assert plan["is_ai_generated"] is False
    assert plan["location_name"] == "Lahore"
    assert "T2M" in plan["parameters"]
    assert "PRECTOTCORR" in plan["parameters"]
    assert plan["start_year"] == 1991
    assert plan["end_year"] == 2020
    assert "parameter_justifications" in plan

def test_fallback_explanation_deterministic():
    """Verify offline explanation produces structured scientific narrative."""
    assistant = GeminiResearchAssistant()
    assistant._client = None
    
    summary = {
        "id": "test-inv-001",
        "title": "Lahore Temperature Analysis",
        "location_name": "Lahore",
        "start_year": 1991,
        "end_year": 2020,
        "findings": [{"id": "f1", "summary": "Statistically significant warming detected."}],
        "statistical_metrics": {"T2M": {"descriptive": {"sample_size": 360}}}
    }
    
    exp = asyncio.run(assistant.explain_findings(summary))
    assert exp["is_ai_generated"] is False
    assert "Lahore" in exp["plain_language_summary"]
    assert "statistical_deep_dive" in exp
    assert "physical_mechanisms" in exp
    assert "scientific_limitations" in exp
    assert len(exp["recommended_follow_ups"]) >= 1

def test_gemini_error_resilience():
    """Verify API exceptions (503, 429, timeout) gracefully trigger deterministic fallback without 500 error."""
    assistant = GeminiResearchAssistant()
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("503 UNAVAILABLE: Model overloaded")
    assistant._client = mock_client
    
    # Should catch exception and return fallback plan
    plan = asyncio.run(assistant.plan_investigation("What is the trend in Lahore?"))
    assert plan["is_ai_generated"] is False
    assert plan["location_name"] == "Lahore"
    
    # Should catch exception and return fallback explanation
    summary = {
        "title": "Lahore Study",
        "location_name": "Lahore",
        "start_year": 1991,
        "end_year": 2020,
        "findings": []
    }
    exp = asyncio.run(assistant.explain_findings(summary))
    assert exp["is_ai_generated"] is False
    assert "Lahore" in exp["plain_language_summary"]
