import jwt
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

from accounts.models import CustomUserModel
from . import settings



class CoreMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            token = request.COOKIES.get("access_token")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id") or payload.get("sub")
            request._user = CustomUserModel.objects.get(id=user_id)

        except:
            request._user = AnonymousUser()

        response = self.get_response(request)

        return response

