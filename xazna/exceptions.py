from rest_framework.exceptions import APIException


class HTTPAuthException(APIException):
    status_code = 401

    def __init__(self, message='Authentication credentials were not provided.', code='not_authenticated'):
        self.detail = {
            "message": message,
            "code": code
        }


class HTTPPermissionException(APIException):
    status_code = 403

    def __init__(self, message='Permission denied', code='permission_denied'):
        self.detail = {
            "message": message,
            "code": code
        }


class ValidationException(APIException):
    status_code = 400

    def __init__(self, data, code='bad_request'):
        self.detail = {
            **data,
            "code": code
        }
