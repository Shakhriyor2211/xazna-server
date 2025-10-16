from django.contrib import admin
from django.core.exceptions import PermissionDenied
from plan.models import PlanModel, PlanMonthlyModel, PlanAnnualModel, STTRateModel, TTSRateModel, ChatRateModel, \
    STTCreditRateModel, TTSCreditRateModel, ChatCreditRateModel, ChatSessionRateModel, PlanRateModel


@admin.register(PlanModel)
class PlanAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        "id",
        "title",
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


@admin.register(STTRateModel)
class STTRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate",
    )


@admin.register(TTSRateModel)
class TTSRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate",
    )

@admin.register(ChatRateModel)
class ChatRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rate__plan",
        "max_sessions"
    )

@admin.register(STTCreditRateModel)
class STTCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stt"
    )


@admin.register(TTSCreditRateModel)
class TTSCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tts"
    )


@admin.register(ChatCreditRateModel)
class ChatCreditRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat"
    )


@admin.register(ChatSessionRateModel)
class ChatSessionRateModel(admin.ModelAdmin):
    list_display = (
        "id",
        "chat",
        "limit",
    )






