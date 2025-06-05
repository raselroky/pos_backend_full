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
from .serializers import StocksSerializer,StocksHistorySerializer,StocksDetailsSerializer,StockAdjustmentSerializer,StockTransferSerializer,StockAdjustmentDetailsSerializer,StockTransferDetailsSerializer
from .models import Stocks,StockHistory,StockAdjustment,StockTransfer
from rest_framework.filters import SearchFilter, OrderingFilter
from helpers.invoice import generate_invoice_no
from helper import MainPagination
from helpers.searching import CustomSearchFilter,FlexibleSearchFilter
from django.db import transaction
from products.models import Product,ProductVariantAttribute,ProductBarcodes
from products.serializers import ProductSerializer,ProductVariantAttributeSerializer,ProductBarcodesSerializer
from catalog.models import Brand,Category,SubCategory,ColorVariation,AttributeVariation,ProductUnit
from catalog.serializers import BrandSerializer,CategorySerializer,SubCategorySerializer,ProductUnitSerializer,ColorVariationSerializer,AttributeVariationSerializer
from rest_framework.exceptions import ValidationError
import pandas as pd
from rest_framework.parsers import MultiPartParser
from datetime import datetime
from helpers.identifier_builders import identifier_builder



class StockListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Stocks.objects.all()
    serializer_class = StocksSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['created_by'] = request.user.id 
        data['branch'] = request.user.branch.id if request.user.branch else None
        
        product_variant_id = data.get('product_variant')
        purchase_quantity = float(data.get('total_qty', 0)) 
        unit_price = float(data.get('purchase_price', 0))
        selling_price = float(data.get('selling_price', 0))
        warranty = int(data.get('warranty', 0))
        remark = data.get('remark', '')

        with transaction.atomic(): 
            stock, created = Stocks.objects.get_or_create(
                product_variant_id=product_variant_id,  
                defaults={
                    "total_qty": 0,
                    "sold_qty": 0,
                    "hold_qty": 0,
                    "available_qty": 0,
                    "warranty": warranty,
                    "purchase_price": unit_price,
                    "selling_price": selling_price, 
                    "discount_percentage": 0,  
                    "remark": remark,
                    "created_by": request.user
                }
            )

            if not created:
                stock.total_qty += purchase_quantity 
                stock.available_qty += purchase_quantity 
            else:
                stock.purchase_price = unit_price 
                stock.selling_price = selling_price

            stock.save() 

           
            StockHistory.objects.create(
                stock=stock,
                quantity=purchase_quantity,
                price=unit_price,
                log_type="Purchase",
                reference=stock.id, 
                created_by=request.user 
            )

           
            serializer = self.get_serializer(stock)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Stocks.objects.all()
    


class StockListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Stocks.objects.all()
    serializer_class=StocksDetailsSerializer
    filter_backends = [OrderingFilter,SearchFilter]
    search_fields = ['id','product_variant__product__product_name','product_variant__product__sku','product_variant__product__category__category_name','product_variant__product__brand__brand_name']
    pagination_class=MainPagination

    def get_queryset(self):
        queryset = Stocks.objects.all()
        barcode_search = self.request.query_params.get('barcode', None)
 
        if barcode_search:
            barcode_qs = ProductBarcodes.objects.filter(barcode__iexact=barcode_search,product_status='Purchased')

            # if not barcode_qs.exists():
            #     return Stocks.objects.none()
            variant_ids = barcode_qs.values_list('product_variant_id', flat=True)
            queryset = queryset.filter(product_variant_id__in=variant_ids)

        return queryset



class StockRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Stocks.objects.all()
    serializer_class=StocksSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Stocks.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



class StockRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Stocks.objects.all()
    serializer_class=StocksDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        return Stocks.objects.all()




######## stock adjustment and transfer


class StockAdjustmentListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id  
        data['branch'] = request.user.branch.id if request.user.branch else None
        stock_id = data.get('stock')
        quantity = float(data.get('quantity', 0))
        reason = data.get('reason', '')
        accept_branch_id = data.get('accept_branch')
        given_branch_id = data.get('given_branch')

        with transaction.atomic():
           
            try:
                stock = Stocks.objects.get(id=stock_id)
            except Stocks.DoesNotExist:
                raise ValidationError(f"Stock with ID {stock_id} does not exist.")

            stock.available_qty += quantity  
            stock.save()

            stock_adjustment = StockAdjustment.objects.create(
                stock=stock,
                quantity=quantity,
                reason=reason,
                accept_branch_id=accept_branch_id,
                given_branch_id=given_branch_id,
                created_by=request.user
            )

            # **DO NOT IMMEDIATELY ADD TO STOCK** (Stock adjustment needs approval before affecting inventory)

          
            StockHistory.objects.create(
                stock=stock,
                quantity=quantity, 
                log_type="Adjustment Pending",
                reference=stock_adjustment.id,
                created_by=request.user
            )

            serializer = self.get_serializer(stock_adjustment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class StockAdjustmentListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=StockAdjustment.objects.all()
    serializer_class=StockAdjustmentDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','reason','stock__product_variant__product__product_name','stock__product_variant__product__sku']
    pagination_class=MainPagination

    def get_queryset(self):
        return StockAdjustment.objects.all()


class StockAdjustmentRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=StockAdjustment.objects.all()
    serializer_class=StockAdjustmentSerializer
    lookup_field='id'

    def get_queryset(self):
        return StockAdjustment.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    



class StockTransferListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id  
        data['branch'] = request.user.branch.id if request.user.branch else None
        stock_id = data.get('stock')
        quantity = float(data.get('quantity', 0))
        reason = data.get('reason', '')
        accept_branch_id = data.get('accept_branch')
        given_branch_id = data.get('given_branch')

        with transaction.atomic():
            try:
                stock = Stocks.objects.get(id=stock_id)
            except Stocks.DoesNotExist:
                raise ValidationError(f"Stock with ID {stock_id} does not exist.")

            if stock.available_qty < quantity:
                raise ValidationError(f"Not enough stock available. Current available stock: {stock.available_qty}")

           
            # stock.available_qty -= quantity
            # stock.transfering_qty += quantity  
            # stock.save()

            stock_transfer = StockTransfer.objects.create(
                stock=stock,
                quantity=quantity,
                reason=reason,
                accept_branch_id=accept_branch_id,
                given_branch_id=given_branch_id,
                created_by=request.user
            )

            # StockHistory.objects.create(
            #     stock=stock,
            #     quantity=-quantity,  
            #     log_type="Stock Transfer Pending",
            #     reference=stock_transfer.id,
            #     created_by=request.user
            # )

            serializer = self.get_serializer(stock_transfer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)



class StockTransfertListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=StockTransfer.objects.all()
    serializer_class=StockTransferDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','reason','stock__product_variant__product__product_name','stock__product_variant__product__sku']
    pagination_class=MainPagination

    def get_queryset(self):
        return StockTransfer.objects.all()


class StockTransferRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=StockTransfer.objects.all()
    serializer_class=StockTransferSerializer
    lookup_field='id'

    def get_queryset(self):
        return StockTransfer.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        if data.get("is_accept") and not instance.is_accept:
            with transaction.atomic():
                stock = instance.stock
                quantity = instance.quantity
                accept_branch = instance.accept_branch
                given_branch = instance.given_branch

                if stock.available_qty < quantity:
                    raise ValidationError(f"Not enough stock to approve. Current: {stock.available_qty}")

                stock.available_qty -= quantity
                stock.transfering_qty += quantity  
                stock.save()

                instance.is_accept = True
                instance.save()

                StockHistory.objects.create(
                    stock=stock,
                    quantity=-quantity,
                    log_type="Transferred from Branch",
                    reference=instance.id,
                    created_by=request.user
                )

                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return super().update(request, *args, **kwargs)






########## Import ##########


class ImportExcelStockAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine="openpyxl")
            df.fillna(None, inplace=True) 

            with transaction.atomic():
                stock_history_entries = []

                for _, row in df.iterrows():
                    product_name = row.get("product_name") 
                    sku = row.get("sku", identifier_builder("products"))
                    weight = row.get("weight", 0) 
                    product_type = row.get("product_type", "Single")  
                    country = row.get("country", None) 
                    vat_percentage = row.get("vat_percentage", 0.0) 
                    description = row.get("description", None) 

                    unit_name = row.get("unit_name")  
                    unit_short_name = row.get("unit_short_name",None)  
                    unit, _ = ProductUnit.objects.get_or_create(
                        unit_name=unit_name,
                        defaults={"unit_short_name": unit_short_name, "created_by": request.user}
                    ) if unit_name else (None, None)

                    brand_name = row.get("brand_name")
                    brand_description = row.get("brand_description",None) 
                    brand_image = row.get("brand_image", None) 
                    brand, _ = Brand.objects.get_or_create(
                        brand_name=brand_name,
                        defaults={
                            "description": brand_description, 
                            "image": brand_image,
                              "created_by": request.user}
                    ) if brand_name else (None, None)

                    category_name = row.get("category_name")  
                    category_code = row.get("category_code", None)  
                    category_description = row.get("category_description",None)  
                    category_image = row.get("category_image", None)  
                    category, _ = Category.objects.get_or_create(
                        category_name=category_name,
                        defaults={
                            "category_code": category_code,
                            "description": category_description,
                            "image": category_image, 
                            "created_by": request.user}
                    ) if category_name else (None, None)

                    subcategory_name = row.get("subcategory_name",None) 
                    subcategory_code = row.get("subcategory_code", None)  
                    subcategory_description = row.get("subcategory_description",None)  
                    subcategory_image = row.get("subcategory_image", None)  
                    sub_category, _ = SubCategory.objects.get_or_create(
                        subcategory_name=subcategory_name,
                        defaults={
                            "category": category,
                            "subcategory_code": subcategory_code,
                            "description": subcategory_description,
                            "image": subcategory_image,
                            "created_by": request.user
                        }
                    ) if subcategory_name else (None, None)

                    product_data = {
                        "product_name": product_name,
                        "sku": sku,
                        "unit": unit,
                        "category": category,
                        "sub_category": sub_category,
                        "brand": brand,
                        "weight": weight,
                        "product_type": product_type,
                        "country": country,
                        "vat_percentage": vat_percentage,
                        "description": description,
                    }

                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save(created_by=request.user)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    color_name = row.get("color_name",None)
                    color_attribute = None
                    if color_name:
                        color_attribute, _ = ColorVariation.objects.get_or_create(
                        color_name=color_name,
                        defaults={"created_by": request.user}
                        )

                    variation_name = row.get("name",None) 
                    variation_values = row.get("values",None)
                    variation_attribute = None
                    if variation_name:
                        variation_attribute, _ = AttributeVariation.objects.get_or_create(
                        name=variation_name,
                        defaults={"values": variation_values, "created_by": request.user}
                        )

                    product_variant, _ = ProductVariantAttribute.objects.get_or_create(
                        product=product,
                        color_attribute=color_attribute,
                        variation_attribute=variation_attribute,
                        defaults={"created_by": request.user}
                    )

                    stock_data = {
                        "total_qty": row.get("total_qty", 0), 
                        "sold_qty": row.get("sold_qty", 0),
                        "hold_qty": row.get("hold_qty", 0), 
                        "available_qty": row.get("available_qty", 0),  
                        "transfering_qty": row.get("transfering_qty", 0),  
                        "warranty": row.get("warranty", 0),
                        "purchase_price": row.get("purchase_price", 0.0),
                        "selling_price": row.get("selling_price", 0.0), 
                        "discount_percentage": row.get("discount_percentage", 0.0), 
                        "remark": row.get("remark", None),  
                    }

                    stock, created_stock = Stocks.objects.get_or_create(
                        product_variant=product_variant,
                        defaults=stock_data
                    )

                    if not created_stock:
                        for field, value in stock_data.items():
                            if field != "product_variant":
                                existing_value = getattr(stock, field)
                                setattr(stock, field, existing_value + value if isinstance(value, (int, float)) else value)
                        stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=stock_data["total_qty"],
                        price=stock_data["purchase_price"],
                        log_type="Import",
                        reference=None
                    )

            return Response({"message": "Stock imported successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)