import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Role  # Pastikan Role diimport
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer # Pastikan RoleSerializer ada
from django.contrib.auth import authenticate
from django.conf import settings
from .permissions import IsSuperadmin

# --- Helper Functions ---
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
    cookie_value = json.dumps(user_data)
    response.set_cookie(
        key='user',
        value=cookie_value,
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=False,
        secure=is_production,
        samesite='Lax'
    )
    return response

# --- Auth Views ---

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        # PERBAIKAN: Ambil .name dari role
        role_name = user.role.name if user.role else None
        
        user_data = {
            'id': user.id, 
            'username': user.username, 
            'email': user.email, 
            'role': role_name 
        }
        
        response = Response({'user': user_data})
        set_auth_cookies(response, refresh)
        set_user_cookie(response, user_data)
        return response
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        role_name = user.role.name if user.role else None
        
        user_data = {
            'id': user.id, 
            'username': user.username, 
            'email': user.email, 
            'role': role_name
        }
        
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

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        refresh_token = request.data.get('refresh')

    if not refresh_token:
        return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
    try:
        token = RefreshToken(refresh_token)
        user = CustomUser.objects.get(id=token['user_id'])
        new_refresh_token = RefreshToken.for_user(user)
        
        role_name = user.role.name if user.role else None
        
        user_data = {
            'id': user.id, 
            'username': user.username, 
            'email': user.email, 
            'role': role_name
        }
        
        response = Response({
            'access': str(new_refresh_token.access_token),
            'user': user_data
        })
        set_auth_cookies(response, new_refresh_token)
        set_user_cookie(response, user_data)
        return response
    except (TokenError, CustomUser.DoesNotExist):
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

# --- Role Management (PENTING: View Baru) ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_list(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)

# --- User Management ---
@api_view(['GET', 'POST'])
@permission_classes([IsSuperadmin])
def user_list_create(request):
    if request.method == 'GET':
        users = CustomUser.objects.exclude(pk=request.user.pk).order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsSuperadmin])
def user_detail(request, pk):
    try:
        if request.user.pk == pk:
             return Response({'error': 'Cannot manage your own account.'}, status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserSerializer(user).data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            if 'password' in request.data and request.data['password']:
                updated_user.set_password(request.data['password'])
                updated_user.save()
            return Response(UserSerializer(updated_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)