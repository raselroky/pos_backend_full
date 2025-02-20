from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact
        fields='__all__'

class ContactDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    refer = serializers.SerializerMethodField()

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
    
    def get_refer(self, obj):
        # Get the user object from the related 'updated_by' ForeignKey
        if obj.refer:
            return {
                'id': obj.refer.id,
                'first_name': obj.refer.first_name,
                'last_name': obj.refer.last_name,
                'email': obj.refer.email,  # Add more fields as necessary
            }
        return None
    
    class Meta:
        model=Contact
        fields='__all__'