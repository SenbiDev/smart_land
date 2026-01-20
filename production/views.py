from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import traceback
from django.db import transaction # PENTING untuk atomic transaction

from .models import Production, Product
from .serializers import ProductionSerializer, ProductSerializer
from authentication.permissions import IsOperatorOrAdmin 

# ==========================================
# 1. MASTER PRODUK
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_products(request):
    try:
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
            
    except Exception as e:
        print("ERROR PRODUCT:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 2. TRANSAKSI PRODUKSI
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsOperatorOrAdmin])
def list_create_productions(request):
    try:
        if request.method == 'GET':
            queryset = Production.objects.select_related('asset', 'product').all().order_by('-date')
            
            asset_id = request.query_params.get('asset')
            search = request.query_params.get('search')
            
            if asset_id and asset_id != 'all':
                queryset = queryset.filter(asset_id=asset_id)
            if search:
                queryset = queryset.filter(product__name__icontains=search)

            serializer = ProductionSerializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # Gunakan atomic transaction agar kalau stok gagal update, produksi juga batal
            with transaction.atomic():
                serializer = ProductionSerializer(data=request.data)
                if serializer.is_valid():
                    production = serializer.save()
                    
                    # [LOGIC STOK] Tambah Stok saat Create
                    if production.status == 'stok':
                        product = production.product
                        product.current_stock += production.quantity
                        product.save()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print("CRITICAL ERROR PRODUKSI:", str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 3. DETAIL PRODUKSI
# ==========================================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsOperatorOrAdmin])
def production_detail(request, pk):
    try:
        production = Production.objects.get(pk=pk)
    except Production.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        if request.method == 'GET':
            serializer = ProductionSerializer(production)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            with transaction.atomic():
                old_qty = production.quantity
                
                partial = request.method == 'PATCH'
                serializer = ProductionSerializer(production, data=request.data, partial=partial)
                if serializer.is_valid():
                    updated_prod = serializer.save()
                    
                    # [LOGIC STOK] Update selisih
                    if updated_prod.status == 'stok':
                        product = updated_prod.product
                        diff = updated_prod.quantity - old_qty
                        product.current_stock += diff
                        product.save()

                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            with transaction.atomic():
                # [LOGIC STOK] Kurangi Stok saat Hapus
                if production.status == 'stok':
                    product = production.product
                    product.current_stock -= production.quantity
                    # Mencegah stok minus (opsional, tergantung kebijakan)
                    # if product.current_stock < 0: product.current_stock = 0 
                    product.save()
                
                production.delete()
                return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            
    except Exception as e:
        print("ERROR DETAIL:", str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)