from django.contrib import admin
from subscription.models import SubscriptionModel


@admin.register(SubscriptionModel)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "expense",
        "credit",
        "status",
        "auto_renew",
        "user",
        "rate",
        "start_date",
        "end_date"
    )

