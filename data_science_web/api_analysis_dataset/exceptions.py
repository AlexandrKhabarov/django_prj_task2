from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status


class CustomHTTPException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'The request could not be completed.'

    def __init__(self, detail=None, field=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_text(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}
