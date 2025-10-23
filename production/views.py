from decimal import Decimal
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Production
from .serializers import ProductionSerializer
from asset.models import Asset
from ownership.models import Ownership
from investor.models import Investor
from profit_distribution.models import ProfitDistribution
from distribution_detail.models import DistributionDetail

# Konstanta untuk persentase owner
OWNER_SHARE_PERCENTAGE = Decimal("0.10")

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def production_list(request):
    if request.method == 'GET':
        productions = Production.objects.all().order_by('-date')
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductionSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            unit_price = serializer.validated_data['unit_price']
            total_value = Decimal(str(quantity)) * unit_price

            production = serializer.save(total_value=total_value)
            asset = production.asset
            net_profit = total_value

            owner_share = net_profit * OWNER_SHARE_PERCENTAGE
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1  

            distribution = ProfitDistribution.objects.create(
                production=production,
                period=str(production.date),
                net_profit=net_profit,
                landowner_share=owner_share,
                investor_share=investor_share_total,
                created_at=timezone.now()
            )

            investor_distributions = []
            for o in ownerships:
                percent = o.units / total_units
                share = investor_share_total * Decimal(str(percent))
                DistributionDetail.objects.create(
                    distribution=distribution,
                    investor=o.investor,
                    ownership_percentage=round(percent * 100, 2),
                    amount_received=share
                )
                investor_distributions.append({
                    'investor': o.investor.user.username,
                    'percentage': round(percent * 100, 2),
                    'share': str(share)
                })

            return Response({
                'production': ProductionSerializer(production).data,
                'profit_distribution': {
                    'owner_share': str(float(owner_share)),
                    'investor_distributions': investor_distributions
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def production_detail(request, pk):
    production = get_object_or_404(Production, pk=pk)

    if request.method == 'GET':
        serializer = ProductionSerializer(production)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        data = request.data.copy()
        quantity = float(data.get('quantity', production.quantity))
        unit_price = float(data.get('unit_price', production.unit_price))
        total_value = Decimal(str(quantity)) * Decimal(str(unit_price))

        serializer = ProductionSerializer(production, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            production = serializer.save(total_value=total_value)
            asset = production.asset
            net_profit = total_value

            owner_share = net_profit * OWNER_SHARE_PERCENTAGE
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1

            distribution = ProfitDistribution.objects.create(
                production=production,
                period=str(production.date),
                net_profit=net_profit,
                landowner_share=owner_share,
                investor_share=investor_share_total,
                created_at=timezone.now()
            )

            investor_distributions = []
            for o in ownerships:
                percent = o.units / total_units
                share = investor_share_total * Decimal(str(percent))
                DistributionDetail.objects.create(
                    distribution=distribution,
                    investor=o.investor,
                    ownership_percentage=round(percent * 100, 2),
                    amount_received=share
                )
                investor_distributions.append({
                    'investor': o.investor.user.username,
                    'percentage': round(percent * 100, 2),
                    'share': str(share)
                })

            return Response({
                'production': ProductionSerializer(production).data,
                'profit_distribution': {
                    'owner_share': str(owner_share),
                    'investor_distributions': investor_distributions
                }
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        production.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)