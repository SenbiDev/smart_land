from decimal import Decimal
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Production
from .serializers import ProductionCreateUpdateSerializer, ProductionDetailSerializer
from asset.models import Asset
from ownership.models import Ownership
from investor.models import Investor
from profit_distribution.models import ProfitDistribution
from distribution_detail.models import DistributionDetail
from authentication.permissions import IsAdminOrSuperadmin, IsOperatorOrAdmin

@api_view(['GET', 'POST'])
@permission_classes([IsOperatorOrAdmin])
def production_list(request):
    
    if request.method == 'GET':
        queryset = Production.objects.select_related('asset').all().order_by('-date')
        
        asset_id = request.query_params.get('asset')
        if asset_id and asset_id != 'all':
            queryset = queryset.filter(asset_id=asset_id)
            
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        type_filter = request.query_params.get('type')
        if type_filter and type_filter != 'all':
            queryset = queryset.filter(asset__type=type_filter)
            
        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
            
        serializer = ProductionDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductionCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            unit_price = serializer.validated_data['unit_price']
            total_value = Decimal(str(quantity)) * unit_price

            production = serializer.save(total_value=total_value)
            
            asset = production.asset
            net_profit = total_value

            owner_share_percent_decimal = asset.landowner_share_percentage / Decimal("100.0")
            owner_share = net_profit * owner_share_percent_decimal
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1  

            distribution, created = ProfitDistribution.objects.update_or_create(
                production=production,
                defaults={
                    'period': str(production.date),
                    'net_profit': net_profit,
                    'landowner_share': owner_share,
                    'investor_share': investor_share_total,
                    'distribution_date': timezone.now().date()
                }
            )

            if not created:
                distribution.details.all().delete()

            for o in ownerships:
                percent = o.units / total_units
                share = investor_share_total * Decimal(str(percent))
                DistributionDetail.objects.create(
                    distribution=distribution,
                    investor=o.investor,
                    ownership_percentage=round(percent * 100, 2),
                    amount_received=share
                )
            
            return_data = ProductionDetailSerializer(production).data
            return Response(return_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsOperatorOrAdmin])
def production_detail(request, pk):
    production = get_object_or_404(Production, pk=pk)

    if request.method == 'GET':
        serializer = ProductionDetailSerializer(production)
        return Response(serializer.data)
    
    is_admin = request.user.is_superuser or (
        request.user.role and request.user.role.name in ['Admin', 'Superadmin']
    )

    if request.method in ['PUT', 'PATCH']:
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat mengubah data.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        
        quantity = float(data.get('quantity', production.quantity))
        unit_price = Decimal(data.get('unit_price', production.unit_price))
        total_value = Decimal(str(quantity)) * unit_price

        serializer = ProductionCreateUpdateSerializer(production, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            production = serializer.save(total_value=total_value)
            
            asset = production.asset
            net_profit = total_value

            owner_share_percent_decimal = asset.landowner_share_percentage / Decimal("100.0")
            owner_share = net_profit * owner_share_percent_decimal
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1

            distribution, created = ProfitDistribution.objects.update_or_create(
                production=production,
                defaults={
                    'period': str(production.date),
                    'net_profit': net_profit,
                    'landowner_share': owner_share,
                    'investor_share': investor_share_total,
                    'distribution_date': timezone.now().date()
                }
            )

            if not created:
                distribution.details.all().delete()

            for o in ownerships:
                percent = o.units / total_units
                share = investor_share_total * Decimal(str(percent))
                DistributionDetail.objects.create(
                    distribution=distribution,
                    investor=o.investor,
                    ownership_percentage=round(percent * 100, 2),
                    amount_received=share
                )

            return_data = ProductionDetailSerializer(production).data
            return Response(return_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat menghapus data.'}, status=status.HTTP_403_FORBIDDEN)
        
        production.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)