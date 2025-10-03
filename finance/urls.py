from django.urls import path

from finance.views import SubscriptionChangeAPIView, SubscriptionListAPIView, SubscriptionCheckAPIView, PlansAPIView, \
    SubscriptionRestartAPIView, SubscriptionManageAPIView, BalanceManageAPIView

urlpatterns = [
    path("plans/", PlansAPIView.as_view(), name="plans"),
    path("balance/manage/", BalanceManageAPIView.as_view(), name="balance_manage"),
    path("subscription/manage/", SubscriptionManageAPIView.as_view(), name="subscription_manage"),
    path("subscription/change/", SubscriptionChangeAPIView.as_view(), name="subscription_change"),
    path("subscription/restart/", SubscriptionRestartAPIView.as_view(), name="subscription_restart"),
    path("subscription/list/", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path("subscription/check/", SubscriptionCheckAPIView.as_view(), name="subscription_check"),

]