import jwt
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from users.models import Users

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract the token from the query string
        token = self.get_token_from_scope(scope)
        
        # Authenticate user based on the token
        scope['user'] = await self.authenticate_user(token) 
        return await self.inner(scope, receive, send)

    def get_token_from_scope(self, scope):
        # Example: Extract token from query string
        query_string = scope['query_string'].decode('utf-8')
        if 'token=' in query_string:
            return query_string.split('token=')[-1]
        return None

    @database_sync_to_async
    def authenticate_user(self, token):
        if token is None:
            return AnonymousUser()

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Users.objects.get(username=payload['username'])
            return user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, Users.DoesNotExist):
            return AnonymousUser()
