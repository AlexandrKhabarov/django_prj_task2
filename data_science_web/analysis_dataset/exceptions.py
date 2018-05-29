from rest_framework.exceptions import ParseError
from rest_framework import status


class UnrecognizedFields(ParseError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Unrecognized Field'
