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
from django.db import transaction
from products.models import Product,ProductUnit,AttributeVariation,ColorVariation
from catalog.models import Brand,Category,SubCategory
from rest_framework.exceptions import ValidationError



class StockListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Stocks.objects.all()
    serializer_class = StocksSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['created_by'] = request.user.id 

        
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
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id']
    pagination_class=MainPagination

    def get_queryset(self):
        return Stocks.objects.all()


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
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



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
    search_fields = ['id']
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
    



class StockTransferListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id  

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

           
            stock.available_qty -= quantity
            stock.transfering_qty += quantity  
            stock.save()

            stock_transfer = StockTransfer.objects.create(
                stock=stock,
                quantity=quantity,
                reason=reason,
                accept_branch_id=accept_branch_id,
                given_branch_id=given_branch_id,
                created_by=request.user
            )

            StockHistory.objects.create(
                stock=stock,
                quantity=-quantity,  
                log_type="Stock Transfer Out",
                reference=stock_transfer.id,
                created_by=request.user
            )

            serializer = self.get_serializer(stock_transfer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)



class StockTransfertListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=StockTransfer.objects.all()
    serializer_class=StockTransferDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id']
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