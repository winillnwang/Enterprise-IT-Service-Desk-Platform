import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

logger = logging.getLogger("tickets")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.exception(
            "Unhandled API exception",
            exc_info=exc,
        )

        return Response(
            {
                "success": False,
                "message": "Internal server error.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data

    if isinstance(data, dict) and "detail" in data:
        response.data = {
            "success": False,
            "message": str(data["detail"]),
        }

        return response

    response.data = {
        "success": False,
        "errors": data,
    }

    return response
