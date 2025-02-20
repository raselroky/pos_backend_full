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
from .serializers import AdditionalExpenseSerializer,PurchaseSerializer,PurchaseReturnSerializer,PurchaseDetailsSerializer,PurchaseReturnDetailsSerializer,PurchaseHistorySerializer,PurchaseHistoryDetailsSerializer,PurchaseReturnHistorySerializer,PurchaseReturnHistoryDetailsSerializer
from .models import AdditionalExpense,Purchase,PurchaseReturn,PurchaseHistory,PurchaseReturnHistory
from rest_framework.filters import SearchFilter, OrderingFilter
from helpers.invoice import generate_invoice_no,generate_return_no
from helper import MainPagination
from django.db import transaction
from stock.models import Stocks,StockHistory
from products.models import Product,ProductUnit,AttributeVariation,ColorVariation,ProductVariantAttribute
from catalog.models import Brand,Category,SubCategory
from rest_framework.exceptions import ValidationError



class AdditionalExpenseListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    
    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

        data['created_by'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return AdditionalExpense.objects.all()


class AdditionalExpenseListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','expense_name','reason']
    pagination_class=MainPagination

    def get_queryset(self):
        return AdditionalExpense.objects.all()


class AdditionalExpenseRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return AdditionalExpense.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



####### purchase 

class PurchaseListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id

        invoice = generate_invoice_no()
        data['invoice_no'] = invoice

        with transaction.atomic():
            purchase_serializer = self.get_serializer(data=data)
            purchase_serializer.is_valid(raise_exception=True)
            purchase = purchase_serializer.save(created_by=request.user)

            purchase_history_data = data.get('purchase_history', [])
            for item in purchase_history_data:
                product_variant_id = item.get('product_variant')
                try:
                    product_variant = ProductVariantAttribute.objects.get(id=product_variant_id)
                except ProductVariantAttribute.DoesNotExist:
                    return Response({"error": f"Product Variant with ID {product_variant_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                
                
                purchase_quantity = item.get('purchase_quantity', 0)
                good_quantity = item.get('good_quantity', 0)
                demaged_quantity = item.get('demaged_quantity', 0)
                unit_price = item.get('unit_price', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', ""),
                selling_price = item.get('selling_price', 0)

                
                purchase_history = PurchaseHistory.objects.create(
                    purchase=purchase,
                    product_variant=product_variant,
                    purchase_quantity=purchase_quantity,
                    good_quantity=good_quantity,
                    demaged_quantity=demaged_quantity,
                    unit_price=unit_price,
                    discount_amount=discount_amount,
                    discount_percent=discount_percent,
                    warranty=warranty,
                    remark=remark,
                    
                    created_by=request.user
                )

                stock = Stocks.objects.filter(product_variant=product_variant).first() 

                if stock:
                    stock.total_qty += purchase_quantity
                    stock.available_qty += good_quantity
                    stock.purchase_price = unit_price
                    stock.selling_price = selling_price
                    stock.warranty = warranty
                    stock.discount_percentage = discount_percent
                    stock.remark = remark
                    stock.save()
                else:
                    stock = Stocks.objects.create(
                    product_variant=product_variant,
                    total_qty=purchase_quantity,
                    sold_qty=0,
                    hold_qty=0,
                    available_qty=good_quantity,
                    warranty=warranty,
                    purchase_price=unit_price,
                    selling_price=selling_price,
                    discount_percentage=discount_percent,
                    remark=remark,
                    created_by=request.user 
                    )

                StockHistory.objects.create(
                    stock=stock,
                    quantity=good_quantity,
                    price=unit_price,
                    log_type="Purchase",
                    reference=purchase.id,
                    created_by=request.user
                )


            headers = self.get_success_headers(purchase_serializer.data)
            return Response(purchase_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Purchase.objects.all()



class PurchaseListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','purchase_status','pay_term','product__product_name','product__sku','product__category__category_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return Purchase.objects.all()


class PurchaseRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Purchase.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PurchaseRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Purchase.objects.all()


####### purchase history 

class PurchaseHistoryListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistorySerializer
    
    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

        data['created_by'] = request.user.id
        invoice=generate_invoice_no()
        data['invoice_no']=invoice

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return PurchaseHistory.objects.all()


class PurchaseHistoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistoryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','product__product_name','product__sku','product__category__category_name','purchase__id','purchase__invoice_no','brand__brand_name','size__name','size__values','color__color_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return PurchaseHistory.objects.all()


class PurchaseHistoryRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistorySerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseHistory.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PurchaseHistoryRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistoryDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseHistory.objects.all()
    



##### purchase return

class PurchaseReturnListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PurchaseReturn.objects.all()
    serializer_class = PurchaseReturnSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        return_no = generate_return_no()
        data['return_no'] = return_no
        with transaction.atomic():
            purchase_return_serializer = self.get_serializer(data=data)
            purchase_return_serializer.is_valid(raise_exception=True)
            purchase_return = purchase_return_serializer.save(created_by=request.user)

            purchase_return_history_data = data.get('purchase_return_history', [])
            total_return_qty = 0
            total_refund_amount = 0

            for item in purchase_return_history_data:
                purchase_history_id = item.get('purchase_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")

                # Retrieve the corresponding purchase history
                try:
                    purchase_history = PurchaseHistory.objects.get(id=purchase_history_id)
                except PurchaseHistory.DoesNotExist:
                    raise ValidationError(f"Purchase history with ID {purchase_history_id} does not exist.")

                # Create purchase return history entry
                purchase_return_history = PurchaseReturnHistory.objects.create(
                    purchase_return=purchase_return,
                    purchase_history=purchase_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )

                total_return_qty += return_qty
                total_refund_amount += refund_amount

                # Update stock quantities based on the return
                try:
                    stock = Stocks.objects.get(product_variant=purchase_history.product_variant)
                    # Update stock: Reduce available quantity by return_qty
                    stock.available_qty -= return_qty

                    # If the returned quantity was previously sold, decrease sold_qty as well
                    stock.sold_qty -= return_qty
                    stock.save()

                    # Create a stock history entry for the return
                    StockHistory.objects.create(
                        stock=stock,
                        quantity=-return_qty,  # Negative quantity indicates return
                        price=purchase_history.unit_price,  # Use unit price from purchase history
                        log_type="Return",  # Log type indicating return operation
                        reference=purchase_return.id,
                        created_by=request.user  # Log the user who performed the operation
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product variant {purchase_history.product_variant.product.product_name} does not exist.")

            # Update the purchase return model with the total return quantities and refund amounts
            purchase_return.total_return_qty = total_return_qty
            purchase_return.total_refund_amount = total_refund_amount
            purchase_return.save()

            headers = self.get_success_headers(purchase_return_serializer.data)
            return Response(purchase_return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return PurchaseReturn.objects.all()


class PurchaseReturnListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','purchase__supplier__business_name','return_date','total_refund_amount','total_return_qty','purchase__invoice_no','purchase__supplier__mobile','purchase__supplier__email']
    pagination_class=MainPagination

    def get_queryset(self):
        return PurchaseReturn.objects.all()


class PurchaseReturnRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturn.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PurchaseReturnRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturn.objects.all()



###### purchase return history

class PurchaseReturnHistoryListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistorySerializer
    
    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

        data['created_by'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return PurchaseReturnHistory.objects.all()


class PurchaseReturnHistoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistoryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','purchase_return__purchase__invoice_no','purchase_return__purchase__supplier__business_name','return_qty','refund_amount','purchase_return__purchase__supplier__email','purchase_return__purchase__supplier__mobile','refund_amount','purchase_history__product__product_name','purchase_history__product__sku','purchase_history__product__country','purchase_history__product__brand__brand_name','purchase_history__product__category__category_name','purchase_history__color__color_name','purchase_history__size__name','purchase_history__size__values','purchase_history__purchase__invoice_no']
    pagination_class=MainPagination
    
    def get_queryset(self):
        return PurchaseReturnHistory.objects.all()


class PurchaseReturnHistoryRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistorySerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturnHistory.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PurchaseReturnHistoryRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistoryDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturnHistory.objects.all()