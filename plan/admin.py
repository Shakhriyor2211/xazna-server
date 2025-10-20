from django.contrib import admin
from plan.models import PlanModel, PlanMonthlyModel, PlanAnnualModel, PlanSTTRateModel, PlanTTSRateModel, PlanChatRateModel, \
    PlanSTTCreditRateModel, PlanTTSCreditRateModel, PlanChatCreditRateModel, PlanChatSessionRateModel, PlanRateModel


@admin.register(PlanModel)
class PlanAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        "id",
        "title",
        "chat_session",
        "chat_context",
        "monthly__credit",
        "annual__credit",
        "user",
        "created_at"
    )


    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(PlanMonthlyModel)
class PlanMonthlyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "plan",
        "credit",
        "price",
        "discount"
    )

@admin.register(PlanAnnualModel)
class PlanAnnualAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "plan",
        "credit",
        "price",
        "discount"
    )


@admin.register(PlanRateModel)
class PlanRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "plan",
    )


@admin.register(PlanSTTRateModel)
class STTRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate",
    )


@admin.register(PlanTTSRateModel)
class TTSRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate",
    )

@admin.register(PlanChatRateModel)
class ChatRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate__plan",
    )

@admin.register(PlanSTTCreditRateModel)
class STTCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stt",
        "limit",
        "time",
    )


@admin.register(PlanTTSCreditRateModel)
class TTSCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tts",
        "limit",
        "time",
    )


@admin.register(PlanChatCreditRateModel)
class ChatCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "limit",
        "time",
    )


@admin.register(PlanChatSessionRateModel)
class ChatSessionRateModel(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "limit",
    )






