from django.contrib import admin
from stt.models import STTModel, STTModelModel



class STTAdmin(admin.ModelAdmin):
    list_display = ("text", "user", "credit", "cash", "created_at")
    ordering = ("-created_at",)


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


admin.site.register(STTModelModel, STTModelAdmin)
admin.site.register(STTModel, STTAdmin)
