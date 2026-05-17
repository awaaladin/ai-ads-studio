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
        str(variant.get(k, "")) for k in ("headline", "body", "cta")
    )
    return moderate_text(combined)


def apply_disclaimer(variants: list[dict]) -> list[dict]:
    for v in variants:
        v.setdefault("meta", {})
        if isinstance(v["meta"], dict):
            v["meta"]["ai_disclaimer"] = DISCLAIMER
    return variants
