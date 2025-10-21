from rest_framework.exceptions import APIException



class ForbiddenException(APIException):
    status_code = 403

    def __init__(self, data, code='permission_denied'):
        self.detail = {
            **data,
            "code": code
        }


class BadRequestException(APIException):
    status_code = 400

    def __init__(self, data, code='bad_request'):
        self.detail = {
            **data,
            "code": code
        }
