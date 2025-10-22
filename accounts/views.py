import json
from datetime import timedelta
import requests
from celery.result import AsyncResult
from django.http import HttpResponseRedirect
from django.utils import timezone
from drf_yasg import openapi
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import CustomUserModel, SocialAccountModel, EmailConfirmOtpModel, PasswordResetTokenModel, PictureModel
from accounts.serializers import SignUpSerializer, UserSerializer, SignInSerializer, RefreshTokenSerializer, \
    VerifyTokenSerializer, ResendEmailCodeSerializer, VerifyEmailCodeSerializer, PasswordChangeSerializer, \
    ProfileChangeInfoSerializer, PictureSerializer
from drf_yasg.utils import swagger_auto_schema
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from accounts.tasks import send_email_confirmation, send_email_reset_password
from accounts.utils import generate_email_otp
from xazna import settings


class UserProfileView(APIView):
    auth_required = True

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersView(APIView):
    auth_required = True
    admin_required = True

    @swagger_auto_schema(operation_description="Users...")
    def get(self, request):
        users = CustomUserModel.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    auth_required = True
    admin_required = True

    @swagger_auto_schema(operation_description="User detail...")
    def get(self, request, user_id):
        user = get_object_or_404(CustomUserModel, id=user_id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    @swagger_auto_schema(operation_description="Sign up...", request_body=SignUpSerializer)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user_instance = serializer.save()

            if user_instance.is_active:
                refresh = RefreshToken.for_user(user_instance)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                user = UserSerializer(user_instance)

                response = Response(data=user.data, status=status.HTTP_200_OK)

                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    # httponly=True,
                    # secure=True,
                    samesite="Lax"
                )

                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    # httponly=True,
                    # secure=True,
                    samesite="Lax"
                )

                return response

            email_otp = EmailConfirmOtpModel.objects.create(user=user_instance)
            email_otp.code, email_otp.expires_at = generate_email_otp(email_otp.code)
            email_otp.remaining_resends -= 1
            email_otp.task_id = send_email_confirmation.delay(email_otp.id)
            email_otp.save()

            return Response(data={"otp_id": email_otp.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    @swagger_auto_schema(operation_description="Sign in...", request_body=SignInSerializer)
    def post(self, request):
        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid():
            user_instance = serializer.validated_data["user"]

            if not user_instance.is_active:
                email_otp = EmailConfirmOtpModel.objects.filter(user=user_instance).first()

                if email_otp is None :
                    email_otp = EmailConfirmOtpModel.objects.create(user=user_instance)
                    email_otp.code, email_otp.expires_at = generate_email_otp(email_otp.code)
                    email_otp.remaining_resends -= 1
                    email_otp.task_id = send_email_confirmation.delay(email_otp.id)
                    email_otp.save()

                    return Response(data={"otp_id": email_otp.id}, status=status.HTTP_200_OK)

                if email_otp.last_attempt + timedelta(minutes=settings.EMAIL_ATTEMPT_BLOCK_TIME) <= timezone.now():
                    email_otp.remaining_attempts = settings.EMAIL_MAX_ATTEMPTS
                elif email_otp.remaining_attempts == 0:
                    return Response(data={"message": "Your account temporarily blocked."},
                                    status=status.HTTP_403_FORBIDDEN)

                if email_otp.last_resend + timedelta(minutes=settings.EMAIL_RESEND_BLOCK_TIME) <= timezone.now():
                    email_otp.remaining_resends = settings.EMAIL_MAX_RESENDS

                if email_otp.remaining_resends > 0:
                    result = AsyncResult(email_otp.task_id)

                    if result.state in ["PENDING", "STARTED"]:
                        result.revoke(terminate=True, signal="SIGKILL")

                    email_otp.code, email_otp.expires_at = generate_email_otp(email_otp.code)
                    email_otp.status = "processing"
                    email_otp.remaining_resends -= 1
                    email_otp.remaining_attempts = settings.EMAIL_MAX_ATTEMPTS
                    email_otp.last_resend = timezone.now()
                    email_otp.save()
                    email_otp.task_id = send_email_confirmation.delay(email_otp.id)
                email_otp.save()

                return Response(data={"otp_id": email_otp.id}, status=status.HTTP_200_OK)

            refresh = RefreshToken.for_user(user_instance)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user = UserSerializer(user_instance)

            user_instance.last_login = timezone.now()
            user_instance.save()

            response = Response(data=user.data, status=status.HTTP_200_OK)

            response.set_cookie(
                key="access_token",
                value=access_token,
                # httponly=True,
                # secure=True,
                samesite="Lax"
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                # httponly=True,
                # secure=True,
                samesite="Lax"
            )

            return response

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendEmailCodeView(APIView):
    @swagger_auto_schema(operation_description="Send email confirmation...", request_body=ResendEmailCodeSerializer)
    def post(self, request):
        try:
            otp_id = request.data.get("otp_id")
            email_otp = EmailConfirmOtpModel.objects.get(id=otp_id)

            if email_otp.last_resend + timedelta(minutes=settings.EMAIL_RESEND_BLOCK_TIME) <= timezone.now():
                email_otp.remaining_resends = settings.EMAIL_MAX_RESENDS

            elif email_otp.remaining_resends == 0:
                return Response(data={"message": "Resend confirmation code limit exceeded."},
                                status=status.HTTP_403_FORBIDDEN)

            if email_otp.remaining_attempts == 0 and email_otp.last_attempt + timedelta(
                    minutes=settings.EMAIL_ATTEMPT_BLOCK_TIME) >= timezone.now():
                return Response(data={"message": "Your account temporarily blocked."},
                                status=status.HTTP_403_FORBIDDEN)

            result = AsyncResult(email_otp.task_id)

            if result.state in ["PENDING", "STARTED"]:
                result.revoke(terminate=True, signal="SIGKILL")

            email_otp.code, email_otp.expires_at = generate_email_otp(email_otp.code)
            email_otp.remaining_attempts = settings.EMAIL_MAX_ATTEMPTS
            email_otp.remaining_resends -= 1
            email_otp.last_resend = timezone.now()
            email_otp.status = "processing"
            email_otp.save()
            email_otp.task_id = send_email_confirmation.delay(email_otp.id)
            email_otp.save()

            return Response(data={"message": "Confirmation code was sent to your email address."},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response(data={"message": "Failed to send confirmation code."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailCodeView(APIView):
    @swagger_auto_schema(
        operation_description="Verify confirmation code...",
        request_body=VerifyEmailCodeSerializer
    )
    def post(self, request):
        code = request.data.get("code")
        otp_id = request.data.get("otp_id")

        email_otp = EmailConfirmOtpModel.objects.get(id=otp_id)

        if email_otp.last_attempt + timedelta(minutes=settings.EMAIL_ATTEMPT_BLOCK_TIME) <= timezone.now():
            email_otp.remaining_attempts = settings.EMAIL_MAX_ATTEMPTS

        if email_otp.remaining_attempts == 0:
            return Response(data={"message": "Your account temporarily blocked."},
                            status=status.HTTP_403_FORBIDDEN)

        email_otp.last_attempt = timezone.now()

        if code != email_otp.code:
            email_otp.remaining_attempts -= 1
            email_otp.save()
            return Response(data={"message": "Invalid confirmation code."},
                            status=status.HTTP_400_BAD_REQUEST)

        if email_otp.expires_at <= timezone.now():
            email_otp.save()
            return Response(data={"message": "Confirmation code is expired."},
                            status=status.HTTP_404_NOT_FOUND)

        user_instance = email_otp.user
        email_otp.delete()
        user_instance.is_active = True
        user_instance.save()

        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user = UserSerializer(user_instance)
        response = Response(data=user.data, status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token",
            value=access_token,
            # httponly=True,
            # secure=True,
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            # httponly=True,
            # secure=True,
            samesite="Lax"
        )

        return response


class RefreshTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Refresh token...",
        request_body=RefreshTokenSerializer
    )
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        refresh_token = request.COOKIES.get("refresh_token") or serializer.validated_data.get("refresh")

        if not refresh_token:
            return Response({"message": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            user_id = token.payload.get("user_id")

            if not user_id:
                raise ValueError("Invalid token payload")

            user = CustomUserModel.objects.get(id=user_id)

            new_access_token = str(token.access_token)
            new_refresh_token = str(RefreshToken.for_user(user))

            token.blacklist()

            response = Response({
                "access": new_access_token,
                "refresh": new_refresh_token,
            }, status=status.HTTP_200_OK)

            response.set_cookie("access_token", new_access_token, samesite="Lax")
            response.set_cookie("refresh_token", new_refresh_token, samesite="Lax")

            return response

        except Exception:
            response = Response({"message": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response


class VerifyTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Verify access token...",
        request_body=VerifyTokenSerializer
    )
    def post(self, request):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        token = serializer.validated_data.get("token") or request.COOKIES.get("access_token")

        if not token:
            return Response({"message": "Access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            AccessToken(token)
            return Response({"message": "Access token is valid."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"message": "Invalid token.", "code": "invalid_token"}, status=status.HTTP_401_UNAUTHORIZED)


class SignOutView(APIView):

    @swagger_auto_schema(operation_description="Sign out...", )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is not None:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(data={"message": "Logged out successfully."}, status=status.HTTP_200_OK)

            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response

        return Response(data={"message": "Token is not provided."}, status=status.HTTP_400_BAD_REQUEST)


class GoogleOAuthView(APIView):
    @swagger_auto_schema(operation_description="Google oauth...")
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code",
        }

        token_res = requests.post("https://oauth2.googleapis.com/token", data=data)

        if not token_res.ok:
            return Response({"error": "Failed to exchange code"}, status=status.HTTP_400_BAD_REQUEST)

        token_data = token_res.json()
        id_token_str = token_data.get("id_token")
        access_token_str = token_data.get("access_token")

        if not id_token_str:
            return Response({"error": "No id_token in response"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

            email = idinfo["email"]
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            user, _ = CustomUserModel.objects.get_or_create(email=email, defaults={"first_name": first_name,
                                                                              "last_name": last_name})

            _, social_account_created = SocialAccountModel.objects.get_or_create(provider_user_id=idinfo["sub"], defaults={
                "user": user,
                "provider": "google"})

            if social_account_created:
                user.is_active = True
                user.google_auth = True
                user.save()
            else:
                user.last_login = timezone.now()
                user.save()

            if not user.picture.portrait:
                picture = self._get_google_photo(access_token_str)

                if picture is not None:
                    user.picture.portrait_url(picture)

            if user.is_blocked:
                return Response(data={"message": "Account is blocked.", "code": "blocked_user"},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = UserSerializer(user)

            response = Response(data=serializer.data, status=status.HTTP_200_OK)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response.set_cookie(
                key="access_token",
                value=access_token,
                # httponly=True,
                # secure=True,
                samesite="Lax"
            )

            if refresh_token:
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    # httponly=True,
                    # secure=True,
                    samesite="Lax"
                )

            return response
        except ValueError:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        state_data = json.loads(state)
        next_url = state_data.get("next", "/")
        fallback_url = state_data.get("fallback", "/404")

        if not code:
            return HttpResponseRedirect(redirect_to=f"""{fallback_url}?error=Missing code.""")

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_res = requests.post(url="https://oauth2.googleapis.com/token", data=data)

        if not token_res.ok:
            return HttpResponseRedirect(redirect_to=f"""{fallback_url}?error=Failed to exchange code.""")

        token_data = token_res.json()

        id_token_str = token_data.get("id_token")
        access_token_str = token_data.get("access_token")

        if not id_token_str:
            return HttpResponseRedirect(redirect_to=f"""{fallback_url}?error=No id_token in response.""")

        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

            email = idinfo["email"]
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            user, _ = CustomUserModel.objects.get_or_create(email=email, defaults={"first_name": first_name,
                                                                              "last_name": last_name})

            _, social_account_created = SocialAccountModel.objects.get_or_create(provider_user_id=idinfo["sub"], defaults={
                "user": user,
                "provider": "google"})

            if social_account_created:
                user.is_active = True
                user.google_auth = True
                user.save()
            else:
                user.last_login = timezone.now()
                user.save()

            if not user.picture.portrait:
                picture = self._get_google_photo(access_token_str)

                if picture is not None:
                    user.picture.portrait_url(picture)

            if user.is_blocked:
                return HttpResponseRedirect(redirect_to=f"""{fallback_url}?error=Account is blocked.""")

            response = HttpResponseRedirect(redirect_to=next_url)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response.set_cookie(
                key="access_token",
                value=access_token,
                # httponly=True,
                # secure=True,
                samesite="Lax"
            )

            if refresh_token:
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    # httponly=True,
                    # secure=True,
                    samesite="Lax"
                )

            return response

        except ValueError:
            return HttpResponseRedirect(redirect_to=f"""{fallback_url}?error=Something went wrong.""")

    def _get_google_photo(self, access_token):
        res = requests.get("https://people.googleapis.com/v1/people/me?personFields=photos",
                           headers={"Authorization": f"Bearer {access_token}"})
        if not res.ok:
            return None

        data = res.json()
        photos = data.get("photos", [])
        is_default = photos[0].get("default", True)

        if is_default:
            return None

        return photos[0].get("url")


class PasswordResetView(APIView):

    @swagger_auto_schema(
        operation_description="Reset password...",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL,
                                        description="User email address"),
                "target": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL,
                                        description="Email confirmation target")
            }
        ))
    def post(self, request):
        try:
            email = request.data.get("email")
            target = request.data.get("target")

            if email is None:
                return Response(data={"message": "Email address is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUserModel.objects.filter(email=email).first()

            if user is None:
                return Response(data={"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active or user.is_blocked:
                return Response(data={"message": "User is inactive or blocked."}, status=status.HTTP_400_BAD_REQUEST)

            token_generator = PasswordResetTokenGenerator()

            t = PasswordResetTokenModel.objects.create(user=user, token=token_generator.make_token(user))
            t.task_id = send_email_reset_password.delay(t.id, target)

            return Response(data={"message": "Message sent successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    def get(self, request, slug):
        t = PasswordResetTokenModel.objects.filter(slug=slug).first()
        if t is None:
            return Response(data={"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        if t.slug is None or t.created_at + timedelta(minutes=settings.RESET_PASSWORD_EXPIRE_TIME) <= timezone.now():
            t.delete()
            return Response(data={"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(t.user)
        t.slug = None
        t.token = token
        t.save()

        return Response({"token": token}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Reset confirm password...",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["password"],
            properties={
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New password"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New password"
                ),
            },
        )
    )
    def post(self, request, slug):
        try:
            t = PasswordResetTokenModel.objects.filter(token=slug).first()

            if t is None:
                return Response(data={"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

            user = t.user
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            if not new_password:
                return Response(data={"new_password": "Password is required."},
                                status=status.HTTP_400_BAD_REQUEST)
            if not confirm_password:
                return Response(data={"confirm_password": "Confirm password is required."},
                                status=status.HTTP_400_BAD_REQUEST)

            elif new_password != confirm_password:
                return Response(data={"confirm_password": "Confirm password did not match."},
                                status=status.HTTP_400_BAD_REQUEST)

            elif user.check_password(new_password):
                return Response(data={"new_password": "New password cannot be the same as the old password"},
                                status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.last_password_update = timezone.now()
            user.save()

            t.delete()
            return Response(data={"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordChangeView(APIView):
    auth_required = True

    @swagger_auto_schema(
        operation_description="Password change..",
        request_body=PasswordChangeSerializer
    )
    def put(self, request):
        if not request.user.regular_auth:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user_instance = request.user
        user_instance.set_password(serializer.validated_data["new_password"])
        user_instance.last_password_update = timezone.now()
        user_instance.save()
        user = UserSerializer(user_instance)
        return Response(data=user.data, status=status.HTTP_200_OK)


class ProfileChangeInfoView(APIView):
    auth_required = True

    @swagger_auto_schema(
        operation_description="Profile info change..",
        request_body=ProfileChangeInfoSerializer
    )
    def patch(self, request):
        user_instance = request.user

        serializer = ProfileChangeInfoSerializer(
            instance=user_instance,
            data=request.data,
            context={"request": request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated_user = serializer.save()

        user_data = UserSerializer(updated_user).data

        response = Response(data=user_data, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(updated_user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response.set_cookie(
            key="access_token",
            value=access_token,
            # httponly=True,
            # secure=True,
            samesite="Lax"
        )

        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                # httponly=True,
                # secure=True,
                samesite="Lax"
            )

        return response


class ProfileChangeImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    auth_required = True

    @swagger_auto_schema(
        operation_description="Profile image change..",
        request_body=PictureSerializer
    )
    def post(self, request, *args, **kwargs):
        try:
            picture = PictureModel.objects.get(user=request.user)
            serializer = PictureSerializer(picture, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            picture_obj = request.user.picture
            picture_obj.portrait = None
            picture_obj.save()
            return Response(
                data={"message": "Profile picture removed."},
                status=status.HTTP_200_OK
            )
        except PictureModel.DoesNotExist:
            return Response(
                data={"error": "No picture found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
