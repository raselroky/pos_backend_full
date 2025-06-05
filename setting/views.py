from django.shortcuts import render
from .serializers import BarcodeSettingSerializer,InvoiceSettingSerializer,BannerSettingSerializer,BarcodeSettingDetailsSerializer,InvoiceSettingDetailsSerializer,GeneralSettingSerializer,GeneralSettingSerializerDetails
from .models import BarcodeSetting,InvoiceSetting,BannerSetting,GeneralSetting
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
from helpers.email_settings import sending_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



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



##############

class GeneralSettingListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=GeneralSetting.objects.all()
    serializer_class=GeneralSettingSerializer

    def create(self, request, *args, **kwargs):
        if GeneralSetting.objects.exists():
            return Response(
                {"error": "Title already exists. You can’t create more than one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None


        with transaction.atomic():
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

    def get_queryset(self):
        return GeneralSetting.objects.all()


class GeneralSettingListAPIView(ListAPIView):
    permission_classes=[AllowAny,]
    queryset=GeneralSetting.objects.all()
    serializer_class=GeneralSettingSerializerDetails
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields =['id','title_name']
    pagination_class=MainPagination

    def get_queryset(self):
        return GeneralSetting.objects.all()


class GeneralSettingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=GeneralSetting.objects.all()
    serializer_class=GeneralSettingSerializer
    lookup_field='id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        data['updated_by'] = request.user.id

        with transaction.atomic():
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            title = serializer.save(updated_by=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return GeneralSetting.objects.all()



###### email send



class SendEmailAPIView(APIView):
    def post(self, request):
        subject = request.data.get("subject")
        body = request.data.get("body")

        to_emails = request.data.get("to", [])
        if isinstance(to_emails, str):
            to_emails = [email.strip() for email in to_emails.split(",") if email.strip()]

        if not subject or not to_emails:
            return Response({"error": "Subject and recipients are required."}, status=status.HTTP_400_BAD_REQUEST)

        for email in to_emails:
            try:
                validate_email(email)
            except ValidationError:
                return Response({"error": f"Invalid email: {email}"}, status=status.HTTP_400_BAD_REQUEST)


        attachments = request.FILES.getlist("attachments")
        attachment_names = [file.name for file in attachments]
        company_name = "Your Company"
        if GeneralSetting.objects.exists():
            company = GeneralSetting.objects.first()
            company_name = company.company_name
            address=company.company_address
        try:
            sending_email(
                subject=subject,
                body=body,
                to_emails=to_emails,
                html_template="send_formal.html",
                context={
                    "subject": subject,
                    "body": body,
                    "company": company_name,
                    "attachment_names": attachment_names,
                    "role":"Admin"
                    
                    },
                attachments=attachments
            )
            return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

