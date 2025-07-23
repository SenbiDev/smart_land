from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Funding
from .serializers import FundingSerializer

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def funding_list(request):
    if request.method == 'GET':
        data = Funding.objects.all()
        serializer = FundingSerializer(data, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FundingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def funding_detail(request, pk):
    try:
        data = Funding.objects.get(pk=pk)
    except Funding.DoesNotExist:
        return Response({'error': 'funding not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FundingSerializer(data)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FundingSerializer(data, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)