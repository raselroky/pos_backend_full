from django.contrib import admin
from .models import Notification,CsutomizeMessage

class NotificationAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
    # Make all fields clickable
    def get_list_display_links(self, request, list_display):
        return list_display 
admin.site.register(Notification,NotificationAdminColumn)


class CsutomizeMessageAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
    # Make all fields clickable
    def get_list_display_links(self, request, list_display):
        return list_display 
admin.site.register(CsutomizeMessage,CsutomizeMessageAdminColumn)