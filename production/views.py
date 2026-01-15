from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Production, Product
from .serializers import ProductionSerializer
from authentication.permissions import IsOperatorOrAdmin 
from rest_framework.permissions import IsAuthenticated

# [TAMBAHKAN CODE INI]
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit', 'current_stock']

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_products(request):
    """Master produk untuk dropdown di form Produksi & Penjualan"""
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Buat produk baru (hanya Admin/Operator)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View yang sudah ada tetap di bawah ini...
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_production(request):
    queryset = Production.objects.select_related('asset', 'product').all()
    serializer = ProductionSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsOperatorOrAdmin])
def create_production(request):
    serializer = ProductionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOperatorOrAdmin])
def production_detail(request, pk):
    try:
        production = Production.objects.get(pk=pk)
    except Production.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductionSerializer(production)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductionSerializer(production, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        production.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)