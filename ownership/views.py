from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import Ownership
from .serializers import OwnershipSerializer
from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ownership_list(request):
    if request.method == 'GET':
        ownership = Ownership.objects.all()
        serializer = OwnershipSerializer(ownership, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OwnershipSerializer(data=request.data)
        if serializer.is_valid():
            ownership = serializer.save()

            asset_id = serializer.data['asset']
            total_units = Ownership.objects.filter(asset=asset_id).aggregate(total=Sum('units'))['total'] or 0
            
            for o in Ownership.objects.filter(asset=asset_id):
                o.ownership_precentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
                o.save(update_fields=['ownership_precentage'])

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
                o.ownership_precentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
                o.save(update_fields=['ownership_precentage'])
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ownership.delete()

        total_units = Ownership.objects.filter(asset=asset_id).aggregate(total=Sum('units'))['total'] or 0
        for o in Ownership.objects.filter(asset=asset_id):
            o.ownership_precentage = round ((o.units / total_units) * 100, 2) if total_units > 0 else 0
            o.save(update_fields=['ownership_precentage'])
                
        return Response(status=status.HTTP_204_NO_CONTENT)