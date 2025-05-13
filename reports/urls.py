from django.urls import path,include
from .views import *
urlpatterns=[
    path('purchase-reports/', PurchaseReportsListViews.as_view(), name='purchase-reports-api'),
    path('purchase-return-reports/', PurchaseReturnReportsListViews.as_view(), name='purchase-return-reports-api'),
    path('sell-reports/', SaleReportsListViews.as_view(), name='sell-reports-api'),
    path('sell-return-reports/', SaleReturnReportsListViews.as_view(), name='sell-return-reports-api'),
    path('stocks-reports/', StockReportsListViews.as_view(), name='stock-reports-api'),
    path('stocks-transfer-reports/', StockTransferReportsListViews.as_view(), name='stock-transfer-reports-api'),
    path('stocks-adjustment-reports/', StockAdjustmentReportsListViews.as_view(), name='stock-adjustment-reports-api'),
    path('customer-reports/', CustomerReportsListViews.as_view(), name='contact-reports-api'),
    path('supplier-reports/', SupplierReportsListViews.as_view(), name='supplier-reports-api'),

]