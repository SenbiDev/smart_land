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

# Helper function to set HttpOnly auth cookies
def set_auth_cookies(response, refresh_token):
    is_production = not settings.DEBUG
    access_token = refresh_token.access_token
    
    print(f"🍪 Setting cookies - is_production: {is_production}")  # Debug
    
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
    
    print(f"✅ Cookies set: access_token={str(access_token)[:20]}...")  # Debug
    return response

# Helper function to set the user data cookie (accessible by JS)
def set_user_cookie(response, user_data):
    is_production = not settings.DEBUG
    # Ensure the value is a valid JSON string
    cookie_value = json.dumps(user_data) 
    
    # Debug print to verify JSON format (optional)
    # print(f"DEBUG: Setting user cookie with value: {cookie_value}")

    response.set_cookie(
        key='user',
        value=cookie_value,
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=False, # Must be False for JS access
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
        # Manually create user_data dict for consistency
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
        
    # Use 401 Unauthorized for invalid credentials
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    request_data = request.data.copy()
    # Ensure default role if not provided
    if 'role' not in request_data or not request_data['role']:
        request_data['role'] = 'Viewer' 

    serializer = RegisterSerializer(data=request_data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        # Manually create user_data dict for consistency with login_view
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        
        response = Response({'user': user_data}, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, refresh)
        set_user_cookie(response, user_data)
        return response
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny]) # Allow any user to attempt logout
def logout_view(request):
    response = Response(status=status.HTTP_204_NO_CONTENT)
    # Delete all relevant cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('user')
    return response