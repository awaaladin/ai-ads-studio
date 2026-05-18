"""Platform-aware prompt construction for ad variant generation."""

PLATFORM_STYLE = {
    "meta": (
        "Meta (Facebook/Instagram): scroll-stopping hook in the headline, conversational "
        "primary text (1–3 short sentences), strong social proof or urgency, emoji optional "
        "but sparing. Optimize for feed ads."
    ),
    "tiktok": (
        "TikTok: casual, trend-aware, speak directly to camera energy in text. Short punchy "
        "lines, curiosity-driven hook, Gen-Z friendly without being cringe."
    ),
    "linkedin": (
        "LinkedIn: professional, credible, value-led. Lead with business outcome or insight. "
        "Avoid hype; use clear ROI or expertise angle."
    ),
    "youtube": (
        "YouTube: curiosity gap in headline, benefit-focused primary text, clear next step. "
        "Works for in-stream or discovery ads."
    ),
    "google": (
        "Google Ads: concise headline (≤30 chars ideal), keyword-aware primary text, "
        "action-oriented CTA. Match search intent."
    ),
}

TONE_GUIDANCE = {
    "friendly": "Warm, approachable, helpful — like a trusted friend recommending a product.",
    "playful": "Light, witty, fun — use wordplay or humor where appropriate.",
    "stylish": "Premium, aspirational, polished — luxury or lifestyle brand voice.",
    "bold": "Direct, confident, high-energy — strong claims backed by specifics.",
}


def platform_guide(platform: str) -> str:
    key = (platform or "meta").lower()
    return PLATFORM_STYLE.get(key, PLATFORM_STYLE["meta"])


def tone_guide(tone: str) -> str:
    key = (tone or "friendly").lower()
    return TONE_GUIDANCE.get(key, TONE_GUIDANCE["friendly"])


def build_variants_prompt(brief_context: dict, variant_count: int) -> str:
    product = brief_context.get("product_service", "")
    audience = brief_context.get("audience", "")
    tone = brief_context.get("tone", "friendly")
    platform = brief_context.get("platform", "meta")
    key_message = brief_context.get("key_message", "")

    return f"""You are a senior performance marketer and ad copywriter.

Create exactly {variant_count} DISTINCT ad variants for this brief. Each variant must use a different angle (benefit, social proof, urgency, question hook, or storytelling).

PRODUCT/SERVICE: {product}
TARGET AUDIENCE: {audience}
KEY MESSAGE: {key_message or "Infer from product and audience."}
TONE: {tone_guide(tone)}
PLATFORM STYLE: {platform_guide(platform)}

RULES:
- Return ONLY valid JSON, no markdown or explanation.
- Each variant MUST have: headline, primary_text, call_to_action
- headline: max 80 characters, punchy
- primary_text: 1–3 sentences, max 280 characters, platform-appropriate
- call_to_action: 2–4 words (e.g. "Shop Now", "Learn More")
- Vary tone intensity across variants while staying on-brand
- Do NOT repeat the same headline or opening line across variants

Return strictly as JSON:
{{
  "variants": [
    {{
      "headline": "...",
      "primary_text": "...",
      "call_to_action": "..."
    }}
  ]
}}"""
