from django.urls import path,include
from .views import *
urlpatterns=[
    path('barcodesetting-create/',BarcodeSettingListCreateAPIView.as_view(), name='barcodesetting-create-api'),
    path('barcodesetting-list/', BarcodeSettingListAPIView.as_view(), name='barcodesetting-list-api'),
    path('barcodesetting-retrieve-update-destroy/<int:id>',BarcodeSettingRetrieveUpdateDestroyAPIView.as_view(), name='barcodesetting-update-destroy-api'),
    path('barcodesetting-retrieve/<int:id>', BarcodeSettingRetrieveListAPIView.as_view(), name='barcode-retrieve-api'),

    path('invoicesetting-create/',InvoiceSettingListCreateAPIView.as_view(), name='invoicesetting-create-api'),
    path('invoicesetting-list/', InvoiceSettingListAPIView.as_view(), name='invoicesetting-list-api'),
    path('invoicesetting-retrieve-update-destroy/<int:id>',InvoiceSettingRetrieveUpdateDestroyAPIView.as_view(), name='invoicesetting-update-destroy-api'),
    path('invoicesetting-retrieve/<int:id>', InvoiceSettingRetrieveListAPIView.as_view(), name='invoice-retrieve-api'),
    

    path('generalsetting-create/',GeneralSettingListCreateAPIView.as_view(), name='generalsetting-create-api'),
    path('generalsetting-list/', GeneralSettingListAPIView.as_view(), name='generalsetting-list-api'),
    path('generalsetting-retrieve-update-destroy/<int:id>',GeneralSettingRetrieveUpdateDestroyAPIView.as_view(), name='generalsetting-update-destroy-api'),


    path('send-email/',SendEmailAPIView.as_view(),name='send-email-from-admin-api'),
]