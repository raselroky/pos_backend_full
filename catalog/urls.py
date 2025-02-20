from django.urls import path,include
from .views import ProductUnitListCreateAPIView,ProductUnitListAPIView,ProductUnitRetrieveUpdateDestroy,BrandListCreateAPIView,BrandListAPIView,BrandRetrieveUpdateDestroy,CategoryListCreateAPIView,CategoryListAPIView,CategoryRetrieveUpdateDestroy,SubCategoryListCreateAPIView,SubCategoryListAPIView,SubCategoryRetrieveUpdateDestroy,ColorVariationListCreateAPIView,ColorVariationListAPIView,ColorVariationRetrieveUpdateDestroy,AttributeVariationListCreateAPIView,AttributeVariationListAPIView,AttributeVariationRetrieveUpdateDestroy

urlpatterns=[
    path('productunit-create/', ProductUnitListCreateAPIView.as_view(), name='productunit-create-api'),
    path('productunit-list/', ProductUnitListAPIView.as_view(), name='productunit-list-api'),
    path('productunit-retrieve-update-destroy/<int:id>', ProductUnitRetrieveUpdateDestroy.as_view(), name='productunit-retrieve-update-destroy-api'),

    path('brand-create/', BrandListCreateAPIView.as_view(), name='brand-create-api'),
    path('brand-list/', BrandListAPIView.as_view(), name='brand-list-api'),
    path('brand-retrieve-update-destroy/<int:id>', BrandRetrieveUpdateDestroy.as_view(), name='brand-retrieve-update-destroy-api'),

    path('category-create/', CategoryListCreateAPIView.as_view(), name='category-create-api'),
    path('category-list/', CategoryListAPIView.as_view(), name='category-list-api'),
    path('category-retrieve-update-destroy/<int:id>', CategoryRetrieveUpdateDestroy.as_view(), name='category-retrieve-update-destroy-api'),

    path('subcategory-create/', SubCategoryListCreateAPIView.as_view(), name='subcategory-create-api'),
    path('subcategory-list/', SubCategoryListAPIView.as_view(), name='subcategory-list-api'),
    path('subcategory-retrieve-update-destroy/<int:id>', SubCategoryRetrieveUpdateDestroy.as_view(), name='subcategory-retrieve-update-destroy-api'),

    path('colorvariation-create/', ColorVariationListCreateAPIView.as_view(), name='colorvariation-create-api'),
    path('colorvariation-list/', ColorVariationListAPIView.as_view(), name='colorvariation-list-api'),
    path('colorvariation-retrieve-update-destroy/<int:id>', ColorVariationRetrieveUpdateDestroy.as_view(), name='colorvariation-retrieve-update-destroy-api'),

    path('attributevariation-create/', AttributeVariationListCreateAPIView.as_view(), name='attributevariation-create-api'),
    path('attributevariation-list/', AttributeVariationListAPIView.as_view(), name='attributevariation-list-api'),
    path('attributevariation-retrieve-update-destroy/<int:id>', AttributeVariationRetrieveUpdateDestroy.as_view(), name='attributevariation-retrieve-update-destroy-api'),
    

]