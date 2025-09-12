from django.urls import path
from accounts.views import SignOutView, SignUpView, GoogleOAuthView, UsersView, UserDetailView, \
    SignInView, UserProfileView, RefreshTokenView, VerifyTokenView, ResendEmailCodeView, \
    VerifyEmailCodeView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView, \
    ProfileChangeInfoView, ProfileChangeImageView

auth_urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("sign-in/", SignInView.as_view(), name="sign_in"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("resend/email/code/", ResendEmailCodeView.as_view(), name="resen_email_code"),
    path("verify/email/code/", VerifyEmailCodeView.as_view(), name="verify_email_code"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset_code"),
    path("password/reset/confirm/<str:slug>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("token/verify/", VerifyTokenView.as_view(), name="token_verify"),
    path("sign-out/", SignOutView.as_view(), name="token_blacklist"),
    path("google/oauth/", GoogleOAuthView.as_view(), name="google_oauth")
]

user_urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("list/", UsersView.as_view(), name="users"),
    path("detail/<int:user_id>/", UserDetailView.as_view(), name="detail"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/info/", ProfileChangeInfoView.as_view(), name="profile_change_info"),
    path("profile/image/", ProfileChangeImageView.as_view(), name="profile_change_image"),
    path("detail/<int:user_id>/", UserDetailView.as_view(), name="detail"),
]
