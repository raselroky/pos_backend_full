from django.shortcuts import render
from .serializers import BarcodeSettingSerializer,InvoiceSettingSerializer,BannerSettingSerializer,EmailSettingSerializer,BarcodeSettingDetailsSerializer,InvoiceSettingDetailsSerializer
from .models import BarcodeSetting,InvoiceSetting,BannerSetting,EmailSetting
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
from helper import MainPagination
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from helpers.barcode import generate_barcode_image
from django.db.models import Sum
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.signals import send_notification


class BarcodeSettingListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=BarcodeSetting.objects.all()
    serializer_class=BarcodeSettingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None

        data['assign_branch']=data.get('assign_branch')
        
        with transaction.atomic():
            # Optional: check if same branch already has a setting (if needed)
            existing = BarcodeSetting.objects.filter(assign_branch=data['assign_branch']).first()
            if existing:
                raise ValidationError({"error": "Barcode setting already exists for this branch."})

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

    def get_queryset(self):
        return BarcodeSetting.objects.all()


class BarcodeSettingListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=BarcodeSetting.objects.all()
    serializer_class=BarcodeSettingDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','barcode_enable','assign_branch__branch_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return BarcodeSetting.objects.all()


class BarcodeSettingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=BarcodeSetting.objects.all()
    serializer_class=BarcodeSettingSerializer
    lookup_field='id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        data['updated_by'] = request.user.id

        with transaction.atomic():
            # existing = BarcodeSetting.objects.filter(assign_branch=data['assign_branch']).first()
            # if existing:
            #     raise ValidationError({"error": "Barcode setting already exists for this branch."})
            
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            barcodesetting = serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return BarcodeSetting.objects.all()

class BarcodeSettingRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=BarcodeSetting.objects.all()
    serializer_class=BarcodeSettingDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        return BarcodeSetting.objects.all()
    


### invoice ###



class InvoiceSettingListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=InvoiceSetting.objects.all()
    serializer_class=InvoiceSettingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None

        data['assign_branch']=data.get('assign_branch')
        
        with transaction.atomic():
            # Optional: check if same branch already has a setting (if needed)
            existing = InvoiceSetting.objects.filter(assign_branch=data['assign_branch']).first()
            if existing:
                raise ValidationError({"error": "Invoice setting already exists for this branch."})

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

    def get_queryset(self):
        return InvoiceSetting.objects.all()


class InvoiceSettingListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=InvoiceSetting.objects.all()
    serializer_class=InvoiceSettingDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields =['id','prefix','assign_branch__branch_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return InvoiceSetting.objects.all()


class InvoiceSettingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=InvoiceSetting.objects.all()
    serializer_class=InvoiceSettingSerializer
    lookup_field='id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        data['updated_by'] = request.user.id

        with transaction.atomic():
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            invoicesetting = serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return InvoiceSetting.objects.all()



class InvoiceSettingRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=InvoiceSetting.objects.all()
    serializer_class=InvoiceSettingDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        return InvoiceSetting.objects.all()