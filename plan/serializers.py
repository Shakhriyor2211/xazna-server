from rest_framework import serializers
from plan.models import PlanModel



class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        exclude = ["user", "created_at", "updated_at"]

