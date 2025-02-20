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
from .serializers import CountrySerializer,CountryDetailsSerializer,BranchSerializer,BranchDetailsSerializer
from .models import Country,Branch
from rest_framework.filters import SearchFilter, OrderingFilter
from helper import MainPagination


class CountryListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Country.objects.all()
    serializer_class=CountrySerializer

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
        return Country.objects.all()


class CountryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Country.objects.all()
    serializer_class=CountryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','country_name','country_code','country_short_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return Country.objects.all()


class CountryRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Country.objects.all()
    serializer_class=CountryDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Country.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


#####barnch



class BranchListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Branch.objects.all()
    serializer_class=BranchSerializer

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
        return Branch.objects.all()


class BranchListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Branch.objects.all()
    serializer_class=BranchDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['country__country_name','country__country_code','country__country_short_name','branch_name','email','phone','address','company_name']
    pagination_class=MainPagination
    
    def get_queryset(self):
        return Branch.objects.all()


class BranchRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Branch.objects.all()
    serializer_class=BranchSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)


    def get_queryset(self):
        
        return Branch.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Item is deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class BranchRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Branch.objects.all()
    serializer_class=BranchDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)


    def get_queryset(self):
        
        return Branch.objects.all()