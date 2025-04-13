from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from sell.models import Sale,SaleReturn
from purchase.models import Purchase,PurchaseReturn
from stock.models import StockTransfer,StockAdjustment,Stocks
from products.models import ProductVariantAttribute
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



@receiver(post_save, sender=ProductVariantAttribute)
def send_productvariantattribute_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.product}-{instance.color_attribute}-{instance.variation_attribute}- This item has created_by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('product variant', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)


@receiver(post_save, sender=Purchase)
def send_purchase_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.invoice_no} This Purchase has just been placed by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('purchase', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)

@receiver(post_save, sender=PurchaseReturn)
def send_purchasereturn_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.return_no} This Purchase Return has just been placed by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('purchase return', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)



@receiver(post_save, sender=Sale)
def send_sale_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.invoice_no} This Sale has just been placed by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('sale', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)

@receiver(post_save, sender=SaleReturn)
def send_salereturn_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.return_no} This Sale Return has just been placed by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('sale return', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)

@receiver(post_save, sender=Stocks)
def send_stock_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.product_variant} ({instance.available_qty})- This item has just been placed for stock by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('stock', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)

@receiver(post_save, sender=StockTransfer)
def send_stocktransfer_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.stock.product_variant}-({instance.quantity})- This item has just been placed for transfer by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('stock transfer', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)

@receiver(post_save, sender=StockAdjustment)
def send_stockadjustment_notification(sender, instance, created, **kwargs):
    if created:
        def create_notification_on_commit():
            sender = instance.created_by if instance.created_by else None
            branch = sender.branch if sender and sender.branch else None
            # print(branch)
            # print('sender',sender)
            # print('invoice',instance.invoice_no)
            message = f"{instance.stock.product_variant}-({instance.quantity})- This item has just been placed for adjustment by {sender}-({branch})."
            admin_user=Users.objects.filter(is_superuser=True,is_staff=True)
            #print('recipient',admin_user)
            recipients=list(set(admin_user))
            for admin in recipients:
                send_notification(admin.id,message)
            create_notification('stock adjustment', sender, recipients, 'created', message)
        transaction.on_commit(create_notification_on_commit)