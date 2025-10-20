from django.contrib import admin
from subscription.models import SubscriptionModel, SubRateModel, SubSTTRateModel, SubTTSRateModel, SubChatRateModel, \
    SubSTTCreditRateModel, SubTTSCreditRateModel, SubChatCreditRateModel, SubChatSessionRateModel


@admin.register(SubscriptionModel)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "credit",
        "credit_expense",
        "chat_session",
        "chat_session_expense",
        "chat_context",
        "chat_context_expense",
        "status",
        "auto_renew",
        "user",
        "rate__tts__credit__limit",
        "rate__tts__credit__usage",
        "rate__stt__credit__limit",
        "rate__stt__credit__usage",
        "rate__chat__credit__limit",
        "rate__chat__credit__usage",
        "rate__chat__session__limit",
        "rate__chat__session__usage",
        "start_date",
        "end_date"
    )



    @admin.register(SubRateModel)
    class SubRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "subscription",
        )

    @admin.register(SubSTTRateModel)
    class STTRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "rate",
        )

    @admin.register(SubTTSRateModel)
    class TTSRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "rate",
        )

    @admin.register(SubChatRateModel)
    class ChatRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "rate__subscription"
        )

    @admin.register(SubSTTCreditRateModel)
    class STTCreditRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "stt",
            "limit",
            "time",
        )

    @admin.register(SubTTSCreditRateModel)
    class TTSCreditRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "tts",
            "limit",
            "time",
        )

    @admin.register(SubChatCreditRateModel)
    class ChatCreditRateAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "chat",
            "limit",
            "time",
        )

    @admin.register(SubChatSessionRateModel)
    class ChatSessionRateModel(admin.ModelAdmin):
        list_display = (
            "id",
            "chat",
            "limit",
        )


