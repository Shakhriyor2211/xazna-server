from django.contrib import admin
from tts.models import TTSModel, TTSEmotionModel, TTSAudioFormatModel, TTSModelModel


@admin.register(TTSModel)
class TTSAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'created_at'
    )
    ordering = ("-created_at",)

    def short_text(self, obj):
        return (obj.text[:50] + "...") if obj.text and len(obj.text) > 50 else obj.text
    short_text.short_description = "Text"

@admin.register(TTSModelModel)
class TTSModelAdmin(admin.ModelAdmin):
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


@admin.register(TTSEmotionModel)
class TTSEmotionAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        'title',
        'user',
        'created_at'
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(TTSAudioFormatModel)
class TTSAudioFormatAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        'title',
        'user',
        'created_at'
    )
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

