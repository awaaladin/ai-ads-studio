"""Normalize and trim LLM ad variant output."""

import re

MAX_HEADLINE = 80
MAX_BODY = 280
MAX_CTA = 40


def _clean_text(value: str) -> str:
    if not value:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^[\"']|[\"']$", "", text)
    return text.strip()


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    cut = value[: limit - 1].rsplit(" ", 1)[0]
    return (cut or value[: limit - 1]).rstrip(".,;") + "…"


def normalize_variant(raw: dict) -> dict | None:
    if not isinstance(raw, dict):
        return None
    headline = _clean_text(
        raw.get("headline") or raw.get("title") or raw.get("hook") or ""
    )
    body = _clean_text(
        raw.get("primary_text") or raw.get("body") or raw.get("description") or ""
    )
    cta = _clean_text(
        raw.get("call_to_action") or raw.get("cta") or raw.get("CTA") or "Learn More"
    )
    if not headline and not body:
        return None
    if not headline:
        headline = _truncate(body, 60)
    if not body:
        body = headline
    return {
        "headline": _truncate(headline, MAX_HEADLINE),
        "body": _truncate(body, MAX_BODY),
        "primary_text": _truncate(body, MAX_BODY),
        "cta": _truncate(cta, MAX_CTA),
        "call_to_action": _truncate(cta, MAX_CTA),
    }


def normalize_variants(
    raw_variants: list,
    *,
    min_count: int = 3,
    max_count: int = 5,
) -> list[dict]:
    cleaned: list[dict] = []
    seen_headlines: set[str] = set()
    for item in raw_variants or []:
        norm = normalize_variant(item)
        if not norm:
            continue
        key = norm["headline"].lower()
        if key in seen_headlines:
            continue
        seen_headlines.add(key)
        cleaned.append(norm)
        if len(cleaned) >= max_count:
            break
    return cleaned[:max_count] if cleaned else []
