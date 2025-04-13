from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import Users
from users.serializers import *
from users.permissions import IsLogin
from helper import MainPagination
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from rest_framework.decorators import action
import os
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken,TokenError
import datetime
from django.utils.timezone import make_aware
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import Permission
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from branch.models import Branch
from django.http import QueryDict


class LoginAPIView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
class LogoutView(APIView):
  permission_classes = [IsLogin]

  def post(self, request):
      
          refresh_token = request.data.get("refresh_token")
          access_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

          if refresh_token:
            try:
              token = RefreshToken(refresh_token)
              token.blacklist()
            except Exception as e:print("Refresh Token Blacklist: ",e)
          if access_token:  
            access_token_obj = AccessToken(access_token)
            
            naive_datetime = datetime.fromtimestamp(access_token_obj['exp'])

            expires_at = make_aware(naive_datetime)
            print('access_token_obj exp',type(access_token_obj['exp']),access_token_obj['exp'])
              
            OutstandingToken.objects.create(
                user_id=request.user.id,
                jti=access_token_obj['jti'],
                token=str(access_token),
                expires_at=expires_at
            )
            outstanding_token = OutstandingToken.objects.get(jti=access_token_obj['jti'])
            BlacklistedToken.objects.create(token=outstanding_token)

            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            for token in tokens:
              print('tokens',token)
              print('tokens',token.user_id)
              BlacklistedToken.objects.get_or_create(token=token)
            
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
          else:
              return Response(
                  {"error": "Both tokens are required"},
                  status=status.HTTP_400_BAD_REQUEST
              )
              
      # except Exception as e:
      #     return Response(
      #         {"error": str(e)},
      #         status=status.HTTP_400_BAD_REQUEST
      #     )

