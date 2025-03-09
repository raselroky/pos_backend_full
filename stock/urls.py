from django.urls import path,include
from .views import *
urlpatterns=[
    path('stock-create/',StockListCreateAPIView.as_view(), name='stock-create-api'),
    path('stock-list/', StockListAPIView.as_view(), name='stock-list-api'),
    path('stock-retrieve-update-destroy/<int:id>',StockRetrieveUpdateDestroyListAPIView.as_view(), name='stock-update-destroy-api'),
    path('stock-retrieve/<int:id>',StockRetrieveListAPIView.as_view(), name='stock-retrieve-api'),

    path('stock-adjustment-create/',StockAdjustmentListCreateAPIView.as_view(), name='stock-adjustment-create-api'),
    path('stock-adjustment-list/',StockAdjustmentListAPIView.as_view(), name='stock-adjustment-list-api'),
    path('stock-adjustment-retrieve-update-destroy/<int:id>',StockAdjustmentRetrieveUpdateDestroyListAPIView.as_view(), name='stock-adjustment-retrieve-update-destroy-api'),

    path('stock-transfer-create/',StockTransferListCreateAPIView.as_view(), name='stock-transfer-create-api'),
    path('stock-transfer-list/',StockTransfertListAPIView.as_view(), name='stock-transfer-list-api'),
    path('stock-transfer-retrieve-update-destroy/<int:id>',StockTransferRetrieveUpdateDestroyListAPIView.as_view(), name='stock-transfer-retrieve-update-destroy-api'),


]
