from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductUnit,Brand,Category,SubCategory,ColorVariation,AttributeVariation
from .serializers import ProductUnitSerializer,BrandSerializer,CategorySerializer,SubCategorySerializer,SubCategoryDetailsSerializer,ColorVariationSerializer,AttributeVariationSerializer,SingleCategorySerializer
from users.permissions import IsLogin
from helper import MainPagination
from django.core.mail import EmailMessage
from datetime import timedelta
from django.utils import timezone
import datetime
from django.utils.timezone import make_aware
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import Permission
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView,RetrieveAPIView



class ProductUnitListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ProductUnit.objects.all()
    serializer_class=ProductUnitSerializer

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
        return ProductUnit.objects.all()
    
class ProductUnitListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ProductUnit.objects.all()
    serializer_class=ProductUnitSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','unit_name','unit_short_name']
    pagination_class=MainPagination

class ProductUnitRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ProductUnit.objects.all()
    serializer_class=ProductUnitSerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class BrandListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer

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
        return Brand.objects.all()
    
class BrandListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','brand_name','description']
    pagination_class=MainPagination

class BrandRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class CategoryListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

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
        return Category.objects.all()
    
class CategoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','category_name','description']
    pagination_class=MainPagination


class CategoryRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class SingleCategoryRetrieveAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Category.objects.all()
    serializer_class=SingleCategorySerializer
    lookup_field='id'

    

class SubCategoryListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SubCategory.objects.all()
    serializer_class=SubCategorySerializer

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
        return SubCategory.objects.all()
    
class SubCategoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SubCategory.objects.all()
    serializer_class=SubCategoryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','subcategory_name','subcategory_code','description','category__category_name']
    pagination_class=MainPagination

class SubCategoryRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SubCategory.objects.all()
    serializer_class=SubCategoryDetailsSerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



### variation


class ColorVariationListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ColorVariation.objects.all()
    serializer_class=ColorVariationSerializer

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
        return ColorVariation.objects.all()
    
class ColorVariationListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ColorVariation.objects.all()
    serializer_class=ColorVariationSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','color_name','description']
    pagination_class=MainPagination

class ColorVariationRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ColorVariation.objects.all()
    serializer_class=ColorVariationSerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)




class AttributeVariationListCreateAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AttributeVariation.objects.all()
    serializer_class=AttributeVariationSerializer

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
        return AttributeVariation.objects.all()
    
class AttributeVariationListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AttributeVariation.objects.all()
    serializer_class=AttributeVariationSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','name','values']
    pagination_class=MainPagination
    
class AttributeVariationRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AttributeVariation.objects.all()
    serializer_class=AttributeVariationSerializer
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)