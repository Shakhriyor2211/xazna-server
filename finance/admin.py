from django.contrib import admin

from finance.models import BalanceModel, SubscriptionModel


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



class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "credits",
        "cash",
        "user",
        "created_at"
    )

admin.site.register(BalanceModel, BalanceAdmin)
admin.site.register(SubscriptionModel, SubscriptionAdmin)
