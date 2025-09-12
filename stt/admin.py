from django.contrib import admin

from stt.models import STTModel


class STTAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'created_at'
    )

admin.site.register(STTModel, STTAdmin)