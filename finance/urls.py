from django.urls import path

from finance.views import SubscriptionAPIView, SubscriptionListAPIView, SubscriptionCheckAPIView, PlansAPIView

urlpatterns = [
    path("plans/", PlansAPIView.as_view(), name="plans"),
    path("subscription/", SubscriptionAPIView.as_view(), name="subscription"),
    path("subscription/list", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path("subscription/check", SubscriptionCheckAPIView.as_view(), name="subscription_check"),

]