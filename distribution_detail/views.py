from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsAdminOrSuperadmin, IsViewerOrInvestorReadOnly
from .models import DistributionDetail
from .serializers import DistributionDetailSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrSuperadmin | IsViewerOrInvestorReadOnly])
def distribution_detail_list(request):
    if request.method == 'GET':
        data = DistributionDetail.objects.all()
        serializer = DistributionDetailSerializer(data, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DistributionDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperadmin | IsViewerOrInvestorReadOnly])
def distribution_detail_detail(request, pk):
    try:
        data = DistributionDetail.objects.get(pk=pk)
    except DistributionDetail.DoesNotExist:
        return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DistributionDetailSerializer(data)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DistributionDetailSerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)