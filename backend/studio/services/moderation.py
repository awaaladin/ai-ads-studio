"""Basic content policy checks before returning AI copy to clients."""

BLOCKED_PATTERNS = (
    "guaranteed cure",
    "get rich quick",
    "100% free money",
    "miracle weight loss",
    "click here now!!!",
    "act now or else",
)

DISCLAIMER = (
    "AI-generated copy. Review before publishing. You are responsible for compliance "
    "with ad platform policies and local laws."
)

INPUT_BLOCKED_PATTERNS = (
    "kill yourself",
    "how to make a bomb",
    "child abuse",
    "illegal drugs for sale",
)

DEMO_METRICS = {
    "demo_mode": True,
    "metrics_source": "simulated",
    "disclaimer": (
        "Campaign metrics are simulated for demo purposes only. "
        "Connect a real ad account for live performance data."
    ),
}


def moderate_text(text: str) -> tuple[bool, str | None]:
    if not text:
        return True, None
    lower = text.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lower:
            return False, f"Content blocked: policy violation ({pattern})."
    return True, None


def moderate_variant(variant: dict) -> tuple[bool, str | None]:
    combined = " ".join(
        str(variant.get(k, ""))
        for k in ("headline", "body", "primary_text", "cta", "call_to_action")
    )
    return moderate_text(combined)


def moderate_brief_input(brief_context: dict) -> tuple[bool, str | None]:
    combined = " ".join(
        str(brief_context.get(k, ""))
        for k in ("product_service", "audience", "key_message")
    )
    ok, reason = moderate_text(combined)
    if not ok:
        return ok, reason
    lower = combined.lower()
    for pattern in INPUT_BLOCKED_PATTERNS:
        if pattern in lower:
            return False, "Input blocked: harmful or invalid content."
    if len(combined.strip()) < 5:
        return False, "Input too short. Provide product and audience details."
    return True, None


def apply_disclaimer(variants: list[dict]) -> list[dict]:
    for v in variants:
        v.setdefault("meta", {})
        if isinstance(v["meta"], dict):
            v["meta"]["ai_disclaimer"] = DISCLAIMER
    return variants
