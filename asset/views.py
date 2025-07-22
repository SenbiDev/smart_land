from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import KategoriAset, Asset, Pemilik
from .serializers import KategoriAsetSerializer, AsetSerializer, PemilikSerializer

# Create your views here.

@api_view(['GET'])
def list_kategori(request):
    kategori = KategoriAset.objects.all()
    serializer = KategoriAsetSerializer(kategori, many=True)
    return Response(serializer.date)

@api_view(['POST'])
def tambah_kategori(request):
    serializers = KategoriAsetSerializer(data=request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data)
    return Response(serializers.errors)

@api_view(['GET'])
def list_aset(request):
    aset = Asset.objects.all()
    serializer = AsetSerializer(aset, many=True)
    return Response(serializer.date) 

@api_view(['POST'])
def tambah_aset(request):
    serializer = AsetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def asset_detail(request, pk):
    try:
        asset = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'})
    
    if request.method == 'GET':
        serializer = AsetSerializer(asset)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AsetSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset.delete()
        return Response({'message': 'Asset deleted'}, status=status.HTTP_204_NO_CONTENT)
        
@api_view(['GET'])
def list_pemilik(request):
    pemilik = Pemilik.objects.all()
    serializer = PemilikSerializer(pemilik, many=True)
    return Response(serializer.date)

@api_view(['POST'])
def tambah_pemilik(request):
    serializer = PemilikSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors) 
