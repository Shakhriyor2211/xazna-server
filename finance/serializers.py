from rest_framework import serializers

from finance.models import SubscriptionModel


class SubscriptionSerializer(serializers.Serializer):
    plan = serializers.CharField(max_length=50)
    period = serializers.CharField(max_length=50)


class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]

