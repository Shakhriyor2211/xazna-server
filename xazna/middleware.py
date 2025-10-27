from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import decode, InvalidTokenError, ExpiredSignatureError
from accounts.models import CustomUserModel
from xazna import settings



class ViewAuthMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        view_class = getattr(view_func, "view_class", None)
        auth_required = getattr(view_class, "auth_required", False) or getattr(view_func, "auth_required", False)

        if not auth_required:
            request._user = AnonymousUser()
            return None

        token = request.COOKIES.get('access_token')

        if not token:
            return JsonResponse({"message": "Authentication credentials were not provided.", "code": "auth_required"}, status=401)


        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True}
            )

            user_id = payload.get("user_id") or payload.get("sub")
            user = CustomUserModel.objects.get(id=user_id)

            if user.is_blocked:
                return JsonResponse({"message": "Account is blocked.", "code": "account_blocked"}, status=403)

            admin_required = getattr(view_class, "admin_required", False) or getattr(view_func, "admin_required", False)

            if admin_required and user.role != "admin" and  user.role != "superadmin":
                return JsonResponse({"message": "Admin privileges required.", "code": "privileges_required"}, status=403)

            request._user = user

        except ExpiredSignatureError:
            return JsonResponse({"message": "Token has expired.", "code": "expired_token"}, status=401)
        except InvalidTokenError:
            return JsonResponse({"message": "Invalid token.", "code": "invalid_token"}, status=400)
        except CustomUserModel.DoesNotExist:
            return JsonResponse({"message": "User not found.", "code": "not_found"}, status=404)






