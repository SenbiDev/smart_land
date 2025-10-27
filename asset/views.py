# File: senbidev/smart_land/smart_land-faiz/asset/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
# Corrected import for Asset and Owner
from .models import Asset, Owner
# Corrected import for Project (from the 'project' app)
# from .models import Project # <<< REMOVE THIS LINE
# Add the correct import below
# from project.models import Project # No need to import Project here anymore, it was likely a leftover mistake.
from .serializers import AsetSerializer, AsetCreateUpdateSerializer, OwnerSerializer
from authentication.permissions import IsAdminOrSuperadmin # Impor izin

@api_view(['GET'])
@permission_classes([IsAdminOrSuperadmin]) # GANTI INI
def list_aset(request):
    assets = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').all()
    serializer = AsetSerializer(assets, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperadmin]) # GANTI INI
def tambah_aset(request):
    serializer = AsetCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        # Correctly save the instance first to get an ID
        asset_instance = serializer.save()
        # Fetch the full instance with related data for the response serializer
        # Note: 'id' might not be directly in serializer.data if it's read-only
        asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=asset_instance.id)
        return_serializer = AsetSerializer(asset)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin]) # GANTI INI
def asset_detail(request, pk):
    try:
        asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AsetSerializer(asset)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AsetCreateUpdateSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return dengan serializer lengkap
            asset.refresh_from_db() # Refresh instance after save
            # Re-fetch with related data might be safer depending on serializer setup
            updated_asset = Asset.objects.select_related('landowner').prefetch_related('ownerships__investor__user').get(pk=pk)
            return_serializer = AsetSerializer(updated_asset)
            return Response(return_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset.delete()
        return Response({'message': 'Asset deleted'}, status=status.HTTP_204_NO_CONTENT)

# ========== OWNER ENDPOINTS ==========

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