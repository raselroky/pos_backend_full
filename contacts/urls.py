from django.urls import path,include
from .views import ContactListCreateAPIView,ContactListAPIView,ContactRetrieveUpdateDestroyListAPIView,ContactSupplierListAPIView,ContactCusotmerListAPIView,ContactBothListAPIView

urlpatterns=[
    path('contact-create/', ContactListCreateAPIView.as_view(), name='contact-create-api'),
    path('contact-list/', ContactListAPIView.as_view(), name='contact-list-api'),
    path('contact-supplier-list/', ContactSupplierListAPIView.as_view(), name='contact-supplier-list-api'),
    path('contact-customer-list/', ContactCusotmerListAPIView.as_view(), name='contact-customer-list-api'),
    path('contact-both-list/', ContactBothListAPIView.as_view(), name='contact-both-list-api'),
    path('contact-retrieve-update-destroy/<int:id>', ContactRetrieveUpdateDestroyListAPIView.as_view(), name='contact-retrieve-update-destroy-api'),
    

]