from django.urls import path
from finance.views import BalanceManageAPIView, BalanceTopUpAPIView, TransactionListAPIView, ExpenseListAPIView

urlpatterns = [
    path("balance/manage/", BalanceManageAPIView.as_view(), name="balance_manage"),
    path("balance/top-up/", BalanceTopUpAPIView.as_view(), name="balance_top_up"),
    path("transaction/list/", TransactionListAPIView.as_view(), name="transaction_list"),
    path("expense/list/", ExpenseListAPIView.as_view(), name="expense_list"),

]
