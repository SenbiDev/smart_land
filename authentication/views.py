import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from django.conf import settings

def set_auth_cookies(response, refresh_token):
    is_production = not settings.DEBUG
    access_token = refresh_token.access_token
    
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=is_production,
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=is_production,
        samesite='Lax'
    )
    return response

def set_user_cookie(response, user_data):
    is_production = not settings.DEBUG
    response.set_cookie(
        key='user',
        value=json.dumps(user_data),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=False, 
        secure=is_production,
        samesite='Lax'
    )
    return response

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        
        response = Response({'user': user_data})
        set_auth_cookies(response, refresh)
        set_user_cookie(response, user_data)
        return response
        
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    request_data = request.data.copy()
    if 'role' not in request_data or not request_data['role']:
        request_data['role'] = 'Viewer' 

    serializer = RegisterSerializer(data=request_data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_data = RegisterSerializer(user).data 
        
        response = Response({'user': user_data}, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, refresh)
        set_user_cookie(response, user_data)
        return response
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def logout_view(request):
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('user')
    return response