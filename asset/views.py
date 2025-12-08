# File: senbidev/smart_land/smart_land-faiz/asset/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Asset, Owner
from .serializers import AsetSerializer, AsetCreateUpdateSerializer, OwnerSerializer
from authentication.permissions import IsAdminOrSuperadmin
from rest_framework.permissions import IsAuthenticated 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_aset(request):
    assets = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').all()
    
    # --- REFACTOR START: Data Scoping ---
    if request.user.role and request.user.role.name == 'Investor':
        # Investor hanya melihat aset yang dia miliki sahamnya
        assets = assets.filter(ownerships__investor__user=request.user).distinct()
    # --- REFACTOR END ---

    serializer = AsetSerializer(assets, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperadmin]) 
def tambah_aset(request):
    serializer = AsetCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        asset_instance = serializer.save()
        asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=asset_instance.id)
        return_serializer = AsetSerializer(asset)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin]) # Detail edit/delete hanya admin
def asset_detail(request, pk):
    try:
        asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Note: Karena permission class adalah IsAdminOrSuperadmin, Investor tidak akan bisa akses endpoint ini.
    # Jika Investor butuh lihat detail aset (read-only), permission harus diganti ke [IsAuthenticated]
    # dan logic pengecekan role ditambahkan manual seperti di bawah.
    # Namun sesuai kode awal, endpoint ini khusus admin. 
    # List aset (list_aset) di atas sudah cukup untuk view investor di tabel.

    if request.method == 'GET':
        serializer = AsetSerializer(asset)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AsetCreateUpdateSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            asset.refresh_from_db()
            updated_asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=pk)
            return_serializer = AsetSerializer(updated_asset)
            return Response(return_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset.delete()
        return Response({'message': 'Asset deleted'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAdminOrSuperadmin])
def list_owner(request):
    owners = Owner.objects.prefetch_related('assets').all()
    serializer = OwnerSerializer(owners, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperadmin])
def tambah_owner(request):
    serializer = OwnerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin])
def owner_detail(request, pk):
    try:
        owner = Owner.objects.prefetch_related('assets').get(pk=pk)
    except Owner.DoesNotExist:
        return Response({'error': 'Owner not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OwnerSerializer(owner)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OwnerSerializer(owner, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        owner.delete()
        return Response({'message': 'Owner deleted'}, status=status.HTTP_204_NO_CONTENT)    