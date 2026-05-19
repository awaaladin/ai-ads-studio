import logging
import os

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _normalize_errors(data):
    if isinstance(data, dict):
        if "detail" in data and "error" not in data:
            detail = data["detail"]
            if isinstance(detail, str):
                data = {**data, "error": detail}
            elif isinstance(detail, list) and detail:
                data = {**data, "error": str(detail[0])}
        elif "error" in data and "detail" not in data:
            data = {**data, "detail": data["error"]}
    return data


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            response.data = _normalize_errors(response.data)
        return response

    logger.exception("Unhandled API error")
    detail = "An unexpected server error occurred."
    payload = {
        "error": detail,
        "detail": detail,
        "error_type": exc.__class__.__name__,
    }
    if settings.DEBUG or os.getenv("EXPOSE_API_ERRORS", "").lower() in ("1", "true", "yes"):
        payload["debug"] = str(exc)[:500]

    return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
