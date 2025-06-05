
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.request import Request
import jwt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
import logging
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
import os
from urllib.parse import urlparse
import re



from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
import os
import uuid
import random
import string

class ImageUploadView(APIView):
    permission_classes=(AllowAny,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        
        random_integer = random.randint(11, 9999)
        random_string = ''.join(random.choices(string.ascii_letters, k=3))

        int_char=str(random_string)+str(random_integer)
        original_filename = image.name
        safe_filename = re.sub(r'[^\w\-_.]', '_', original_filename)
        file_name = f'{uuid.uuid4().hex}{int_char}-{safe_filename}'
        with open(f'media/{file_name}', 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)

        image_url = f'{request.build_absolute_uri(settings.MEDIA_URL)}{file_name}'
        return Response({'image_url': image_url}, status=status.HTTP_200_OK)

class ImageDeleteView(APIView):
    permission_classes = (AllowAny,)

    def delete(self, request, *args, **kwargs):
        image_url = request.data.get('image_url')

        if not image_url:
            return Response({'error': 'No image URL provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed_url = urlparse(image_url)
            image_name = os.path.basename(parsed_url.path)
        except Exception as e:
            return Response({'error': 'Invalid image URL'}, status=status.HTTP_400_BAD_REQUEST)

        image_path = os.path.join(settings.MEDIA_ROOT, image_name)
        #print(image_path,image_name)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                return Response({'message': f'Image {image_name} deleted successfully.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Error deleting file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

