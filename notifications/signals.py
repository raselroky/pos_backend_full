from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from sell.models import Sale,SaleReturn
from stock.models import StockTransfer,StockAdjustment
from django.conf import settings
from django.db import transaction
from users.models import Users
from django.http import JsonResponse
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)



def send_notification(user_id,notification_message):
    try:
        if isinstance(notification_message, tuple):
            notification_message = ' '.join(notification_message)

        channel_layer = get_channel_layer()

        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                f'user_{user_id}', 
                {
                    'type': 'notify',
                    'message': notification_message
                }
            )
            response_data = {"status": 'Notification sent', "message": notification_message}
            #print('okk,send success')
            return Response(response_data)

        return Response({'error': 'Channel layer is not available'}, status=500)

    except Users.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=404)




def create_notification(title,sender,recipients,verb,message):
    recipients = list(set(recipients)) 
    
    full_message = f"{title}: {message}"
    if recipients:
        for recipient in recipients:
            try:
                send_notification(recipient.id,full_message)    
                
                Notification.objects.create(
                    title=title, 
                    sender=sender,
                    recipient=recipient,
                    verb=verb,
                    message=message
                )
            except Exception as e:
                print(f"Error sending notification to user {recipient.id}: {e}")
    else:
        print("No recipients to send notification.")





@receiver(post_save, sender=Sale)
def send_sale_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            print('sender',sender)
            print('invoice',instance.invoice_no)
            message = f"{instance.invoice_no} This Sale has just been placed by {sender}."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('sale', sender, recipients, 'created', message)

        transaction.on_commit(create_notification_on_commit)