from django.urls import path
from plan.views import PlanListAPIView

urlpatterns = [
    path("list/", PlanListAPIView.as_view(), name="plan_list")
]