from django.urls import path, include
from users.views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('api/user', UsersViewSet)
router.register('api/role', RolesViewSet)
router.register('api/permission', PermissionsViewSet)
router.register('api/password-reset', PasswordResetViewSet, basename="password-reset")

urlpatterns = [
    #API
    path('', include(router.urls)),
    path('api/userget/<str:id>', UserGetRetrieve.as_view(), name="user-get"),
    path('api/user-list/', UserListAPIView.as_view(), name="user-list"),
    path('api/passwordchange/', PasswordChange.as_view(), name="password_change"),
    path('api/login/', LoginAPIView.as_view(), name="api_login"),
    path('api/refresh/token/', TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/permission-list/', PermissionListAPIView.as_view(), name='permission-list-api'),

    path('api/role-permissions/', RolePermissionsListCreateView.as_view(), name='role-permissions-list-create'),
    path('api/role-permissions-list/', RolePermissionsListAPIView.as_view(), name='role-permissions-list-create'),
    path('api/role-permissions/<int:id>', RolePermissionsRetrieveUpdateDestroyView.as_view(), name='role-permissions-detail'),
    path('api/role-permissions-check/', RolePermissionsSearchCheckAPIView.as_view(), name='role-permissions-check-api'),

    path('api/role-update-destroy/<int:id>', RolesRetrieveUpdateDestroy.as_view(), name='role-update-destroy-detail'),

    


]
