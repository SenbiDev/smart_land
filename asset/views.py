from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Asset
from .serializers import AsetSerializer, AsetCreateUpdateSerializer
from authentication.permissions import IsAdminOrSuperadmin
from rest_framework.permissions import IsAuthenticated 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_aset(request):
    # Hapus select_related('landowner') karena tabel owner sudah tidak ada
    assets = Asset.objects.prefetch_related('ownerships__investor__user').all()
    serializer = AsetSerializer(assets, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperadmin]) 
@parser_classes([MultiPartParser, FormParser]) # Support Upload Gambar
def tambah_aset(request):
    serializer = AsetCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        asset_instance = serializer.save()
        # Ambil data lengkap untuk response
        asset = Asset.objects.prefetch_related('ownerships__investor__user').get(pk=asset_instance.id)
        return_serializer = AsetSerializer(asset, context={'request': request})
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin]) 
@parser_classes([MultiPartParser, FormParser]) # Support Upload Gambar saat Edit
def asset_detail(request, pk):
    try:
        asset = Asset.objects.prefetch_related('ownerships__investor__user').get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AsetSerializer(asset, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AsetCreateUpdateSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            asset.refresh_from_db()
            updated_asset = Asset.objects.prefetch_related('ownerships__investor__user').get(pk=pk)
            return_serializer = AsetSerializer(updated_asset, context={'request': request})
            return Response(return_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Hapus gambar fisik jika ada (opsional, Django biasanya tidak auto hapus file)
        if asset.image:
            asset.image.delete(save=False)
        asset.delete()
        return Response({'message': 'Asset deleted'}, status=status.HTTP_204_NO_CONTENT)