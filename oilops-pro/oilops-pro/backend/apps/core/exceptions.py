from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Normalise error payloads to {"detail": ..., "errors": ...}."""
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and "detail" not in response.data:
        response.data = {"detail": "Validation failed.", "errors": response.data}
    elif response is not None and isinstance(response.data, list):
        response.data = {"detail": "Validation failed.", "errors": response.data}
    return response
