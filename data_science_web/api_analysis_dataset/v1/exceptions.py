from rest_framework.exceptions import ValidationError, ParseError
from rest_framework import status


class UnrecognizedFields(ParseError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Unrecognized Field'


class CannotCreateArchive(ValidationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'error'


class CannotCreateAnalysis(ValidationError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'error'
