from django.contrib import admin
from shared.models import AudioModel, SubscriptionModel


class AudioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "file",
        "created_at"
    )

class SubscriptionAdmin(admin.ModelAdmin):
    exclude = ("user",)

    list_display = (
        "id",
        "title",
        "credits",
        "monthly_cost",
        "annual_cost",
        "discount",
        "user",
        "created_at"
    )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(SubscriptionModel, SubscriptionAdmin)
admin.site.register(AudioModel, AudioAdmin)