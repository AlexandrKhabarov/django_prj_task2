from rest_framework.views import exception_handler
import logging
import traceback

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    logging.exception(''.join(traceback.format_tb(exc.__traceback__)))
    response = exception_handler(exc, context)

    return response
