from django.contrib import admin
from .models import ChatSessionModel, ChatMessageModel, ChatModelModel


@admin.register(ChatModelModel)
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


@admin.register(ChatMessageModel)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "status", "short_content", "created_at")
    list_filter = ("role", "status", "created_at")
    search_fields = ("content", "session__title", "session__user__email")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if obj.content and len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"



@admin.register(ChatSessionModel)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "user__email", "user__username")


