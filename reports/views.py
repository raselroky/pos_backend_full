from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from helper import MainPagination
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser

from purchase.models import Purchase,PurchaseReturn,PurchaseHistory,PurchaseReturnHistory
from purchase.serializers import PurchaseDetailsSerializer,PurchaseReturnDetailsSerializer
from sell.models import Sale,SaleReturn,SaleHistory,SaleReturnHistory
from sell.serializers import SaleDetailsSerializer,SaleReturnDetailsSerializer
from stock.models import Stocks,StockTransfer,StockAdjustment,StockHistory
from stock.serializers import StocksDetailsSerializer,StockAdjustmentDetailsSerializer,StockTransferDetailsSerializer
from contacts.models import Contact
from contacts.serializers import ContactDetailsSerializer
from django.db.models import Sum, F, FloatField, ExpressionWrapper




class PurchaseReportsListViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = Purchase.objects.all()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        total_purchase=queryset.count()
        total_purchase_amount=0
        total_purchase_due=0
        total_discount_amount=0
        total_vat_amount=0
        product_discount=0
        product_vat=0
        product_amount_iv=0
        product_amount_wv=0
        total_paid_amount=0
        purchase_qunatity=0
        good_qunatity=0
        damage_qunatity=0
        count=0
        for iset in queryset:
            total_purchase_amount+=iset.total_amount
            total_purchase_due+=iset.due_amount
            total_discount_amount+=iset.discount_amount
            total_vat_amount+=iset.vat_amount
            total_paid_amount+=iset.paid_amount
            ph=PurchaseHistory.objects.filter(purchase__invoice_no=iset.invoice_no)
            for jset in ph:
                product_discount+=jset.discount_amount
                product_vat+=jset.vat_amounts
                product_amount_iv+=jset.total_amount_iv
                product_amount_wv+=jset.total_amount_wv
                purchase_qunatity+=jset.purchase_quantity
                good_qunatity+=jset.good_quantity
                damage_qunatity+=jset.demaged_quantity
                count+=1
                
        
                
        data={
            "total_purchase":total_purchase,
            "total_purchase_amount":total_purchase_amount,
            "total_paid_amount":total_paid_amount,
            "total_purchase_due":total_purchase_due,
            "total_discount_amount":total_discount_amount,
            "total_vat_amount":total_vat_amount,
            "products":{
                "total_product":count,
                "total_purchase_qunatity":purchase_qunatity,
                "total_good_qunatity":good_qunatity,
                "total_damage_quantity":damage_qunatity,
                "total_product_discount":product_discount,
                "total_product_vat":product_vat,
                "total_product_amount_iv":product_amount_iv,
                "total_product_amount_wv":product_amount_wv
            }
        }

        return Response(data)

class PurchaseReturnReportsListViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = PurchaseReturn.objects.all()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        total_purchasereturn=queryset.count()
        total_purchasereturn_amount=0
        total_purchasereturn_due=0
        
        purchasereturn_qunatity=0
        refund_amount=0
        purchasereturn_qunatity=0
        count=0
        for iset in queryset:
            total_purchasereturn_amount+=iset.total_refund_amount
            
            prh=PurchaseReturnHistory.objects.filter(purchase_return__return_no=iset.return_no)
            for jset in prh:
                purchasereturn_qunatity+=jset.return_qty
                refund_amount+=jset.refund_amount
                count+=1
                
        
                
        data={
            "total_purchasereturn":total_purchasereturn,
            "total_purchasereturn_amount":total_purchasereturn_amount,
            "products":{
                "total_product":count,
                "purchasereturn_qunatity":purchasereturn_qunatity
                
            }
        }

        return Response(data)

class SaleReportsListViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = Sale.objects.all()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        total_sell=queryset.count()
        total_sell_amount=0
        total_sell_due=0
        total_discount_amount=0
        total_vat_amount=0
        product_discount=0
        product_vat=0
        product_amount_iv=0
        product_amount_wv=0
        total_paid_amount=0
        sell_qunatity=0
        purchase_price=0
        selling_price=0
        count=0
        for iset in queryset:
            total_sell_amount+=iset.total_amount
            total_sell_due+=iset.due_amount
            total_discount_amount+=iset.discount_amount
            total_vat_amount+=iset.vat_amount
            total_paid_amount+=iset.paid_amount
            sl=SaleHistory.objects.filter(sale__invoice_no=iset.invoice_no)
            for jset in sl:
                stp=Stocks.objects.filter(product_variant__id=jset.product_variant.id).first()
                purchase_price+=stp.purchase_price
                selling_price+=stp.selling_price
                product_discount+=jset.discount_amount
                product_vat+=jset.vat_amounts
                product_amount_iv+=jset.total_amount_iv
                product_amount_wv+=jset.total_amount_wv
                sell_qunatity+=jset.quantity
                count+=1
                
                
        
                
        data={
            "total_sell":total_sell,
            "total_sell_amount":total_sell_amount,
            "total_paid_amount":total_paid_amount,
            "total_sell_due":total_sell_due,
            "total_discount_amount":total_discount_amount,
            "total_vat_amount":total_vat_amount,
            "products":{
                "total_product":count,
                "total_sell_qunatity":sell_qunatity,
                "total_product_discount":product_discount,
                "total_product_vat":product_vat,
                "total_product_amount_iv":product_amount_iv,
                "total_product_amount_wv":product_amount_wv,
                "total_purchase_price":purchase_price,
                "total_selling_price":selling_price
            }
        }

        return Response(data)



class SaleReturnReportsListViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = SaleReturn.objects.all()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        total_salereturn=queryset.count()
        total_salereturn_amount=0
        total_salereturn_due=0
        
        salereturn_qunatity=0
        refund_amount=0
        salereturn_qunatity=0
        count=0
        for iset in queryset:
            total_salereturn_amount+=iset.total_refund_amount
            
            slh=SaleReturnHistory.objects.filter(sale_return__return_no=iset.return_no)
            for jset in slh:
                salereturn_qunatity+=jset.return_qty
                refund_amount+=jset.refund_amount
                count+=1
                
        
                
        data={
            "total_salereturn":total_salereturn,
            "total_salereturn_amount":total_salereturn_amount,
            "products":{
                "total_product":count,
                "salereturn_qunatity":salereturn_qunatity
                
            }
        }

        return Response(data)





class StockReportsListViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = Stocks.objects.all()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        total_stock=queryset.count()
        #print(queryset)
        total_quantity=0
        total_sold_quantity=0
        total_hold_quantity=0
        total_available_quantity=0
        total_transfer_quantity=0
        total_purchase_amount=0
        total_selling_amount=0

        price=0
        sell_qunatity=0
        count=0
        for iset in queryset:
            total_quantity+=iset.total_qty
            total_sold_quantity+=iset.sold_qty
            total_hold_quantity+=iset.hold_qty
            total_available_quantity+=iset.available_qty
            total_transfer_quantity+=iset.transfering_qty
            total_purchase_amount+=iset.purchase_price
            total_selling_amount+=iset.selling_price

            sth=StockHistory.objects.filter(stock__id=iset.id)
            for jset in sth:
                price+=jset.price
                sell_qunatity+=jset.quantity
                
                count+=1
                
                
        
                
        data={
            "total_stock":total_stock,
            "total_quantity":total_quantity,
            "total_sold_quantity":total_sold_quantity,
            "total_hold_quantity":total_hold_quantity,
            "total_available_quantity":total_available_quantity,
            "total_transfer_quantity":total_transfer_quantity,
            "total_purchase_amount":total_purchase_amount,
            "total_selling_amount":total_selling_amount,
            "products":{
                "total_product":count,
                "total_price":price,
                "total_sell_quantity":sell_qunatity
                
            }
        }

        return Response(data)


class StockTransferReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=StockTransfer.objects.all()
    serializer_class=StockTransferDetailsSerializer

    def get_queryset(self):
        queryset = StockTransfer.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class StockAdjustmentReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=StockAdjustment.objects.all()
    serializer_class=StockAdjustmentDetailsSerializer

    def get_queryset(self):
        queryset =StockAdjustment.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')


        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset




class CustomerReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer


    def get_queryset(self):
        queryset =Contact.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date,contactor_type='Customers')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date,contactor_type='Customers')

        return queryset

class SupplierReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer


    def get_queryset(self):
        queryset =Contact.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date,contactor_type='Suppliers')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date,contactor_type='Suppliers')

        return queryset