from django.contrib import admin
from finance.models import BalanceModel, TransactionModel, ExpenseModel

@admin.register(ExpenseModel)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "operation",
        "cash",
        "credit",
        "user",
        "created_at"
    )

@admin.register(TransactionModel)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "amount",
        "currency",
        "provider",
        "method",
        "status",
        "user",
        "created_at"
    )


@admin.register(BalanceModel)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cash",
        "subscription__credit_expense",
        "subscription__credit",
        "subscription__title",
        "user",
        "created_at"
    )



