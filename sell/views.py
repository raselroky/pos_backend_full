from django.shortcuts import render
from .serializers import SaleSerializer,SaleHistorySerializer,SaleReturnSerializer,SaleReturnHistorySerializer,SaleReturnDetailsSerializer,SaleDetailsSerializer
from .models import Sale,SaleHistory,SaleReturn,SaleReturnHistory
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.filters import SearchFilter, OrderingFilter
from helpers.invoice import generate_invoice_no,generate_return_no
from helper import MainPagination
from django.db import transaction
from stock.models import Stocks,StockHistory
from rest_framework.exceptions import ValidationError



class SaleListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    
    def create(self, request, *args, **kwargs):
        # Make data mutable and add created_by
        data = request.data.copy()
        data['created_by'] = request.user.id  # Add created_by to data
        data['invoice_no'] = generate_invoice_no()  # Generate invoice number

        # Use atomic transaction to ensure all operations are done together
        with transaction.atomic():
            # Create Sale object
            sale_serializer = self.get_serializer(data=data)
            sale_serializer.is_valid(raise_exception=True)
            sale = sale_serializer.save(created_by=request.user)

            sale_history_data = data.get('sale_history', [])
            total_sale_amount = 0
            total_discount_amount = 0

            # Handle SaleHistory and Stock updates
            for item in sale_history_data:
                product_id = item.get('product_variant')
                quantity = item.get('quantity', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', "")

                # Retrieve the product stock record
                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock with product variant ID {stock.product_variant.product.product_name} does not exist.")
                
                if stock.available_qty < quantity:
                    raise ValidationError(
                        f"Not enough stock available for product {stock.product_variant.product.product_name}. "
                        f"Available: {stock.available_qty}, Requested: {quantity}"
                    )
                
                # Create SaleHistory for this item
                sale_history = SaleHistory.objects.create(
                    sale=sale,
                    product_variant=stock,
                    quantity=quantity,
                    unit_price=stock.purchase_price,
                    selling_price=stock.selling_price,
                    discount_amount=discount_amount,
                    discount_percent=discount_percent,
                    warranty=warranty,
                    remark=remark,
                    created_by=request.user
                )

                # Update stock information (sold quantity and available quantity)
                stock.sold_qty += quantity
                stock.available_qty -= quantity
                stock.save()

                # Record the stock history for the sale
                StockHistory.objects.create(
                    stock=stock,
                    quantity=-quantity,  # Negative because it's a sale (decrease stock)
                    price=stock.selling_price,  # Using unit price from SaleHistory
                    log_type="Sale",
                    reference=sale.id,
                    created_by=request.user
                )

                # Update total sale amount and discount
                total_sale_amount += stock.selling_price * quantity
                total_discount_amount += discount_amount

            # Update the Sale object with total amounts
            sale.total_amount = total_sale_amount
            sale.discount_amount = total_discount_amount
            sale.sub_total = total_sale_amount - total_discount_amount
            sale.due_amount = sale.total_amount - sale.paid_amount
            sale.save()

            headers = self.get_success_headers(sale_serializer.data)
            return Response(sale_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Sale.objects.all()

class SaleListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Sale.objects.all()
    serializer_class=SaleDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id']
    pagination_class=MainPagination

    def get_queryset(self):
        return Sale.objects.all()


class SaleRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Sale.objects.all()
    serializer_class=SaleSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Sale.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    


### salereturn 



class SaleReturnListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SaleReturn.objects.all()
    serializer_class = SaleReturnSerializer
    
    def create(self, request, *args, **kwargs):
        # Copy and prepare data
        data = request.data.copy()  # Make data mutable
        data['created_by'] = request.user.id  # Add created_by field to the data
        return_no = generate_return_no()  # Generate unique return number
        data['return_no'] = return_no

        # Start a transaction for atomic operations
        with transaction.atomic():
            # Create SaleReturn object
            sale_return_serializer = self.get_serializer(data=data)
            sale_return_serializer.is_valid(raise_exception=True)
            sale_return = sale_return_serializer.save(created_by=request.user)

            # Initialize totals
            total_return_qty = 0
            total_refund_amount = 0

            # Process each sale return history entry
            sale_return_history_data = data.get('sale_return_history', [])
            for item in sale_return_history_data:
                sale_history_id = item.get('sale_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")

                # Retrieve the related SaleHistory entry
                try:
                    sale_history = SaleHistory.objects.get(id=sale_history_id)
                except SaleHistory.DoesNotExist:
                    raise ValidationError(f"Sale history with ID {sale_history_id} does not exist.")

                # Create SaleReturnHistory entry
                SaleReturnHistory.objects.create(
                    sale_return=sale_return,
                    sale_history=sale_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )

                # Update stock information (increase available quantity and decrease sold quantity)
                try:
                    stock = Stocks.objects.get(id=sale_history.product_variant.id)
                    # Adjust stock: Decrease sold_qty and increase available_qty
                    stock.sold_qty -= return_qty
                    stock.available_qty += return_qty
                    stock.save()

                    # Create a StockHistory entry for the return
                    StockHistory.objects.create(
                        stock=stock,
                        quantity=return_qty,  # Positive quantity indicates return (stock increase)
                        price=sale_history.selling_price,  # Use unit price from SaleHistory
                        log_type="Return",  # Log type indicating return operation
                        reference=sale_return.id,  # Reference to SaleReturn
                        created_by=request.user  # Log the user who performed the operation
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product {sale_history.product_variant.id} does not exist.")

                # Update total quantities and refund amounts
                total_return_qty += return_qty
                total_refund_amount += refund_amount

            # Update SaleReturn object with total quantities and refund amount
            sale_return.total_return_qty = total_return_qty
            sale_return.total_refund_amount = total_refund_amount
            sale_return.save()

            # Return success response
            headers = self.get_success_headers(sale_return_serializer.data)
            return Response(sale_return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_success_headers(self, data):
        return {'Location': f"/sale_returns/{data.get('id')}/"}


class SaleReturnListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id']
    pagination_class=MainPagination

    def get_queryset(self):
        return SaleReturn.objects.all()


class SaleReturnRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return SaleReturn.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




class SaleReturnRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        return SaleReturn.objects.all()