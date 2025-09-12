from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.exceptions import AuthException, PermissionException


class AuthPermission(IsAuthenticated):
    def has_permission(self, request, view):
        jwt_auth = JWTAuthentication()

        access_token = request.COOKIES.get('access_token')

        if not access_token:
            raise AuthException(message="Authentication credentials were not provided.", code="not_authenticated")

        try:
            validated_token = jwt_auth.get_validated_token(access_token)
            request.user = jwt_auth.get_user(validated_token)

        except:
            raise AuthException(message="Token is invalid or expired.", code="invalid_token")


        if request.user.is_blocked:
            raise PermissionException(message="Account is blocked.", code="user_blocked")

        return True



class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user is None:
            raise AuthException(message="Authentication credentials were not provided.", code="not_authenticated")

        if user.is_blocked:
            raise PermissionException(message="Account is blocked.", code="user_blocked")

        if user.role != 'superadmin' and user.role != 'admin':
            raise PermissionException

        return True


