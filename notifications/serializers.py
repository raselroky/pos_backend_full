
from rest_framework import serializers
from .models import Notification,CsutomizeMessage
import re


class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    unique_field=serializers.SerializerMethodField()

    def get_unique_field(self, obj):
        title=obj.title
        if title=='product variant':
            msg=obj.message
            msg_split=msg.split('-')
            #print(msg_split[0]+'-'+msg_split[1]+'-'+msg_split[2])
            
            return str(msg_split[0])
        elif title=='stock adjustment' or title=='stock transfer' or title=='stock':
            msg = obj.message.strip()
            
            final_text = msg.split("(")[0].strip()

            return final_text
        elif title=='sale' or title=='sale return' or title=='purchase' or title=='purchase return':
            msg=obj.message
            msg_split=msg.split(' ')
            return msg_split[0]
        
        return None

    def get_unread_count(self, obj):
        unread_count = Notification.objects.filter(is_read=False, recipient=self.context['request'].user).count()
        return unread_count

    def get_read_count(self, obj):
        read_count = Notification.objects.filter(is_read=True, recipient=self.context['request'].user).count()
        return read_count

    def get_sender(self, obj):
        sender = obj.sender
        #print(sender)
        if sender:
            return {
                "sender_username": sender.email,
                "sender_branch":sender.branch.branch_name if sender.branch else "No Branch",
                "sender_role":[role.title for role in sender.role.all()] 
               
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