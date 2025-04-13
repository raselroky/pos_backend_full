from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, ListAPIView,
    RetrieveDestroyAPIView,RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.utils.decorators import method_decorator
from .models import (
    Notification,CsutomizeMessage
)
from .serializers import NotificationSerializer,CustomizeMessageSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Case, When

from django.http import HttpResponse
from rest_framework.views import APIView

from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist





class AdminNotificationListAPIView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Notification.objects.filter()
    serializer_class=NotificationSerializer
    search_fields = ['title', 'verb', 'message']
    #pagination_class = None
    def get_queryset(self):
        
        qs=Notification.objects.all().order_by(
            Case(
                When(is_read=False, then=0),
                default=1
            ),
            '-created_at'
        )
        return qs


class AdminNotificationRetrieveDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Notification.objects.all()
    serializer_class=NotificationSerializer
    lookup_field='id'

    def get_queryset(self):
        current_user=self.request.user
        qs=Notification.objects.all().order_by('-created_at')
        return qs
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.created_by != request.user:
        #     return Response({"message": "You do not have permission to update this notification."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)




class CustomizeMessageListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=CsutomizeMessage.objects.all()
    serializer_class=CustomizeMessageSerializer
    search_fields = ['topics', 'message']

    def get_queryset(self):
        
        return CsutomizeMessage.objects.filter()



class CustomizeMessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=CsutomizeMessage.objects.all()
    serializer_class=CustomizeMessageSerializer
    lookup_field='id'

    def get_queryset(self):
        current_user=self.request.user
        qs=CsutomizeMessage.objects.all().order_by('-created_at')
        return qs
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)