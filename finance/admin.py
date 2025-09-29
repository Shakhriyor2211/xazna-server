from django.contrib import admin
from django.core.exceptions import PermissionDenied

from finance.models import BalanceModel, PlanModel, SubscriptionModel


class PlanAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = (
        "id",
        "title",
        "monthly_credit",
        "annual_credit",
        "monthly_price",
        "annual_price",
        "monthly_discount",
        "annual_discount",
        "rate",
        "rate_time",
        "user",
        "created_at"
    )
    ordering = ("-created_at",)

    def delete_model(self, request, obj):
        if obj.title == "Free" or obj.title == "Enterprise":
            raise PermissionDenied("The Free plan cannot be deleted.")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if queryset.filter(title="Free").exists():
            raise PermissionDenied("The Free plan cannot be deleted.")

        if queryset.filter(title="Enterprise").exists():
            raise PermissionDenied("The Free plan cannot be deleted.")

        super().delete_queryset(request, queryset)

    def get_exclude(self, request, obj=None):
        exclude_fields = super().get_exclude(request, obj)
        if obj and obj.title == "Free":
            items = ["description", "rate", "rate_time", "monthly_credit"]
            fields = [f.name for f in self.model._meta.concrete_fields]
            exclude_fields += tuple(f for f in fields if f not in items)

        if obj and obj.title == "Enterprise":
            items = ["description"]
            fields = [f.name for f in self.model._meta.concrete_fields]
            exclude_fields += tuple(f for f in fields if f not in items)

        return exclude_fields



    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cash",
        "subscription__expense",
        "subscription__credit",
        "subscription__title",
        "user",
        "created_at"
    )



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
        "rate_usage",
        "rate_reset",
        "start_date",
        "end_date"
    )
    ordering = ("-created_at",)

admin.site.register(BalanceModel, BalanceAdmin)
admin.site.register(PlanModel, PlanAdmin)
admin.site.register(SubscriptionModel, SubscriptionAdmin)
