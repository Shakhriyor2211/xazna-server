from django.contrib import admin
from shared.models import AudioModel


@admin.register(AudioModel)
class AudioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "file",
        "created_at"
    )

