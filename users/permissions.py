from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken,OutstandingToken
from rest_framework import exceptions

class IsLogin(IsAuthenticated):
    def has_permission(self, request, view):
        # First, check if the user is authenticated
        is_authenticated = super().has_permission(request, view)
        
        if not is_authenticated:
            return False
        
        # Check if the access token is blacklisted
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        try:
            token_type, token = auth_header.split()
            if token_type != "Bearer":
                raise exceptions.AuthenticationFailed("Authorization header must contain Bearer token")
            
            access_token = AccessToken(token)
            jti = access_token.get("jti")
            
            # Check if the token has been blacklisted
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise exceptions.AuthenticationFailed("This token has expired. Please Login again!")
        
        except ValueError:
            raise exceptions.AuthenticationFailed("Authorization header is missing or malformed.")
        
        return True
