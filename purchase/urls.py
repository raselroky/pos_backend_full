from django.urls import path,include
from .views import *
urlpatterns=[
    path('expense-create/', AdditionalExpenseListCreateAPIView.as_view(), name='additional-expense-create-api'),
    path('expense-list/', AdditionalExpenseListAPIView.as_view(), name='additional-expense-list-api'),
    path('expense-retrieve-update-destroy/<int:id>', AdditionalExpenseRetrieveUpdateDestroyListAPIView.as_view(), name='additional-expense-retrieve-update-destroy-api'),
    
    path('purchase-create/', PurchaseListCreateAPIView.as_view(), name='purchase-create-api'),
    path('purchase-list/', PurchaseListAPIView.as_view(), name='purchase-list-api'),
    path('purchase-retrieve-update-destroy/<int:id>', PurchaseRetrieveUpdateDestroyListAPIView.as_view(), name='purchase-retrieve-update-destroy-api'),
    path('purchase-retrieve/<int:id>', PurchaseRetrieveListAPIView.as_view(), name='purchase-retrieve-api'),

    path('purchase-history-create/', PurchaseHistoryListCreateAPIView.as_view(), name='purchase-history-create-api'),
    path('purchase-history-list/', PurchaseHistoryListAPIView.as_view(), name='purchase-history-list-api'),
    path('purchase-history-retrieve-update-destroy/<int:id>', PurchaseHistoryRetrieveUpdateDestroyListAPIView.as_view(), name='purchase-history-retrieve-update-destroy-api'),
    path('purchase-history-retrieve/<int:id>', PurchaseHistoryRetrieveListAPIView.as_view(), name='purchase-history-retrieve-api'),

    path('purchase-return-create/', PurchaseReturnListCreateAPIView.as_view(), name='purchase-return-create-api'),
    path('purchase-return-list/', PurchaseReturnListAPIView.as_view(), name='purchase-return-list-api'),
    path('purchase-return-retrieve-update-destroy/<int:id>', PurchaseReturnRetrieveUpdateDestroyListAPIView.as_view(), name='purchase-return-retrieve-update-destroy-api'),
    path('purchase-return-retrieve/<int:id>', PurchaseReturnRetrieveListAPIView.as_view(), name='purchase-return-retrieve-api'),

    path('purchase-return-history-create/', PurchaseReturnHistoryListCreateAPIView.as_view(), name='purchase-return-history-create-api'),
    path('purchase-return-history-list/', PurchaseReturnHistoryListAPIView.as_view(), name='purchase-return-history-list-api'),
    path('purchase-return-history-retrieve-update-destroy/<int:id>', PurchaseReturnHistoryRetrieveUpdateDestroyListAPIView.as_view(), name='purchase-return-history-retrieve-update-destroy-api'),
    path('purchase-return-history-retrieve/<int:id>', PurchaseReturnHistoryRetrieveListAPIView.as_view(), name='purchase-return-history-retrieve-api'),
    

]