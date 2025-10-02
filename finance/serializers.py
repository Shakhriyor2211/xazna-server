from rest_framework import serializers

from finance.models import SubscriptionModel, BalanceModel, PlanModel


class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        exclude = ["user", "created_at", "updated_at"]

class SubscriptionWriteSerializer(serializers.Serializer):
    plan = serializers.CharField(max_length=50)
    period = serializers.CharField(max_length=50)


class SubscriptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]

class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]


class BalanceSerializer(serializers.ModelSerializer):
    subscription = SubscriptionReadSerializer(read_only=True)

    class Meta:
        model = BalanceModel
        exclude = ["user"]