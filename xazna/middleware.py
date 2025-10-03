import jwt
from inspect import iscoroutinefunction
from asgiref.sync import sync_to_async, markcoroutinefunction
from django.contrib.auth.models import AnonymousUser

from accounts.models import CustomUserModel
from xazna import settings


def _get_user_id(request):
    token = request.COOKIES.get("access_token")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    return payload.get("user_id") or payload.get("sub")



class CoreMiddleware:
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self._is_async = False

        if iscoroutinefunction(self.get_response):
            self._is_async = True
            markcoroutinefunction(self)

    def __call__(self, request):
        if self._is_async:
            return self._async_call(request)

        return self._sync_call(request)

    def _sync_call(self, request):
        try:
            user_id = self._get_user_id(request)
            request._user = CustomUserModel.objects.get(id=user_id)
        except:
            request._user = AnonymousUser()

        return self.get_response(request)

    async def _async_call(self, request):
        try:
            user_id = self._get_user_id(request)
            request._user = await sync_to_async(CustomUserModel.objects.get)(id=user_id)
        except:
            request._user = AnonymousUser()

        return await self.get_response(request)

    def _get_user_id(self, request):
        token = request.COOKIES.get("access_token")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("user_id") or payload.get("sub")

