from rest_framework import serializers
from .models import BarcodeSetting,InvoiceSetting,BannerSetting,EmailSetting
from contacts.serializers import ContactDetailsSerializer
from contacts.models import Contact
from django.db.models import Q


class BarcodeSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=BarcodeSetting
        fields='__all__'

class BarcodeSettingDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    assign_branch = serializers.SerializerMethodField()
    branch=serializers.SerializerMethodField()

    def get_created_by(self, obj):
        if obj and obj.created_by:
            return {
                "id": obj.created_by.id,
                "email": obj.created_by.email,
                "role": [role.title for role in obj.created_by.role.all()]
            }
        return None
    def get_updated_by(self, obj):
        if obj and obj.updated_by:
            return {
                "id": obj.updated_by.id,
                "email": obj.updated_by.email,
                "role": [role.title for role in obj.updated_by.role.all()]
            }
        return None

    def get_assign_branch(self, obj):
        if obj and obj.assign_branch:
            return {
                "id": obj.assign_branch.id,
                "name": obj.assign_branch.branch_name,
                "country": obj.assign_branch.country.country_name,
                "address": obj.assign_branch.address
            }
        return None
    def get_branch(self, obj):
        if obj and obj.branch:
            return {
                "id": obj.branch.id,
                "name": obj.branch.branch_name,
                "country": obj.branch.country.country_name,
                "address": obj.branch.address
            }
        return None

    class Meta:
        model = BarcodeSetting
        fields = '__all__'

class InvoiceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=InvoiceSetting
        fields='__all__'


class InvoiceSettingDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    assign_branch = serializers.SerializerMethodField()
    branch=serializers.SerializerMethodField()

    def get_created_by(self, obj):
        if obj and obj.created_by:
            return {
                "id": obj.created_by.id,
                "email": obj.created_by.email,
                "role": [role.title for role in obj.created_by.role.all()]
            }
        return None
    def get_updated_by(self, obj):
        if obj and obj.updated_by:
            return {
                "id": obj.updated_by.id,
                "email": obj.updated_by.email,
                "role": [role.title for role in obj.updated_by.role.all()]
            }
        return None

    def get_assign_branch(self, obj):
        if obj and obj.assign_branch:
            return {
                "id": obj.assign_branch.id,
                "name": obj.assign_branch.branch_name,
                "country": obj.assign_branch.country.country_name,
                "address": obj.assign_branch.address
            }
        return None
    def get_branch(self, obj):
        if obj and obj.branch:
            return {
                "id": obj.branch.id,
                "name": obj.branch.branch_name,
                "country": obj.branch.country.country_name,
                "address": obj.branch.address
            }
        return None

    class Meta:
        model=InvoiceSetting
        fields='__all__'


class BannerSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=BannerSetting
        fields='__all__'

class EmailSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=EmailSetting
        fields='__all__'

