from django.contrib import admin
from stt.models import STTModel, STTModelModel


@admin.register(STTModel)
class STTAdmin(admin.ModelAdmin):
    list_display = ("short_text", "user", "created_at")
    ordering = ("-created_at",)

    def short_text(self, obj):
        return (obj.text[:50] + "...") if obj.text and len(obj.text) > 50 else obj.text
    short_text.short_description = "Text"


@admin.register(STTModelModel)
class STTModelAdmin(admin.ModelAdmin):
    exclude = ("user",)

    list_display = (
        "title",
        "user",
        "credit",
        "cash",
        "created_at",
    )
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


