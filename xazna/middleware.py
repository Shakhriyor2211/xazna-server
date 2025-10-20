from fnmatch import fnmatch

import jwt
from inspect import iscoroutinefunction
from asgiref.sync import markcoroutinefunction
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.models import CustomUserModel
from xazna import settings



class HTTPAuthMiddleware:
    async_capable = True
    sync_capable = False
    PUBLIC_PATHS = [
        "/swagger/",
        "/api/auth/*",
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        print(self._is_public_path(request.path), request.path)
        if self._is_public_path(request.path):
            request._user = AnonymousUser()
            return await self.get_response(request)

        jwt_auth = JWTAuthentication()
        token = request.COOKIES.get('access_token')

        if not token:
            return JsonResponse({"message": "Authentication credentials were not provided."}, status=401)

        try:
            validated_token = jwt_auth.get_validated_token(token)
            request.user = jwt_auth.get_user(validated_token)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id") or payload.get("sub")
            user = CustomUserModel.objects.filter(id=user_id).first()

            if user.is_blocked:
                return JsonResponse({"message": "Account is blocked."}, status=403)

            request._user = AnonymousUser() if user is None else user

        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=401)
        except CustomUserModel.DoesNotExist:
            raise PermissionDenied("User not found")

        return await self.get_response(request)

    def _is_public_path(self, path: str) -> bool:
        for pattern in self.PUBLIC_PATHS:
            if fnmatch(path, pattern):
                return True
        return False

