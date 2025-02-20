from rest_framework import serializers
from .models import Country,Branch

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model=Country
        fields='__all__'

class CountryDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        # Get the user object from the related 'created_by' ForeignKey
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'first_name': obj.created_by.first_name,
                'last_name': obj.created_by.last_name,
                'email': obj.created_by.email,  # Add more fields as necessary
            }
        return None  # Return None if no user is associated

    def get_updated_by(self, obj):
        # Get the user object from the related 'updated_by' ForeignKey
        if obj.updated_by:
            return {
                'id': obj.updated_by.id,
                'first_name': obj.updated_by.first_name,
                'last_name': obj.updated_by.last_name,
                'email': obj.updated_by.email,  # Add more fields as necessary
            }
        return None
    
    class Meta:
        model=Country
        fields='__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Branch
        fields='__all__'

class BranchDetailsSerializer(serializers.ModelSerializer):
    country=serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        # Get the user object from the related 'created_by' ForeignKey
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'first_name': obj.created_by.first_name,
                'last_name': obj.created_by.last_name,
                'email': obj.created_by.email,  # Add more fields as necessary
            }
        return None  # Return None if no user is associated

    def get_updated_by(self, obj):
        # Get the user object from the related 'updated_by' ForeignKey
        if obj.updated_by:
            return {
                'id': obj.updated_by.id,
                'first_name': obj.updated_by.first_name,
                'last_name': obj.updated_by.last_name,
                'email': obj.updated_by.email,  # Add more fields as necessary
            }
        return None
    def get_country(self,obj):
        if obj.country:
            return {
                'id': obj.country.id,
                'country_name': obj.country.country_name,
                'country_code': obj.country.country_code,
                'country_short_name': obj.country.country_short_name,  # Add more fields as necessary
            }
        return None
    class Meta:
        model=Branch
        fields='__all__'