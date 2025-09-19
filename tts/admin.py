from django.contrib import admin

from tts.models import TTSModel, TTSModelModel, TTSEmotionModel, TTSAudioFormatModel


class TTSAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'created_at'
    )
class TTSModelAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        "title",
        "user",
        "credit",
        "cash",
        "created_at",
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

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

class TTSAudioFormatAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        'title',
        'user',
        'created_at'
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(TTSModelModel, TTSModelAdmin)
admin.site.register(TTSEmotionModel, TTSEmotionAdmin)
admin.site.register(TTSAudioFormatModel, TTSAudioFormatAdmin)
admin.site.register(TTSModel, TTSAdmin)