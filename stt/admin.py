from django.contrib import admin
from stt.models import STTModel, STTModelModel



class STTAdmin(admin.ModelAdmin):
    list_display = ("text", "user", "created_at")


class STTModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "credit",
        "cash",
        "created_at",
    )


admin.site.register(STTModelModel, STTModelAdmin)
admin.site.register(STTModel, STTAdmin)
