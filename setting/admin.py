from django.contrib import admin
from .models import BarcodeSetting,InvoiceSetting,BannerSetting,GeneralSetting
from django.utils.html import format_html

class BarcodeSettingAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Replace 'file' with 'file_display' if file is in list_display
        fields = [field.name for field in self.model._meta.fields]
        return [f if f != 'barcode_logo' else 'barcode_logo_display' for f in fields]

    def get_list_display_links(self, request, list_display):
        return list_display

    def barcode_logo_display(self, obj):
        if obj.barcode_logo and isinstance(obj.barcode_logo, list):
            links = []
            for url in obj.barcode_logo:
                links.append(f'<a href="{url}" target="_blank">{url.split("/")[-1]}</a>')
            return format_html("<br>".join(links))
        return "-"
    
    barcode_logo_display.short_description = "Files"
admin.site.register(BarcodeSetting, BarcodeSettingAdmin)


class InvoiceSettingAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Replace 'file' with 'file_display' if file is in list_display
        fields = [field.name for field in self.model._meta.fields]
        return [f if f != 'invoice_logo' else 'invoice_logo_display' for f in fields]

    def get_list_display_links(self, request, list_display):
        return list_display

    def invoice_logo_display(self, obj):
        if obj.invoice_logo and isinstance(obj.invoice_logo, list):
            links = []
            for url in obj.invoice_logo:
                links.append(f'<a href="{url}" target="_blank">{url.split("/")[-1]}</a>')
            return format_html("<br>".join(links))
        return "-"
    
    invoice_logo_display.short_description = "Files"
admin.site.register(InvoiceSetting, InvoiceSettingAdmin)


class BannerSettingAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        # Replace 'file' with 'file_display' if file is in list_display
        fields = [field.name for field in self.model._meta.fields]
        return [f if f != 'banner_image' else 'banner_image_display' for f in fields]

    def get_list_display_links(self, request, list_display):
        return list_display

    def banner_image_display(self, obj):
        if obj.banner_image and isinstance(obj.banner_image, list):
            links = []
            for url in obj.banner_image:
                links.append(f'<a href="{url}" target="_blank">{url.split("/")[-1]}</a>')
            return format_html("<br>".join(links))
        return "-"
    
    banner_image_display.short_description = "Files"
admin.site.register(BannerSetting, BannerSettingAdminColumn)


class GeneralSettingAdminColumn(admin.ModelAdmin):
    def get_list_display(self, request):
        # Show other fields normally, but replace company_logo and favicon_icon
        fields = [field.name for field in self.model._meta.fields]
        return [f if f not in ['company_logo', 'favicon_icon'] 
                else f + '_display' for f in fields]

    def get_list_display_links(self, request, list_display):
        return list_display

    def company_logo_display(self, obj):
        return self.render_files(obj.company_logo)

    def favicon_icon_display(self, obj):
        return self.render_files(obj.favicon_icon)

    def render_files(self, file_data):
        if file_data and isinstance(file_data, list):
            links = []
            for item in file_data:
                if isinstance(item, dict):
                    url = item.get("url") or ""
                    filename = item.get("name") or url.split("/")[-1]
                elif isinstance(item, str):
                    url = item
                    filename = url.split("/")[-1]
                else:
                    continue
                if url:
                    links.append(f'<a href="{url}" target="_blank">{filename}</a>')
            return format_html("<br>".join(links))
        return "-"

    company_logo_display.short_description = "Company Logo"
    favicon_icon_display.short_description = "Favicon Icon"

admin.site.register(GeneralSetting, GeneralSettingAdminColumn)