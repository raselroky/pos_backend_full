from django.urls import path,include
from .views import CountryListCreateAPIView,CountryListAPIView,CountryRetrieveUpdateDestroyListAPIView,BranchListCreateAPIView,BranchListAPIView,BranchRetrieveUpdateDestroyListAPIView,BranchRetrieveListAPIView

urlpatterns=[
    path('country-create/', CountryListCreateAPIView.as_view(), name='country-create-api'),
    path('country-list/', CountryListAPIView.as_view(), name='country-list-api'),
    path('country-retrieve-update-destroy/<int:id>', CountryRetrieveUpdateDestroyListAPIView.as_view(), name='country-retrieve-update-destroy-api'),
    path('branch-create/', BranchListCreateAPIView.as_view(), name='branch-create-api'),
    path('branch-list/', BranchListAPIView.as_view(), name='branch-list-api'),
    path('branch-retrieve-update-destroy/<int:id>', BranchRetrieveUpdateDestroyListAPIView.as_view(), name='branch-retrieve-update-destroy-api'),
    path('branch-retrieve/<int:id>', BranchRetrieveListAPIView.as_view(), name='branch-retrieve-api'),

]