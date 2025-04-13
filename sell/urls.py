from django.urls import path,include
from .views import *
urlpatterns=[
    path('sale-create/',SaleListCreateAPIView.as_view(), name='sale-create-api'),
    path('sale-list/', SaleListAPIView.as_view(), name='sale-list-api'),
    path('sale-retrieve-update-destroy/<int:id>',SaleRetrieveUpdateDestroyListAPIView.as_view(), name='sale-update-destroy-api'),
    path('sale-retrieve/<int:id>', SaleRetrieveAPIView.as_view(), name='sale-retrieve-api'),

    path('sale-return-create/',SaleReturnListCreateAPIView.as_view(), name='sale-return-create-api'),
    path('sale-return-list/', SaleReturnListAPIView.as_view(), name='sale-return-list-api'),
    path('sale-return-retrieve-update-destroy/<int:id>',SaleReturnRetrieveUpdateDestroyListAPIView.as_view(), name='sale-return-update-destroy-api'),
    path('sale-return-retrieve/<int:id>',SaleReturnRetrieveListAPIView.as_view(), name='sale-return-retrieve-api'),


    path('quotation-create/',QuotationListCreateAPIView.as_view(), name='quotation-create-api'),
    path('quotation-list/', QuotationListAPIView.as_view(), name='quotation-list-api'),
    path('quotation-retrieve-update-destroy/<int:id>',QuotationRetrieveUpdateDestroyListAPIView.as_view(), name='quotation-update-destroy-api'),
    path('quotation-retrieve/<int:id>', QuotationRetrieveAPIView.as_view(), name='quotation-retrieve-api'),
    
]