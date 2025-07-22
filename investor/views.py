from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Investor
from .serializers import InvestorSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def investor_list_create(request):
    if request.method == 'GET':
        investors = Investor.objects.all()
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def investor_detail(request, pk):
    try:
        investor = Investor.objects.get(pk=pk)
    except Investor.DoesNotExist:
        return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvestorSerializer(investor)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = InvestorSerializer(investor, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        investor.delete()
        return Response({'message': 'Investor deleted'}, status=status.HTTP_204_NO_CONTENT)
