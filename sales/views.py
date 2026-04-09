from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Sale
from .serializers import SaleSerializer
from authentication.permissions import HasSSOPermission 

@api_view(['GET', 'POST'])
@permission_classes([HasSSOPermission('sales')])
def list_create_sales(request):
    if request.method == 'GET':
        queryset = Sale.objects.select_related('product').all().order_by('-date')
        
        # Filter Pencarian
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(product__name__icontains=search) | queryset.filter(buyer_name__icontains=search)

        serializer = SaleSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SaleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Simpan data. 
                # Model Sale.save() akan otomatis:
                # 1. Validasi stok cukup
                # 2. Hitung total harga
                # 3. Kurangi stok produk
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                # Tangkap error validasi stok dari models.py
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([HasSSOPermission('sales')])
def sale_detail(request, pk):
    try:
        sale = Sale.objects.get(pk=pk)
    except Sale.DoesNotExist:
        return Response({'detail': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SaleSerializer(sale)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = SaleSerializer(sale, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Perhatian: Model Anda saat ini TIDAK memiliki logika pengembalian stok saat delete.
        # Jika ingin stok kembali saat delete, Anda harus menambahkannya manual di sini 
        # atau di method delete() model.
        
        # Contoh manual pengembalian stok sederhana:
        product = sale.product
        product.current_stock += sale.quantity
        product.save()
        
        sale.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)