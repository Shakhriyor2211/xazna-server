from rest_framework import serializers
from subscription.models import SubscriptionModel


class SubscriptionChangeSerializer(serializers.Serializer):
    plan = serializers.CharField(max_length=50)
    period = serializers.CharField(max_length=50)

class SubscriptionManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ["auto_renew"]

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]

class SubscriptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        exclude = ["user"]

