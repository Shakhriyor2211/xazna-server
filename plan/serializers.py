from rest_framework import serializers
from plan.models import (
    PlanRateModel, PlanModel, PlanMonthlyModel, PlanAnnualModel,
    PlanSTTRateModel, PlanTTSRateModel, PlanChatRateModel,
    PlanSTTCreditRateModel, PlanTTSCreditRateModel, PlanChatCreditRateModel,
    PlanChatSessionRateModel,
)

class PlanSTTCreditRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanSTTCreditRateModel
        fields = ["limit", "time"]


class PlanTTSCreditRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanTTSCreditRateModel
        fields = ["limit", "time"]


class PlanChatCreditRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanChatCreditRateModel
        fields = ["limit", "time"]


class PlanChatSessionRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanChatSessionRateModel
        fields = ["limit"]


class PlanSTTRateSerializer(serializers.ModelSerializer):
    credit = PlanSTTCreditRateSerializer()

    class Meta:
        model = PlanSTTRateModel
        fields = ["credit"]


class PlanTTSRateSerializer(serializers.ModelSerializer):
    credit = PlanTTSCreditRateSerializer()

    class Meta:
        model = PlanTTSRateModel
        fields = ["credit"]


class PlanChatRateSerializer(serializers.ModelSerializer):
    credit = PlanChatCreditRateSerializer()
    session = PlanChatSessionRateSerializer()

    class Meta:
        model = PlanChatRateModel
        fields = ["max_sessions", "credit", "session"]


class PlanRateSerializer(serializers.ModelSerializer):
    stt = PlanSTTRateSerializer()
    tts = PlanTTSRateSerializer()
    chat = PlanChatRateSerializer()

    class Meta:
        model = PlanRateModel
        fields = ["stt", "tts", "chat"]


class PlanMonthlySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanMonthlyModel
        fields = ["credit", "price", "discount"]


class PlanAnnualSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanAnnualModel
        fields = ["credit", "price", "discount"]


class PlanSerializer(serializers.ModelSerializer):
    rate = PlanRateSerializer()
    monthly = PlanMonthlySerializer()
    annual = PlanAnnualSerializer()

    class Meta:
        model = PlanModel
        fields = ["id", "title", "description", "rate", "monthly", "annual"]
