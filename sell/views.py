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
from django.utils.timezone import now
from helpers.barcode import generate_barcode_image
from products.models import ProductBarcodes



class SaleListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        data['invoice_no'] = generate_invoice_no() 

        with transaction.atomic():
            sale_serializer = self.get_serializer(data=data)
            sale_serializer.is_valid(raise_exception=True)
            sale = sale_serializer.save(created_by=request.user)

            sale_history_data = data.get('sale_history', [])
            total_sale_amount = 0
            total_discount_amount = 0

            for item in sale_history_data:
                product_id = item.get('product_variant')
                quantity = item.get('quantity', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])
                if len(barcode) != quantity:
                    return Response({"error": f"Number of barcodes ({len(barcode)}) must match the good quantity ({quantity})."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock with product variant ID {stock.product_variant.product.product_name} does not exist.")
                
                if stock.available_qty < quantity:
                    raise ValidationError(
                        f"Not enough stock available for product {stock.product_variant.product.product_name}. "
                        f"Available: {stock.available_qty}, Requested: {quantity}"
                    )
                
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

                stock.sold_qty += quantity
                stock.available_qty -= quantity
                stock.save()

                StockHistory.objects.create(
                    stock=stock,
                    quantity=-quantity, 
                    price=stock.selling_price, 
                    log_type="Sale",
                    reference=sale.id,
                    created_by=request.user
                )

                total_sale_amount += stock.selling_price * quantity
                total_discount_amount += discount_amount

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)
                        
                        # Validate barcode ownership
                        if barcode_entry.product_variant != stock.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        # Update barcode status
                        barcode_entry.product_status = "Sold"
                        barcode_entry.sold_at = now()
                        barcode_entry.remarks = "Sold via sales transaction"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

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
        data = request.data.copy() 
        data['created_by'] = request.user.id 
        return_no = generate_return_no() 
        data['return_no'] = return_no

        with transaction.atomic():
            sale_return_serializer = self.get_serializer(data=data)
            sale_return_serializer.is_valid(raise_exception=True)
            sale_return = sale_return_serializer.save(created_by=request.user)

            total_return_qty = 0
            total_refund_amount = 0

            sale_return_history_data = data.get('sale_return_history', [])
            for item in sale_return_history_data:
                sale_history_id = item.get('sale_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])
                if len(barcode) != return_qty:
                    return Response({"error": f"Number of barcodes ({len(barcode)}) must match the good quantity ({return_qty})."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    sale_history = SaleHistory.objects.get(id=sale_history_id)
                except SaleHistory.DoesNotExist:
                    raise ValidationError(f"Sale history with ID {sale_history_id} does not exist.")
                
                if return_qty > sale_history.quantity:
                    return Response(
                        {"error": f"Cannot return more than the sold quantity for sale history ID {sale_history_id}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        print(f"Barcode product variant: {barcode_entry.product_variant.id}")
                        print(f"Sale history product variant: {sale_history.product_variant.id}")

                        if barcode_entry.product_variant!= sale_history.product_variant.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the returned product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        barcode_entry.product_status = "Sales Return"
                        barcode_entry.sold_at = None  
                        barcode_entry.sales_return_at = now() 
                        barcode_entry.remarks = "Returned via sales return"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )


                SaleReturnHistory.objects.create(
                    sale_return=sale_return,
                    sale_history=sale_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )
                total_return_qty += return_qty
                total_refund_amount += refund_amount

                try:
                    stock = Stocks.objects.get(id=sale_history.product_variant.id)
                    stock.sold_qty -= return_qty
                    stock.available_qty += return_qty
                    stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=return_qty, 
                        price=sale_history.selling_price, 
                        log_type="Return",  
                        reference=sale_return.id, 
                        created_by=request.user 
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product {sale_history.product_variant} does not exist.")
                
                

                

            sale_return.total_return_qty = total_return_qty
            sale_return.total_refund_amount = total_refund_amount
            sale_return.save()

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