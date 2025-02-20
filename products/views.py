from django.shortcuts import render

from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, ListAPIView,
    RetrieveDestroyAPIView,RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ProductSerializer,ProductVariantAttributeSerializer,ProductDetailsSerializer,ProductVariantAttributeDetailsSerializer,ProductDetailsSerializer2,ProductBarcodesSerializer,ProductBarcodesDetailsSerializer
from .models import Product,ProductVariantAttribute,ProductBarcodes
from rest_framework.filters import SearchFilter, OrderingFilter
from helper import MainPagination
from helpers.identifier_builders import identifier_builder
from helpers.barcode import generate_barcode_image
import pandas as pd
from rest_framework.viewsets import ModelViewSet
from django.db import transaction


class ProductListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = MainPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        sku = request.data.get('sku', identifier_builder(table_name='products'))
        data['sku'] = sku

        color_id = data.get('color_attribute')
        size_id = data.get('variation_attribute')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            product = serializer.save(created_by=request.user)

            ProductVariantAttribute.objects.create(
                product=product,
                color_attribute_id=color_id,
                variation_attribute_id=size_id,
                created_by=request.user
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProductListAPIView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Product.objects.all()
    serializer_class=ProductDetailsSerializer
    pagination_class=MainPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','product_name','sku','category__category_name','sub_category__subcategory_name','brand__brand_name','weight','product_type','country']

    def get_queryset(self):
        return Product.objects.all()
    
class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return Product.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProductRetrieve(RetrieveAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Product.objects.all()
    serializer_class=ProductDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return Product.objects.all()


#################


class ProductVariantAttributeListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductVariantAttribute.objects.all()
    serializer_class=ProductVariantAttributeSerializer
    pagination_class=MainPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['created_by'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return ProductVariantAttribute.objects.all()


class ProductVariantAttributeListAPIView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductVariantAttribute.objects.all()
    serializer_class=ProductVariantAttributeDetailsSerializer
    pagination_class=MainPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','product_name','sku','category__category_name','sub_category__subcategory_name','brand__brand_name','product_type','country']
    
    def get_queryset(self):
        return ProductVariantAttribute.objects.all()
    
class ProductVariantAttributeRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductVariantAttribute.objects.all()
    serializer_class=ProductVariantAttributeSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return ProductVariantAttribute.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProductVariantAttributeRetrieve(RetrieveAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductVariantAttribute.objects.all()
    serializer_class=ProductVariantAttributeDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return ProductVariantAttribute.objects.all()




####### Excel Export


class ProductExportExcelAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
      
        
        data = Product.objects.all()
      
        serializer = ProductDetailsSerializer2(data, many=True)
        df = pd.DataFrame(serializer.data)

        df = df.drop(columns=["created_by", "updated_by","created_at","updated_by","description"], errors="ignore")
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Product_data.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)

        return response



class ProductBarcodeListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductBarcodes.objects.all()
    serializer_class=ProductBarcodesSerializer
    pagination_class=MainPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['created_by'] = request.user.id
        product_id = request.data.get('product_variant')
        try:
            product_variant = ProductVariantAttribute.objects.get(id=product_id)
        except ProductVariantAttribute.DoesNotExist:
            return Response({"error": "Invalid product variant ID"}, status=status.HTTP_400_BAD_REQUEST)
        sku = product_variant.product.sku
        data['barcode'] = sku
        barcode_image = generate_barcode_image(sku)
        data['barcode_image'] = barcode_image

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return ProductBarcodes.objects.all()


class ProductBarcodeListAPIView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductBarcodes.objects.all()
    serializer_class=ProductBarcodesDetailsSerializer
    pagination_class=MainPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','product__product_name','product__brand__brand_name','product__country','barcode']

    def get_queryset(self):
        return ProductBarcodes.objects.all()
    
class ProductBarcodeRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductBarcodes.objects.all()
    serializer_class=ProductBarcodesSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return ProductBarcodes.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




class ProductBarcodeRetrieveListAPIView(RetrieveAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductBarcodes.objects.all()
    serializer_class=ProductBarcodesDetailsSerializer
    lookup_field='id'
    #pagination_class=MainPagination
    #filter_backends = [SearchFilter, OrderingFilter]
    #search_fields = ['id','product_name','sku','category__category_name','sub_category__subcategory_name','brand__brand_name','weight','product_type','country']

    def get_queryset(self):
        return ProductBarcodes.objects.all()