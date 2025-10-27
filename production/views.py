# File: senbidev/smart_land/smart_land-faiz/production/views.py
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
# Impor izin kustom baru
from authentication.permissions import IsAdminOrSuperadmin, IsOpratorOrAdmin

# ❗️ DIHAPUS: Konstanta tidak lagi digunakan
# OWNER_SHARE_PERCENTAGE = Decimal("0.10") 

@api_view(['GET', 'POST'])
@permission_classes([IsOpratorOrAdmin]) # Oprator boleh GET (list) dan POST (create)
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

            # --- POIN 2: Ambil persentase dinamis dari Aset ---
            owner_share_percent_decimal = asset.landowner_share_percentage / Decimal("100.0")
            owner_share = net_profit * owner_share_percent_decimal
            # --------------------------------------------------
            
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1  

            # --- POIN 3: Gunakan update_or_create ---
            distribution, created = ProfitDistribution.objects.update_or_create(
                production=production, # Kunci unik
                defaults={
                    'period': str(production.date),
                    'net_profit': net_profit,
                    'landowner_share': owner_share,
                    'investor_share': investor_share_total,
                    'created_at': timezone.now()
                }
            )

            # Jika meng-update, hapus detail lama agar tidak tumpang tindih
            if not created:
                distribution.details.all().delete()
            # ------------------------------------------

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
@permission_classes([IsOpratorOrAdmin]) # Oprator boleh GET (detail)
def production_detail(request, pk):
    production = get_object_or_404(Production, pk=pk)

    if request.method == 'GET':
        serializer = ProductionSerializer(production)
        return Response(serializer.data)

    is_admin = request.user.role == 'Admin' or request.user.role == 'Superadmin'

    if request.method in ['PUT', 'PATCH']:
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat mengubah data.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        quantity = float(data.get('quantity', production.quantity))
        unit_price = float(data.get('unit_price', production.unit_price))
        total_value = Decimal(str(quantity)) * Decimal(str(unit_price))

        serializer = ProductionSerializer(production, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            production = serializer.save(total_value=total_value)
            asset = production.asset
            net_profit = total_value

            # --- POIN 2: Ambil persentase dinamis dari Aset ---
            owner_share_percent_decimal = asset.landowner_share_percentage / Decimal("100.0")
            owner_share = net_profit * owner_share_percent_decimal
            # --------------------------------------------------
            
            investor_share_total = net_profit - owner_share

            ownerships = Ownership.objects.filter(asset=asset)
            total_units = sum(o.units for o in ownerships) or 1

            # --- POIN 3: Gunakan update_or_create ---
            distribution, created = ProfitDistribution.objects.update_or_create(
                production=production, # Kunci unik
                defaults={
                    'period': str(production.date),
                    'net_profit': net_profit,
                    'landowner_share': owner_share,
                    'investor_share': investor_share_total,
                    'created_at': timezone.now()
                }
            )

            # Jika meng-update, hapus detail lama
            if not created:
                distribution.details.all().delete()
            # ------------------------------------------

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
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat menghapus data.'}, status=status.HTTP_403_FORBIDDEN)
        
        production.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)