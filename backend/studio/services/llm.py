import json

from django.conf import settings
from groq import Groq


class LLMServiceError(Exception):
    pass


def _client():
    if not settings.GROQ_API_KEY:
        raise LLMServiceError("GROQ_API_KEY is not configured.")
    return Groq(api_key=settings.GROQ_API_KEY)


def _fallback_variants(brief_context: dict, variant_count: int = 3) -> list[dict]:
    """Template variants when GROQ is unavailable (local dev / demos)."""
    product = brief_context.get("product_service") or "your product"
    audience = brief_context.get("audience") or "your audience"
    tone = brief_context.get("tone") or "friendly"
    platform = brief_context.get("platform") or "social"
    key = brief_context.get("key_message") or f"Discover why {audience} love {product}."
    bases = [
        {
            "headline": f"{product} — built for {audience}",
            "body": f"{key}\n\nTone: {tone}. Optimized for {platform}.",
            "cta": "Shop now",
        },
        {
            "headline": f"Why {audience} choose {product}",
            "body": f"Stand out on {platform} with messaging that feels {tone}.\n\n{key}",
            "cta": "Learn more",
        },
        {
            "headline": f"Limited offer: {product}",
            "body": f"Don't miss this — {key}\n\nPerfect for {audience} on {platform}.",
            "cta": "Get started",
        },
    ]
    return bases[:variant_count]


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
        client = _client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_MODEL,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except LLMServiceError:
        raise
    except Exception as exc:
        raise LLMServiceError(str(exc)) from exc


def generate_ad_variants(brief_context: dict, variant_count: int = 3) -> list[dict]:
    if not settings.GROQ_API_KEY:
        return _fallback_variants(brief_context, variant_count)

    prompt = f"""
You are an expert ad copywriter. Create {variant_count} distinct ad variants for this brief.

Brief:
{json.dumps(brief_context, indent=2)}

Return strictly as JSON:
{{
  "variants": [
    {{"headline": "...", "body": "...", "cta": "..."}}
  ]
}}
"""
    try:
        client = _client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_MODEL,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        variants = data.get("variants", [])
        if not variants:
            return _fallback_variants(brief_context, variant_count)
        return variants[:variant_count]
    except LLMServiceError:
        return _fallback_variants(brief_context, variant_count)
    except Exception:
        return _fallback_variants(brief_context, variant_count)
