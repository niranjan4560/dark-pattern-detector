import os
import json
import re
from typing import Dict, List, Any

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Safe Gemini import — works with or without key
GEMINI_AVAILABLE = False
genai = None

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        print("✅ Gemini AI configured")
    except Exception as e:
        print(f"⚠️  Gemini setup error: {e} — falling back to mock analysis")
else:
    print("⚠️  GEMINI_API_KEY not set — using mock analysis (add key to .env)")

SYSTEM_PROMPT = """You are an expert UX researcher specializing in identifying dark patterns —
manipulative UI/UX design techniques used by websites to trick users.

Analyze website content and identify specific dark patterns with evidence.

DARK PATTERN TYPES TO CHECK:
1. fake_urgency — False countdown timers, fake low stock warnings
2. hidden_costs — Fees revealed only at final checkout
3. trick_questions — Pre-selected checkboxes, confusing opt-out language
4. roach_motel — Easy signup, very hard to cancel
5. misdirection — Tiny decline buttons, important info in small grey text
6. forced_continuity — Free trials that silently auto-renew
7. social_proof_manipulation — Fake viewer counts, fabricated reviews
8. confirm_shaming — Guilt-trip decline language
9. disguised_ads — Sponsored content styled as organic results
10. privacy_zuckering — Default maximum data sharing, vague consent

Respond ONLY in valid JSON. No markdown. No explanation outside JSON."""


# Try model names in order — newest first, falls back if one is deprecated/unavailable
MODEL_CANDIDATES = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]


async def analyze_with_gemini(page_content: str, url: str) -> Dict[str, Any]:
    """Analyze page content using Gemini AI"""

    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return _mock_analysis(url)

    last_error = None
    content = page_content[:8000] if len(page_content) > 8000 else page_content

    for model_name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
            result = await _run_gemini_prompt(model, content, url)
            if result is not None:
                print(f"✅ Gemini analysis succeeded using model: {model_name}")
                return result
        except Exception as e:
            last_error = e
            print(f"⚠️  Model {model_name} failed: {e}")
            continue

    print(f"⚠️  All Gemini models failed. Last error: {last_error} — using mock")
    return _mock_analysis(url)


async def _run_gemini_prompt(model, content: str, url: str):
    """Run the actual prompt against a given model instance. Returns None on failure to trigger fallback."""
    try:
        prompt = f"""Analyze this website content for dark patterns.

URL: {url}

CONTENT:
{content}

Return ONLY this JSON structure (no markdown, no backticks):
{{
  "page_title": "page title or domain",
  "industry_category": "e-commerce or travel or subscription or food-delivery or social-media or finance or other",
  "overall_credibility_score": 75,
  "summary": "2-3 sentence assessment of the website practices",
  "dark_patterns": [
    {{
      "pattern_type": "fake_urgency",
      "pattern_name": "Descriptive name of the specific pattern",
      "severity": "High",
      "confidence_score": 0.92,
      "evidence": "Exact text or element found on the page",
      "location_hint": "Where on the page (header/checkout/popup/footer)",
      "user_impact": "How this harms the user"
    }}
  ],
  "positive_practices": ["List of good practices found"],
  "recommendations": ["Specific actionable improvements"]
}}

Score guide: 80-100=Safe, 60-79=Caution, 40-59=Suspicious, 0-39=Dangerous
Return ONLY the JSON object."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Strip markdown if Gemini wraps response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Fix trailing commas (common Gemini output issue)
        response_text = re.sub(r',\s*([}\]])', r'\1', response_text)

        result = json.loads(response_text)

        # Ensure all required fields exist
        result.setdefault("page_title", url)
        result.setdefault("industry_category", "other")
        result.setdefault("overall_credibility_score", 70)
        result.setdefault("summary", "Analysis complete.")
        result.setdefault("dark_patterns", [])
        result.setdefault("positive_practices", [])
        result.setdefault("recommendations", [])

        return result

    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        raise
    except Exception as e:
        print(f"⚠️  Gemini call error: {e}")
        raise


async def analyze_text_content(text: str, url: str) -> Dict[str, Any]:
    """Analyze plain text / pasted content"""
    return await analyze_with_gemini(text, url)


def calculate_credibility_score(patterns: List[Dict]) -> float:
    """Calculate credibility score from detected patterns"""
    if not patterns:
        return 90.0

    weights = {"Critical": 40, "High": 25, "Medium": 15, "Low": 5}
    deduction = sum(
        weights.get(p.get("severity", "Low"), 5) * float(p.get("confidence_score", 0.5))
        for p in patterns
    )
    return round(max(0.0, 100.0 - deduction), 1)


def get_severity_label(score: float) -> str:
    """Map credibility score to label"""
    if score >= 80: return "Safe"
    if score >= 60: return "Caution"
    if score >= 40: return "Suspicious"
    return "Dangerous"


def _mock_analysis(url: str) -> Dict[str, Any]:
    """
    Realistic mock analysis — used when no Gemini key is set.
    Clearly labeled as demo data so users know to add their key.
    """
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    return {
        "page_title": f"{domain}",
        "industry_category": "e-commerce",
        "overall_credibility_score": 42,
        "summary": (
            f"DEMO DATA: Analysis of {domain} shows several concerning patterns. "
            "Add your Gemini API key to .env for real AI-powered analysis. "
            "Get a free key at aistudio.google.com/app/apikey"
        ),
        "dark_patterns": [
            {
                "pattern_type": "fake_urgency",
                "pattern_name": "False Countdown Timer",
                "severity": "High",
                "confidence_score": 0.89,
                "evidence": "DEMO: Countdown timer with no real deadline found on product pages",
                "location_hint": "Product page, above Add to Cart",
                "user_impact": "Creates artificial time pressure forcing rushed purchasing decisions"
            },
            {
                "pattern_type": "hidden_costs",
                "pattern_name": "Late-Stage Fee Disclosure",
                "severity": "High",
                "confidence_score": 0.85,
                "evidence": "DEMO: Convenience fee Rs.49 + packaging Rs.20 added only at final checkout",
                "location_hint": "Final checkout page",
                "user_impact": "Users invest time selecting items only to find total is higher"
            },
            {
                "pattern_type": "trick_questions",
                "pattern_name": "Pre-selected Marketing Consent",
                "severity": "Medium",
                "confidence_score": 0.76,
                "evidence": "DEMO: Newsletter checkbox pre-ticked during account creation",
                "location_hint": "Account registration form",
                "user_impact": "Users unknowingly consent to marketing communications"
            },
            {
                "pattern_type": "confirm_shaming",
                "pattern_name": "Guilt-Trip Decline Language",
                "severity": "Low",
                "confidence_score": 0.71,
                "evidence": "DEMO: Decline button reads: No thanks, I don't want to save money",
                "location_hint": "Promotional popup overlay",
                "user_impact": "Emotional manipulation to prevent users from declining offers"
            }
        ],
        "positive_practices": [
            "Clear return policy in footer",
            "SSL certificate present",
            "Contact information visible"
        ],
        "recommendations": [
            "Remove countdown timers unless tied to real deadlines",
            "Show all fees upfront on product pages",
            "Use neutral language for decline buttons",
            "Default marketing consent to unchecked"
        ]
    }
