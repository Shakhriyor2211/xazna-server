from django.urls import path
from subscription.views import SubscriptionChangeAPIView, SubscriptionListAPIView, SubscriptionCheckAPIView, \
    SubscriptionRestartAPIView, SubscriptionManageAPIView

urlpatterns = [
    path("manage/", SubscriptionManageAPIView.as_view(), name="subscription_manage"),
    path("change/", SubscriptionChangeAPIView.as_view(), name="subscription_change"),
    path("restart/", SubscriptionRestartAPIView.as_view(), name="subscription_restart"),
    path("list/", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path("check/", SubscriptionCheckAPIView.as_view(), name="subscription_check"),
]
