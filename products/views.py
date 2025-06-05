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
from catalog.models import ColorVariation,AttributeVariation,Category,SubCategory,Brand,ProductUnit
import uuid
from rest_framework.exceptions import ValidationError


class ProductListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = MainPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        sku = request.data.get('sku', identifier_builder(table_name='products'))
        data['sku'] = sku

        color_id = data.get('color_attribute')
        size_id = data.get('variation_attribute')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            product = serializer.save(created_by=request.user)
            branch_id = product.branch.id if product.branch else None

            ProductVariantAttribute.objects.create(
                product=product,
                color_attribute_id=color_id,
                variation_attribute_id=size_id,
                created_by=request.user,
                branch_id=branch_id
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if 'images' in request.FILES:
            data['images'] = request.FILES['images']
        elif 'images' in data and data['images'] in ["null", "", None]:  
            instance.images.delete(save=False)  
            data.pop('images')

        color_id = data.get("color_attribute")
        size_id = data.get("variation_attribute")

        try:
            color_id = int(color_id) if color_id else None
        except (ValueError, TypeError):
            return Response({"error": "Invalid color_attribute ID!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            size_id = int(size_id) if size_id else None
        except (ValueError, TypeError):
            return Response({"error": "Invalid variation_attribute ID!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=data,partial=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_update(serializer)

            if color_id or size_id:
                variant, created = ProductVariantAttribute.objects.get_or_create(product=instance)

                if color_id:
                    try:
                        variant.color_attribute = ColorVariation.objects.get(id=color_id)
                    except ColorVariation.DoesNotExist:
                        return Response({"error": "Invalid color_attribute ID!"}, status=status.HTTP_400_BAD_REQUEST)

                if size_id:
                    try:
                        variant.variation_attribute = AttributeVariation.objects.get(id=size_id)
                    except AttributeVariation.DoesNotExist:
                        return Response({"error": "Invalid variation_attribute ID!"}, status=status.HTTP_400_BAD_REQUEST)

                variant.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def get_queryset(self):
        user=self.request.user
        return Product.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


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
        data['branch'] = request.user.branch.id if request.user.branch else None
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
    search_fields = ['id','product__product_name','product__sku','product__country','product__brand__brand_name','product__category__category_name']
    
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
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class ProductVariantAttributeRetrieve(RetrieveAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductVariantAttribute.objects.all()
    serializer_class=ProductVariantAttributeDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        user=self.request.user
        return ProductVariantAttribute.objects.all()




class ProductBarcodeListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=ProductBarcodes.objects.all()
    serializer_class=ProductBarcodesSerializer
    pagination_class=MainPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        product_id = request.data.get('product_variant')
        try:
            product_variant = ProductVariantAttribute.objects.get(id=product_id)
        except ProductVariantAttribute.DoesNotExist:
            raise ValidationError({"error": "Invalid product variant ID"})
        
        input_barcode = data.get('barcode')
        if not input_barcode:
            generated_code = f"A-{uuid.uuid4().hex[:6].upper()}"
            if not ProductBarcodes.objects.filter(barcode=generated_code).exists():
                input_barcode=generated_code
                
        data['barcode'] = input_barcode
        data['barcode_image'] = generate_barcode_image(input_barcode)

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
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)




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




####### ExportExcel Product


class ProductExportExcelAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
      
        
        data = Product.objects.all()
      
        serializer = ProductDetailsSerializer2(data, many=True)
        df = pd.DataFrame(serializer.data)

        df = df.drop(columns=["created_by", "updated_by","created_at","updated_at","description"], errors="ignore")
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Product_data.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)

        return response



#######  ImportExcel product
def clean_value(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return str(value).strip()


class ProductImportExcelAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine="openpyxl")
            df = df.where(pd.notnull(df), None)

            with transaction.atomic():
                for _, row in df.iterrows():
                    unit_name = row.get("unit_name")
                    unit_short_name = row.get("unit_short_name")
                    unit = None
                    if unit_name:
                        unit, _ = ProductUnit.objects.update_or_create(
                            unit_name=unit_name,
                            defaults={"unit_short_name": unit_short_name, "created_by": request.user}
                        )

                    brand_name =row.get("brand_name")
                    brand_description = row.get("brand_description")
                    brand = None
                    if brand_name:
                        brand, _ = Brand.objects.update_or_create(
                            brand_name=brand_name,
                            defaults={"description": brand_description, "created_by": request.user}
                        )

                    category_name = row.get("category_name")
                    category = None
                    if category_name:
                        category, _ = Category.objects.update_or_create(
                            category_name=category_name,
                            defaults={"created_by": request.user}
                        )

                    subcategory_name = row.get("subcategory_name")
                    sub_category = None
                    if subcategory_name:
                        sub_category, _ = SubCategory.objects.update_or_create(
                            subcategory_name=subcategory_name,
                            defaults={"category": category, "created_by": request.user}
                        )
                    
                    # product_data = {
                    #     "product_name": row.get("product_name"),
                    #     "sku": row.get("sku", identifier_builder("products")),
                    #     "unit": unit,
                    #     "category": category,
                    #     "sub_category": sub_category,
                    #     "brand": brand,
                    #     "weight": row.get("weight", 0),
                    #     "product_type": row.get("product_type", "Single"),
                    #     "country": row.get("country"),
                    #     "vat_percentage": row.get("vat_percentage", 0.0),
                    #     "description": row.get("description"),
                    # }

                    # serializer = ProductSerializer(data=product_data)
                    # if serializer.is_valid():
                    #     product = serializer.save(created_by=request.user)
                    # else:
                    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    sku_raw = row.get("sku")

                    if sku_raw is None:
                        sku = identifier_builder(table_name='products')

                    if isinstance(sku_raw, (int, float)):
                        sku = str(int(sku_raw)).zfill(10)
                    else:
                        sku = str(sku_raw).strip()
                    product, created = Product.objects.update_or_create(
                        sku=sku,
                        defaults={
                            "product_name": row.get("product_name"),
                            "unit": unit,
                            "category": category,
                            "sub_category": sub_category,
                            "brand": brand,
                            "weight": row.get("weight", 0),
                            "product_type": row.get("product_type", "None"),
                            "country": row.get("country"),
                            "vat_percentage": row.get("vat_percentage", 0.0),
                            "description": row.get("description"),
                            "created_by": request.user
                        }
                    )
                    
                    color_name = row.get("color_name",None)
                    color_attribute = None
                    if color_name:
                        color_attribute, _ = ColorVariation.objects.update_or_create(
                        color_name=color_name,
                        defaults={"created_by": request.user}
                        )

                    variation_name =row.get("name",None)
                    variation_values = row.get("values",None)
                    variation_attribute = None
                    if variation_name:
                        variation_attribute, _ = AttributeVariation.objects.update_or_create(
                        name=variation_name,
                        defaults={"values": variation_values, "created_by": request.user}
                        )

                    product_variant, _ = ProductVariantAttribute.objects.update_or_create(
                        product=product,
                        color_attribute=color_attribute,
                        variation_attribute=variation_attribute,
                        defaults={"created_by": request.user}
                    )

            return Response({"message": "Product import successful"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
