from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


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
    return Response(
        {"error": "An unexpected server error occurred.", "detail": "An unexpected server error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
