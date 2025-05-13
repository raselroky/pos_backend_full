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

from purchase.models import Purchase,PurchaseReturn
from purchase.serializers import PurchaseDetailsSerializer,PurchaseReturnDetailsSerializer
from sell.models import Sale,SaleReturn
from sell.serializers import SaleDetailsSerializer,SaleReturnDetailsSerializer
from stock.models import Stocks,StockTransfer,StockAdjustment
from stock.serializers import StocksDetailsSerializer,StockAdjustmentDetailsSerializer,StockTransferDetailsSerializer
from contacts.models import Contact
from contacts.serializers import ContactDetailsSerializer




class PurchaseReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer

    def get_queryset(self):
        queryset = Purchase.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

class PurchaseReturnReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnDetailsSerializer

    def get_queryset(self):
        queryset = PurchaseReturn.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

class SaleReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Sale.objects.all()
    serializer_class=SaleDetailsSerializer

    def get_queryset(self):
        queryset = Sale.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class SaleReturnReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer

    def get_queryset(self):
        queryset = SaleReturn.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset



class StockReportsListViews(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Stocks.objects.all()
    serializer_class=StocksDetailsSerializer

    def get_queryset(self):
        queryset = Stocks.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


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