
from rest_framework import serializers
from .models import Notification,CsutomizeMessage

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    

    def get_unread_count(self, obj):
        unread_count = Notification.objects.filter(is_read=False, recipient=self.context['request'].user).count()
        return unread_count

    def get_read_count(self, obj):
        read_count = Notification.objects.filter(is_read=True, recipient=self.context['request'].user).count()
        return read_count

    def get_sender(self, obj):
        sender = obj.sender
        if sender:
            return {
                "sender_username": sender.email,
                "sender_branch":sender.branch_name,
                "sender_country":sender.country,
                "sender_address":sender.address,
                "sender_role":sender.role.title
               
            }
        return None 

    def get_recipient(self, obj):
        recipient = obj.recipient
        
        if recipient:
            return {
                "recipient_username": recipient.email
                
            }
        return None 

    class Meta:
        model = Notification
        fields = "__all__"


class CustomizeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=CsutomizeMessage
        fields='__all__'