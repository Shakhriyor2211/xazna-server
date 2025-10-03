from rest_framework import serializers

from finance.models import SubscriptionModel, BalanceModel, PlanModel


class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        exclude = ["user", "created_at", "updated_at"]

class SubscriptionChangeSerializer(serializers.Serializer):
    plan = serializers.CharField(max_length=50)
    period = serializers.CharField(max_length=50)


class SubscriptionManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ["auto_renew"]

class BalanceManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceModel
        fields = ["chargeable"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]

class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]


class BalanceSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = BalanceModel
        exclude = ["user"]