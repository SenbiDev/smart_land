from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
# Menambahkan IsOperatorOrAdmin agar operator bisa GET data untuk dropdown expense
from authentication.permissions import IsAdminOrSuperadmin, IsViewerOrInvestorReadOnly, IsOperatorOrAdmin
from django.db.models import Sum, F, DecimalField, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
from decimal import Decimal 
from .models import Funding
from .serializers import FundingCreateUpdateSerializer, FundingDetailSerializer

@api_view(['GET', 'POST'])
# Update Permission: Tambahkan IsOperatorOrAdmin
@permission_classes([IsAdminOrSuperadmin | IsViewerOrInvestorReadOnly | IsOperatorOrAdmin]) 
def funding_list(request):
    
    if request.method == 'GET':
        queryset = Funding.objects.select_related('source', 'project').all()
        
        # Data Scoping: Investor hanya melihat funding di aset miliknya
        if request.user.role and request.user.role.name == 'Investor':
            queryset = queryset.filter(project__asset__ownerships__investor__user=request.user).distinct()
        
        # Note: Operator akan melihat .all() (semua dana) agar bisa memilih sumber dana manapun 
        # saat input pengeluaran.

        asset_id = request.query_params.get('asset_id')
        if asset_id and asset_id != 'all':
            try:
                queryset = queryset.filter(project__asset_id=int(asset_id))
            except (ValueError, TypeError):
                pass

        queryset = queryset.annotate(
            total_terpakai=Coalesce(
                Sum('expenses__amount'), 
                Decimal('0.0'), 
                output_field=DecimalField()
            )
        ).annotate(
            sisa_dana=F('amount') - F('total_terpakai'),
            persen_terpakai=Case(
                When(amount=Decimal('0.0'), then=Value(0.0)), 
                default=(F('total_terpakai') * 100.0 / F('amount')),
                output_field=FloatField()
            )
        )

        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by('-date_received')
        serializer = FundingDetailSerializer(queryset, many=True)

        return Response(serializer.data)

    if request.method == 'POST':
        # Manual Check: Meskipun Operator lolos permission class di atas,
        # kode ini akan MENOLAK Operator untuk melakukan POST (Tambah Dana).
        is_allowed = request.user.is_superuser or (
            request.user.role and request.user.role.name in ['Admin', 'Superadmin']
        )

        if not is_allowed:
             return Response({'error': 'Hanya Admin yang dapat menambah data.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = FundingCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
# Update Permission: Tambahkan IsOperatorOrAdmin
@permission_classes([IsAdminOrSuperadmin | IsViewerOrInvestorReadOnly | IsOperatorOrAdmin])
def funding_detail(request, pk):
    try:
        queryset = Funding.objects.select_related('source', 'project')
        queryset = queryset.annotate(
            total_terpakai=Coalesce(
                Sum('expenses__amount'), 
                Decimal('0.0'), 
                output_field=DecimalField()
            )
        ).annotate(
            sisa_dana=F('amount') - F('total_terpakai'),
            persen_terpakai=Case(
                When(amount=Decimal('0.0'), then=Value(0.0)), 
                default=(F('total_terpakai') * 100.0 / F('amount')),
                output_field=FloatField()
            )
        )
        
        funding_instance = queryset.get(pk=pk)

    except Funding.DoesNotExist:
        return Response({'error': 'funding not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Cek akses read detail funding untuk investor
    if request.user.role and request.user.role.name == 'Investor':
        has_access = False
        if funding_instance.project and funding_instance.project.asset:
            has_access = funding_instance.project.asset.ownerships.filter(investor__user=request.user).exists()
        
        if not has_access:
             return Response({'error': 'Anda tidak memiliki akses ke data pendanaan ini.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = FundingDetailSerializer(funding_instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Manual Check: Pastikan hanya Admin/Superadmin yang bisa Edit
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = FundingCreateUpdateSerializer(funding_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
         # Manual Check: Pastikan hanya Admin/Superadmin yang bisa Hapus
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        funding_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)