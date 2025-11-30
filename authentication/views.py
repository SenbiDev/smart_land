import json
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import Q
from .models import CustomUser, Role
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer
from .permissions import IsSuperadmin, IsAdminOrSuperadmin
from investor.models import Investor

# --- Helper: User Data Dict ---
def get_user_data_dict(user):
    role_data = None
    if user.is_superuser:
        role_data = {"id": 999, "name": "Superadmin"}
    elif user.role:
        role_data = {"id": user.role.id, "name": user.role.name}
    else:
        role_data = {"id": 0, "name": "Viewer"}
    
    profile_data = None
    if hasattr(user, 'profile'):
        profile_data = {
            "phone": user.profile.phone,
            "address": user.profile.address,
            "website": user.profile.website
        }
    
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': role_data,
        'profile': profile_data
    }

# --- Custom Login ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = get_user_data_dict(self.user)
        data.update({'user': user_data})
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# --- Auth Helper Cookies ---
def set_auth_cookies(response, refresh_token):
    is_production = not settings.DEBUG
    response.set_cookie(
        key='access_token',
        value=str(refresh_token.access_token),
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

def set_user_cookie(response, user_data):
    response.set_cookie(
        key='user',
        value=json.dumps(user_data),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=False,
        secure=not settings.DEBUG,
        samesite='Lax'
    )

# --- Views ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        user_data = get_user_data_dict(user)
        
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
        user_data = get_user_data_dict(user)

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
        new_refresh = RefreshToken.for_user(user)
        user_data = get_user_data_dict(user)
        
        response = Response({'user': user_data})
        set_auth_cookies(response, new_refresh)
        set_user_cookie(response, user_data)
        return response
    except:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

# --- User Management ---
@api_view(['GET', 'POST'])
@permission_classes([IsSuperadmin])
def user_list_create(request):
    if request.method == 'GET':
        users = CustomUser.objects.all().select_related('role', 'profile').order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsSuperadmin])
def user_detail(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- Role Management (Untuk Dropdown) ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_list(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminOrSuperadmin])
def get_available_users_for_investor(request):
    existing = Investor.objects.values_list('user_id', flat=True)
    # Cari user yg role-nya Investor atau Viewer, dan belum ada di tabel Investor
    users = CustomUser.objects.filter(
        Q(role__name='Investor') | Q(role__name='Viewer')
    ).exclude(id__in=existing)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)