from django.urls import path,include
from .views import *
urlpatterns=[
    path('product-create/', ProductListCreateAPIView.as_view(), name='product-create-api'),
    path('product-list/', ProductListAPIView.as_view(), name='product-list-api'),
    path('product-retrieve-update-destroy/<int:id>', ProductRetrieveUpdateDestroy.as_view(), name='product-retrieve-update-destroy-api'),
    path('product-retrieve/<int:id>', ProductRetrieve.as_view(), name='product-retrieve-api'),

    path('productvariant-create/', ProductVariantAttributeListCreateAPIView.as_view(), name='productvariant-create-api'),
    path('productvariant-list/', ProductVariantAttributeListAPIView.as_view(), name='productvariant-list-api'),
    path('productvariant-retrieve-update-destroy/<int:id>', ProductVariantAttributeRetrieveUpdateDestroy.as_view(), name='productvariant-retrieve-update-destroy-api'),
    path('productvariant-retrieve/<int:id>', ProductVariantAttributeRetrieve.as_view(), name='productvariant-retrieve-api'),


    path('export-product/', ProductExportExcelAPIView.as_view(), name='product-export-api'),


    path('productbarcode-create/', ProductBarcodeListCreateAPIView.as_view(), name='productbarcode-create-api'),
    path('productbarcode-list/', ProductBarcodeListAPIView.as_view(), name='productbarcode-list-api'),
    path('productbarcode-retrieve-update-destroy/<int:id>', ProductBarcodeRetrieveUpdateDestroy.as_view(), name='productbarcode-retrieve-update-destroy-api'),
    path('productbarcode-retrieve/<int:id>', ProductBarcodeRetrieveListAPIView.as_view(), name='productbarcode-retrieve-api'),

    
]