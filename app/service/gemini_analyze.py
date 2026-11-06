import json
import re
from google import genai
from google.genai import types
try:
    from .prompt import CONTRACT_ANALYSIS_PROMPT
    from ..config import GEMINI_API_KEY
    from ..models import ClauseAnalysis, RiskFlag, AnalysisResult
except ImportError:
    from service.prompt import CONTRACT_ANALYSIS_PROMPT
    from config import GEMINI_API_KEY
    from models import ClauseAnalysis, RiskFlag, AnalysisResult

GEMINI_MODEL = "gemini-3.8-flash"

async def analyze_contract(contract_id: str, text_content: str):
    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text = text_content[:15000])

    if not GEMINI_API_KEY:
        raise ValueError("GOOGLE_AI_API_KEY is not configured")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4096,
            response_mime_type="application/json",
        ),
    )

    raw_text = response.text
    if not raw_text:
        raise ValueError("Gemini returned an empty analysis response")

    raw_text = raw_text.strip()
    fence_match = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```",
        raw_text,
        re.DOTALL | re.IGNORECASE,
    )
    if fence_match:
        raw_text = fence_match.group(1).strip()

    analysis_data = json.loads(raw_text)

    key_clauses = [
        ClauseAnalysis(**clause)
        for clause in analysis_data.get("key_clauses", [])
    ]

    risk_flags = [
        RiskFlag(**risk)
        for risk in analysis_data.get("risk_flags", [])
    ]

    return AnalysisResult(
        contract_id=contract_id,
        summary=analysis_data.get("summary", ""),
        contract_type=analysis_data.get("contract_type", "unknown"),
        key_clauses=key_clauses,
        risk_flags=risk_flags,
        overall_risk_level=analysis_data.get("overall_risk_level", "low"),
        recommendations=analysis_data.get("recommendations", []),
    )