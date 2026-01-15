from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import ProfitDistribution
from .serializers import ProfitDistributionSerializer
from authentication.permissions import IsAdminOrSuperadmin
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_distribution(request):
    queryset = ProfitDistribution.objects.all()
    serializer = ProfitDistributionSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperadmin])
def create_distribution(request):
    serializer = ProfitDistributionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() # Ini akan memanggil logika save() di models.py
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin])
def distribution_detail(request, pk):
    try:
        dist = ProfitDistribution.objects.get(pk=pk)
    except ProfitDistribution.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfitDistributionSerializer(dist)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfitDistributionSerializer(dist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        dist.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)