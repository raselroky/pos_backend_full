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
from .serializers import ContactSerializer,ContactDetailsSerializer
from .models import Contact
from rest_framework.filters import SearchFilter, OrderingFilter
from helper import MainPagination

class ContactListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactSerializer

    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

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
        return Contact.objects.all()


class ContactListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','business_name','owner_name','conact_id','mobile','email','tax_number']
    pagination_class=MainPagination

    def get_queryset(self):
        return Contact.objects.all()


class ContactRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer
    lookup_field='id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if 'file_image' in request.FILES:
            data['file_image'] = request.FILES['file_image']
        elif 'file_image' in data and data['file_image'] in ["null", "", None]:  
            instance.file_image.delete(save=False)  
            data.pop('file_image')
        
        serializer = self.get_serializer(instance, data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return Contact.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class ContactSupplierListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','business_name','owner_name','conact_id','mobile','email','tax_number']
    pagination_class=MainPagination

    def get_queryset(self):
        return Contact.objects.filter(contactor_type='Suppliers')

class ContactCusotmerListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','business_name','owner_name','conact_id','mobile','email','tax_number']
    pagination_class=MainPagination

    def get_queryset(self):
        return Contact.objects.filter(contactor_type='Customers')

class ContactBothListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Contact.objects.all()
    serializer_class=ContactDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','business_name','owner_name','conact_id','mobile','email','tax_number']
    pagination_class=MainPagination
    
    def get_queryset(self):
        return Contact.objects.filter(contactor_type='Both')