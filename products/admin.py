from django.contrib import admin
from .models import Product,ProductBarcodes,ProductVariantAttribute
from django.utils.html import format_html

class ProductAdminColumn(admin.ModelAdmin):
    # def get_list_display(self, request):
    #     return [field.name for field in self.model._meta.fields]
    
    # # Make all fields clickable
    # def get_list_display_links(self, request, list_display):
    #     return list_display 

    def get_list_display(self, request):
        # Replace 'file' with 'file_display' if file is in list_display
        fields = [field.name for field in self.model._meta.fields]
        return [f if f != 'file' else 'file_display' for f in fields]

    def get_list_display_links(self, request, list_display):
        return list_display

    def file_display(self, obj):
        if obj.file and isinstance(obj.file, list):
            links = []
            for url in obj.file:
                links.append(f'<a href="{url}" target="_blank">{url.split("/")[-1]}</a>')
            return format_html("<br>".join(links))
        return "-"
    
    file_display.short_description = "Files"

admin.site.register(Product,ProductAdminColumn)

class ProductVariantAttributeAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
    # Make all fields clickable
    def get_list_display_links(self, request, list_display):
        return list_display 
admin.site.register(ProductVariantAttribute,ProductVariantAttributeAdminColumn)

class ProductBarcodesAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    
    # Make all fields clickable
    def get_list_display_links(self, request, list_display):
        return list_display 
admin.site.register(ProductBarcodes,ProductBarcodesAdminColumn)
