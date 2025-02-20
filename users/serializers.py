from rest_framework import serializers
from users.models import *
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)
    role = serializers.PrimaryKeyRelatedField(queryset=Roles.objects.all(), many=True, required=False, allow_null=True)
    permissions = serializers.SerializerMethodField()
    email=serializers.CharField(required=False)
    class Meta:
        model = Users
        fields = ('id', 'email', 'first_name', 'last_name', 'photo', 'is_superadmin', 'is_active', 'age', 'password', 'permissions', 'role')

    def get_permissions(self, obj):
        data = []
        if hasattr(obj, 'account_user_permissions'):
            for account_permission in obj.account_user_permissions.all():
                permission = account_permission.permission
                item = {
                    'id': permission.id,
                    'title': permission.title,
                    'module': permission.module,
                    'sub_module': permission.sub_module
                }
                data.append(item)
        return data

class UsersUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('first_name','last_name','age','phone','gender')
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return data
    
class RolesSerializer(serializers.ModelSerializer):
    #permissions = serializers.SerializerMethodField()
    class Meta:
        model = Roles
        fields = "__all__"
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = Users.objects.filter(email=email).filter(is_active=True).first()

        if user and user.check_password(password):
            self.user = user
        else:
            raise serializers.ValidationError("Invalid email and password combination.")

        refresh = self.get_token(self.user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'lifetime': int(refresh.access_token.lifetime.total_seconds()),
            'id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'date_joined': self.user.date_joined,
        }
        return data
       
class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        return data        

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = "__all__"

class PermissionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"

class RolePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = "__all__"


class RolePermissionSerializer2(serializers.ModelSerializer):
    permission = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)

    class Meta:
        model = RolePermissions
        fields = ['id', 'role', 'permission']

    def create(self, validated_data):
        permissions = validated_data.pop('permission')  # Get permissions
        role_permissions = RolePermissions.objects.create(**validated_data)  # Create RolePermissions instance
        role_permissions.permission.set(permissions)  # Add the permissions to the instance
        role_permissions.save()
        return role_permissions

class RolePermissionSerializerModify(serializers.ModelSerializer):
    permission = PermissionSerializer2(many=True)
    role=serializers.SerializerMethodField()
    def get_role(self,obj):
        if obj.role:
            return {
                "id":obj.role.id,
                "role":obj.role.title
            }
        return None
    class Meta:
        model = RolePermissions
        fields = ['id', 'role', 'permission']


class UserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissions
        fields = "__all__"




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=False)
    new_password = serializers.CharField(required=False)