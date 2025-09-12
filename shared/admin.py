from django.contrib import admin
from shared.models import AudioModel


class AudioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'file',
        'created_at'
    )


admin.site.register(AudioModel, AudioAdmin)