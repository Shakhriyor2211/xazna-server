from django.contrib import admin

from tts.models import TTSModel


class TTSAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'created_at'
    )

admin.site.register(TTSModel, TTSAdmin)