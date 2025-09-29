from django.urls import path

from finance.views import SubscriptionAPIView, SubscriptionListAPIView, SubscriptionCheckAPIView

urlpatterns = [
    path("subscription/", SubscriptionAPIView.as_view(), name="subscription"),
    path("subscription/list", SubscriptionListAPIView.as_view(), name="subscription_list"),
    path("subscription/check", SubscriptionCheckAPIView.as_view(), name="subscription_check"),

]