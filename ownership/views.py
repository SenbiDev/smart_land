from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from decimal import Decimal
from .models import Ownership
from .serializers import (
    OwnershipSerializer,
    OwnershipSummarySerializer,
    OwnershipCompositionSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ownership_list(request):
    if request.method == 'GET':
        ownerships = Ownership.objects.select_related(
            'investor__user', 'asset', 'funding'
        ).all()  # ← UBAH INI (optimize query)
        
        # Tambah filter by asset (opsional, biar bisa filter)
        asset_id = request.query_params.get('asset_id')
        if asset_id:
            ownerships = ownerships.filter(asset_id=asset_id)
        
        serializer = OwnershipSerializer(ownerships, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OwnershipSerializer(data=request.data)
        if serializer.is_valid():
            ownership = serializer.save()

            asset_id = serializer.data['asset']
            total_units = Ownership.objects.filter(asset=asset_id).aggregate(total=Sum('units'))['total'] or 0
            
            for o in Ownership.objects.filter(asset=asset_id):
                o.ownership_percentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
                o.save(update_fields=['ownership_percentage'])

            ownership.refresh_from_db()
        
            update_serializer = OwnershipSerializer(ownership)
            return Response(update_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def ownership_detail(request, pk):
    try:
        ownership = Ownership.objects.get(pk=pk)
    except Ownership.DoesNotExist:
        return Response({'error': 'Ownership not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OwnershipSerializer(ownership)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OwnershipSerializer(ownership, data=request.data)
        if serializer.is_valid():
            serializer.save()

            asset_id = serializer.data['asset']
            total_units = Ownership.objects.filter(asset=asset_id).aggregate(total=Sum('units'))['total'] or 0
            for o in Ownership.objects.filter(asset=asset_id):
                o.ownership_percentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
                o.save(update_fields=['ownership_percentage'])
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        asset_id = ownership.asset.id
        ownership.delete()

        total_units = Ownership.objects.filter(asset=asset_id).aggregate(total=Sum('units'))['total'] or 0
        for o in Ownership.objects.filter(asset=asset_id):
            o.ownership_percentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
            o.save(update_fields=['ownership_percentage'])
                
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ownership_summary(request):
    asset_id = request.query_params.get('asset_id')
    if not asset_id:
        return Response({'error': 'asset_id required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        from asset.models import Asset
        asset = Asset.objects.get(id=asset_id)
        
        ownerships = Ownership.objects.filter(asset_id=asset_id)
        
        summary = ownerships.aggregate(
            total_investors=Count('investor', distinct=True),
            total_units=Sum('units'),
            total_investment=Sum('funding__amount')
        )
        
        total_units = summary['total_units'] or Decimal('0')
        total_investment = summary['total_investors'] or Decimal('0')
        if total_units > 0:
            price_per_unit = total_investment / total_units 
            
        data = {
            'total_investors': summary['total_investors'] or 0,
            'total_units': total_units,
            'total_investment': total_investment,
            'price_per_unit': price_per_unit
        }
        
        from .serializers import OwnershipSummarySerializer
        serializer = OwnershipSummarySerializer(data)
        return Response(serializer.data)
    
    except Asset.DoesNotExist:
        return Response({'error': 'asset not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ownership_composition(request):
    """Komposisi untuk pie chart & list investor"""
    asset_id = request.query_params.get('asset_id')
    
    if not asset_id:
        return Response({'error': 'asset_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from asset.models import Asset
        asset = Asset.objects.get(id=asset_id)
        
        ownerships = Ownership.objects.filter(
            asset_id=asset_id
        ).select_related('investor__user', 'funding').order_by('-ownership_percentage')
        
        composition = []
        for ownership in ownerships:
            # Deduce investor type dari username
            username = ownership.investor.user.username.lower()
            if 'pt' in username or 'cv' in username:
                investor_type = 'corporate'
            elif 'yayasan' in username:
                investor_type = 'yayasan'
            else:
                investor_type = 'individual'
            
            composition.append({
                'investor_id': ownership.investor.id,
                'investor_name': ownership.investor.user.username,
                'investor_type': investor_type,
                'units': ownership.units,
                'percentage': ownership.ownership_percentage,
                'total_investment': float(ownership.funding.amount),
                'join_date': ownership.investment_date,
                'status': 'active'
            })
        
        from .serializers import OwnershipCompositionSerializer
        serializer = OwnershipCompositionSerializer(composition, many=True)
        return Response(serializer.data)
        
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)