class TokenRefreshAPIView(TokenRefreshView):
    serializer_class = TokenRefreshLifetimeSerializer


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]
    pagination_class = MainPagination
    queryset = Users.objects.all()


    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)
        if Users.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists!"}, status=status.HTTP_400_BAD_REQUEST)
        
        mutable_data = request.data.copy() if isinstance(request.data, QueryDict) else request.data

        role_ids = request.data.getlist("role") if isinstance(request.data, QueryDict) else request.data.get("role", [])
        role_ids = [int(role_id) for role_id in role_ids if str(role_id).isdigit()]

        branch_id = request.data.get("branch", None)

        gender = request.data.get("gender", "Please Select")
        mutable_data["gender"] = gender

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        user_instance = serializer.save()

        if role_ids:
            valid_roles = Roles.objects.filter(id__in=role_ids)
            user_instance.role.set(valid_roles)

        if branch_id:
            try:
                branch_instance = Branch.objects.get(id=int(branch_id))
                user_instance.branch = branch_instance
            except (Branch.DoesNotExist, ValueError):
                return Response({"error": "Invalid branch ID!"}, status=status.HTTP_400_BAD_REQUEST)

        if "photo" in request.FILES:
            user_instance.photo = request.FILES["photo"]

        user_instance.save()

        return Response(UsersSerializer(user_instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        allowed_fields = {'first_name', 'last_name', 'age', 'role','photo','is_superadmin','is_active'}
        filtered_data = {field: value for field, value in request.data.items() if field in allowed_fields}

        serializer = self.get_serializer(instance, data=filtered_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-profile")
    def my_profile(self, request, *args, **kwargs):
        serializer = UsersSerializer(request.user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["put"], url_path="update-my-profile")
    def update_my_profile(self, request, *args, **kwargs):
        serializer = UsersUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"], url_path="my-permissions")
    def my_permissions(self, request, *args, **kwargs):
        serializer = UsersSerializer(request.user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["put"], url_path="change-password")
    def change_password(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({"error": "New password is required!"}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class RolesViewSet(viewsets.ModelViewSet):
    serializer_class = RolesSerializer
    permission_classes = [IsLogin]
    pagination_class = MainPagination
    queryset = Roles.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RolesRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = RolesSerializer
    permission_classes = [IsLogin]
    pagination_class = MainPagination
    queryset = Roles.objects.all()
    lookup_field='id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
class PasswordResetViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordResetSerializer

    @action(detail=False, methods=["post"], url_path="request")
    def password_reset_request(self, request, *args, **kwargs):
      email = request.data.get('email')
      if not email:
          return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)
      user = Users.objects.filter(email=email).first()
      if not user:
          return Response({"error": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)
      token_generator = PasswordResetTokenGenerator()
      token = token_generator.make_token(user)
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = f"{uid}:{token}"
      reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
      email_subject = f"Reset Password"
      email_body = f"""
      <html>
          <body>
                <h2>Reset Password</h2>
              <p>Click the button below to reset your password:</p>
              <a href="{reset_link}" style="
                  display: inline-block;
                  background-color: #4CAF50;
                  color: white;
                  text-decoration: none;
                  padding: 10px 20px;
                  font-size: 16px;
                  border-radius: 5px;
              ">
                Reset Password
              </a>
              <p>If your link expires, please retry again.</p>
          </body>
      </html>
      """

      # Send the email
      email_message = EmailMessage(
          email_subject, email_body, to=[email]
      )
      email_message.content_subtype = "html"  # Specify the email format as HTML
      email_message.send()

      return Response({'message': 'password reset link sent.','link':reset_link}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        token = request.data.get("token")
        password = request.data.get("new_password")
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        if ":" not in token:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id, actual_token = token.split(':', 1)
        user_id = force_str(urlsafe_base64_decode(user_id))
        user = Users.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, actual_token):
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return Users.objects.none()
    



###########


class PermissionListAPIView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer2
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'codename']
    pagination_class = None

    def get_queryset(self):
        role_id = self.request.query_params.get('role_id')
        if role_id:
            return Permission.objects.filter(roles__id=role_id)
        return super().get_queryset()

class RolePermissionsListCreateView(ListCreateAPIView):
    queryset = RolePermissions.objects.all()
    serializer_class = RolePermissionSerializer2
    permission_classes = [IsAuthenticated]  # You can add custom permission classes if needed


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RolePermissionsListAPIView(ListAPIView):
    queryset = RolePermissions.objects.all()
    serializer_class = RolePermissionSerializerModify
    permission_classes = [IsAuthenticated]  # You can add custom permission classes if needed
    pagination_class=MainPagination


class RolePermissionsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = RolePermissions.objects.all()
    serializer_class = RolePermissionSerializer2
    permission_classes = [IsAuthenticated]
    lookup_field='id'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)




class PermissionsViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionsSerializer
    permission_classes = [IsLogin]
    pagination_class = MainPagination
    queryset = Permissions.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='assign-role-permission')
    def assign_role_permission(self, request):
        obj = request.data
        data = {}
        data['created_by'] = request.user.id
        permission_list = obj.get('permissions',[])
        role = obj.get('role',None)
        if not role:
            return Response({"error": "Role is required!"}, status=status.HTTP_400_BAD_REQUEST)
        check_role = Roles.objects.filter(id=role).first()
        if not check_role:
            return Response({"error": "Role not exists!"}, status=status.HTTP_400_BAD_REQUEST)
        if not permission_list:
            return Response({"error": "Permission is required!"}, status=status.HTTP_400_BAD_REQUEST)
        RolePermissions.objects.filter(role=role).delete()
        for permission in permission_list:
            data['role'] = role
            data['permission'] = permission
            serializer = RolePermissionsSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                break
        serializer = RolesSerializer(check_role)
        return Response({"message": "Permission assigned successfully.","data":serializer.data}, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['post'], url_path='assign-user-permission')
    def assign_user_permission(self, request):
        obj = request.data
        data = {}
        data['created_by'] = request.user.id
        permission_list = obj.get('permissions',[])
        user = obj.get('user',None)
        if not user:
            return Response({"error": "User is required!"}, status=status.HTTP_400_BAD_REQUEST)
        check_user = Users.objects.filter(id=user).first()
        if not check_user:
            return Response({"error": "User not exists!"}, status=status.HTTP_400_BAD_REQUEST)
        if not permission_list:
            return Response({"error": "Permission is required!"}, status=status.HTTP_400_BAD_REQUEST)
        UserPermissions.objects.filter(user=user).delete()
        for permission in permission_list:
            data['user'] = user
            data['permission'] = permission
            serializer = UserPermissionsSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                break
        serializer = UsersSerializer(check_user)
        return Response({"message": "Permission assigned successfully.","data":serializer.data}, status=status.HTTP_201_CREATED)
        


class ForgetPassword(APIView):
    permission_classes=(AllowAny,)

    
    def post(self,request):
        email=request.data['email']
        
        usr=Users.objects.filter(email=email)
        if usr.exists():
            phone=request.data['phone']
            usr1=Users.objects.filter(email=email,phone=phone)
            if usr1.exists():
                usr2=Users.objects.filter(email=email,phone=phone).first()
                new_password=request.data['new_password']

                usr2.password=new_password
                usr2.save()
                return Response({"message":"Successfully set new Passowrd."},status=status.HTTP_200_OK)
            return Response({"message":"Phone number not correct,try again."},status=status.HTTP_404_NOT_FOUND)
        return Response({"message":"user doesn't exist,try again."},status=status.HTTP_404_NOT_FOUND)




class RolePermissionsSearchCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        id = request.data.get('id') 
        if not id:
            return Response({"error": "ID is required."}, status=400)

        checker = RolePermissions.objects.filter(role__id=id).first()
        if not checker:
            created_by_user = self.request.user
            checker = RolePermissions.objects.create(role_id=id,created_by=created_by_user)

        serializer = RolePermissionSerializerModify(checker)
        return Response(serializer.data, status=200)
        
        

class UserGetRetrieve(RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Users.objects.all()
    serializer_class=UsersSerializer
    lookup_field='id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if 'photo' in request.FILES:
            data['photo'] = request.FILES['photo']
        elif 'photo' in data and data['photo'] in ["null", "", None]:  
            instance.photo.delete(save=False)  
            data.pop('photo')
        
        serializer = self.get_serializer(instance, data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        user=self.request.user
        return Users.objects.all()


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    
    
class PasswordChange(APIView):
    permission_classes=(IsAuthenticated,)

    def post(self, request):
        user = self.request.user 

        usr=Users.objects.filter(id=user.id).first()
        old_password=request.data['old_password']
        new_password=request.data['new_password']
        confirm_password=request.data['confirm_password']
        #print(old_password,usr.password)
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password!=confirm_password:
            return Response({"error": "Two Password is didnt matched."}, status=status.HTTP_400_BAD_REQUEST)


        usr.set_password(new_password)
        usr.save()

    

        return Response({"message":"Successfully set new Passowrd."},status=status.HTTP_200_OK)



class UserListAPIView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=Users.objects.all()
    serializer_class=UsersSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','email','first_name','last_name','age','phone','gender']
    pagination_class=MainPagination
    
    def get_queryset(self):
        return Users.objects.all()