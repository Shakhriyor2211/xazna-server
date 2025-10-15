from rest_framework import serializers

from finance.models import BalanceModel, TransactionModel, ExpenseModel
from subscription.serializers import SubscriptionSerializer


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        exclude = ["user"]
        extra_kwargs = {
            "status": {"read_only": True},
        }


class BalanceManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceModel
        fields = ["chargeable"]


class BalanceSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = BalanceModel
        exclude = ["user"]


class ExpenseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseModel
        exclude = ["user"]