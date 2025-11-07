import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import Q # <-- PENTING: Import Q

# ---> IMPORT BARU UNTUK PERMISSION DAN LOGIKA AVAILABLE USERS <---
from .permissions import IsSuperadmin, IsAdminOrSuperadmin
from investor.models import Investor # Untuk cek user available


# --- Helper Functions (set_auth_cookies, set_user_cookie) ---
# ... (Fungsi helper ini SAMA SEPERTI SEBELUMNYA) ...
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
        httponly=False, # Must be False for JS access
        secure=is_production,
        samesite='Lax'
    )
    return response

# --- Views (login, register, logout, refresh) ---
# ... (Fungsi login_view, register_view, logout_view, refresh_view SAMA SEPERTI SEBELUMNYA) ...
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        user_data = {
            'id': user.id, 'username': user.username,
            'email': user.email, 'role': user.role
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
        user_data = {
            'id': user.id, 'username': user.username,
            'email': user.email, 'role': user.role
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
        return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        token = RefreshToken(refresh_token)
        user = CustomUser.objects.get(id=token['user_id'])
        new_refresh_token = RefreshToken.for_user(user)
        user_data = {
            'id': user.id, 'username': user.username,
            'email': user.email, 'role': user.role
        }
        response = Response({'user': user_data})
        set_auth_cookies(response, new_refresh_token)
        set_user_cookie(response, user_data)
        return response
    except TokenError as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

# --- ENDPOINT BARU UNTUK USER MANAGEMENT (Superadmin) ---

@api_view(['GET', 'POST'])
@permission_classes([IsSuperadmin]) # Hanya Superadmin
def user_list_create(request):
    if request.method == 'GET':
        # Exclude diri sendiri agar tidak bisa edit/hapus diri sendiri
        users = CustomUser.objects.exclude(pk=request.user.pk).order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Pastikan password di-hash saat create
            user.set_password(request.data.get('password'))
            user.save()
            return_serializer = UserSerializer(user) # Serializer data baru
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsSuperadmin]) # Hanya Superadmin
def user_detail(request, pk):
    try:
        # Pastikan tidak bisa edit/hapus diri sendiri
        if request.user.pk == pk:
             return Response({'error': 'Cannot manage your own account.'}, status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
         # partial=True agar tidak semua field wajib diisi saat update
        serializer = UserSerializer(user, data=request.data, partial=True) 
        if serializer.is_valid():
            updated_user = serializer.save()
            # Jika ada password baru di request, hash-kan
            if 'password' in request.data and request.data['password']:
                updated_user.set_password(request.data['password'])
                updated_user.save()
            return_serializer = UserSerializer(updated_user) # Serializer data baru
            return Response(return_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---> INI FUNGSI YANG HILANG <---
# Endpoint untuk dropdown 'Tambah Investor'
@api_view(['GET'])
@permission_classes([IsAdminOrSuperadmin]) # Admin/Superadmin boleh akses
def get_available_users_for_investor(request):
    """
    Mengembalikan daftar user yang BELUM memiliki profil Investor.
    Hanya user dengan role 'Viewer' atau 'Investor' yang relevan.
    """
    # 1. Dapatkan semua ID user yang SUDAH terdaftar di model Investor
    existing_investor_user_ids = Investor.objects.values_list('user_id', flat=True)

    # 2. Cari user (dengan role 'Viewer' atau 'Investor') 
    #    yang ID-nya TIDAK ADA di daftar 'existing_investor_user_ids'
    available_users = CustomUser.objects.filter(
        Q(role='Viewer') | Q(role='Investor')
    ).exclude(
        id__in=existing_investor_user_ids
    ).order_by('username')

    serializer = UserSerializer(available_users, many=True)
    return Response(serializer.data)