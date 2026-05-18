import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from django.conf import settings
from groq import Groq

from .output_cleaner import normalize_variants
from .prompts import build_variants_prompt


class LLMServiceError(Exception):
    pass


def _variant_count() -> int:
    count = int(getattr(settings, "GENERATION_VARIANT_COUNT", 4))
    return max(3, min(5, count))


def _client():
    if not settings.GROQ_API_KEY:
        raise LLMServiceError("GROQ_API_KEY is not configured.")
    return Groq(api_key=settings.GROQ_API_KEY)


def _call_groq_json(prompt: str) -> dict:
    client = _client()
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a JSON-only ad copy API. Respond with valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        model=settings.GROQ_MODEL,
        response_format={"type": "json_object"},
        temperature=0.85,
    )
    content = response.choices[0].message.content
    return json.loads(content)


def _with_timeout(fn, *args, timeout: int | None = None, **kwargs):
    seconds = timeout or int(getattr(settings, "GROQ_TIMEOUT_SECONDS", 45))
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=seconds)
        except FuturesTimeoutError as exc:
            raise LLMServiceError("Generation timed out. Please try again.") from exc


def _fallback_variants(brief_context: dict, variant_count: int | None = None) -> list[dict]:
    """Template variants when GROQ is unavailable (local dev / demos)."""
    count = variant_count or _variant_count()
    product = brief_context.get("product_service") or "your product"
    audience = brief_context.get("audience") or "your audience"
    tone = brief_context.get("tone") or "friendly"
    platform = brief_context.get("platform") or "meta"
    key = brief_context.get("key_message") or f"Discover why {audience} love {product}."
    bases = [
        {
            "headline": f"{product} — built for {audience}",
            "primary_text": f"{key} Tone: {tone}. Optimized for {platform}.",
            "call_to_action": "Shop now",
        },
        {
            "headline": f"Why {audience} choose {product}",
            "primary_text": f"Stand out on {platform} with messaging that feels {tone}. {key}",
            "call_to_action": "Learn more",
        },
        {
            "headline": f"See what {audience} are saying",
            "primary_text": f"Real results start with the right message. {key}",
            "call_to_action": "Get started",
        },
        {
            "headline": f"Ready for better {platform} ads?",
            "primary_text": f"{product} meets {audience} where they are — {tone} and clear. {key}",
            "call_to_action": "Try it free",
        },
        {
            "headline": f"Don't miss out on {product}",
            "primary_text": f"Limited attention window — make it count. {key}",
            "call_to_action": "Claim offer",
        },
    ]
    return normalize_variants(bases[:count], min_count=3, max_count=count)


def generate_ad_copy(business_context: dict, assets_text: str = "") -> dict:
    prompt = f"""
You are an expert AI marketing assistant. Given the business context and optional asset text,
generate ad copy, social media posts, and brochure content.

Business Context:
{json.dumps(business_context, indent=2)}

Extracted Text from Assets (if any):
{assets_text or "None"}

Return strictly as JSON:
{{
  "ad_copy": "Headline, body, CTA as plain text",
  "social_posts": ["post1", "post2", "post3"],
  "brochure_content": "Detailed brochure text"
}}
"""
    try:
        return _with_timeout(_call_groq_json, prompt)
    except LLMServiceError:
        raise
    except Exception as exc:
        raise LLMServiceError(str(exc)) from exc


def generate_ad_variants(brief_context: dict, variant_count: int | None = None) -> list[dict]:
    count = variant_count or _variant_count()
    if not settings.GROQ_API_KEY:
        return _fallback_variants(brief_context, count)

    prompt = build_variants_prompt(brief_context, count)
    try:
        data = _with_timeout(_call_groq_json, prompt)
        variants = normalize_variants(
            data.get("variants", []),
            min_count=3,
            max_count=count,
        )
        if len(variants) < 3:
            return _fallback_variants(brief_context, count)
        return variants
    except LLMServiceError:
        return _fallback_variants(brief_context, count)
    except Exception:
        return _fallback_variants(brief_context, count)
