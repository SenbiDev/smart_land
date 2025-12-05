from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from authentication.permissions import IsAdminOrSuperadmin
from django.db.models import Sum, F, DecimalField, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
from decimal import Decimal 
from .models import Funding
from expense.models import Expense 
from project.models import Project
from .serializers import FundingCreateUpdateSerializer, FundingDetailSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) 
def funding_list(request):
    
    if request.method == 'GET':
        queryset = Funding.objects.select_related('source', 'project').all()
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
@permission_classes([IsAdminOrSuperadmin])
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

    if request.method == 'GET':
        serializer = FundingDetailSerializer(funding_instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FundingCreateUpdateSerializer(funding_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        funding_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)