from .views import AdminNotificationListAPIView,AdminNotificationRetrieveDestroyAPIView,CustomizeMessageListCreateAPIView,CustomizeMessageRetrieveUpdateDestroyAPIView
from django.urls import path

urlpatterns=[
    path('admin-notification/',AdminNotificationListAPIView.as_view(),name='admin-notifcation-list'),
    path('admin-notification-retrieve-destroy/<int:id>',AdminNotificationRetrieveDestroyAPIView.as_view(),name='admin-notifcation-retrieve-destroy'),

    path('cutomize-message-create/',CustomizeMessageListCreateAPIView.as_view(),name='cutomize-message-create-api'),
    path('cutomize-message-retrieve-update-destroy/<int:id>',CustomizeMessageRetrieveUpdateDestroyAPIView.as_view(),name='cutomize-message-retrieve-update-destroy'),
]