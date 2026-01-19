from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Production, Product
from .serializers import ProductionSerializer, ProductSerializer
from authentication.permissions import IsOperatorOrAdmin 

# ==========================================
# 1. MASTER PRODUK (GET & POST)
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_products(request):
    if request.method == 'GET':
        search_query = request.query_params.get('search', None)
        products = Product.objects.all().order_by('name')
        
        if search_query:
            products = products.filter(name__icontains=search_query)
            
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==========================================
# 2. TRANSAKSI PRODUKSI (GET & POST)
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsOperatorOrAdmin])
def list_create_productions(request):
    if request.method == 'GET':
        # select_related agar query join ke tabel asset dan product lebih efisien
        queryset = Production.objects.select_related('asset', 'product').all().order_by('-date')
        
        # --- FILTERING LOGIC ---
        asset_id = request.query_params.get('asset')
        search = request.query_params.get('search')
        status_param = request.query_params.get('status')

        if asset_id and asset_id != 'all':
            queryset = queryset.filter(asset_id=asset_id)
        
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)

        if search:
            queryset = queryset.filter(product__name__icontains=search)
        # -----------------------

        serializer = ProductionSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # [SOLUSI ERROR 500 & 405]
        # Menerima data JSON dari frontend (ID produk, ID asset, dll)
        serializer = ProductionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Jika data tidak valid, return error 400 (Bad Request) agar ketahuan salahnya dimana
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==========================================
# 3. DETAIL PRODUKSI (GET, PUT, PATCH, DELETE)
# ==========================================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsOperatorOrAdmin])
def production_detail(request, pk):
    try:
        production = Production.objects.get(pk=pk)
    except Production.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductionSerializer(production)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = ProductionSerializer(production, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        production.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)