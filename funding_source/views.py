from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FundingSource
from .serializers import FundingSourceSerializer
# Create your views here.

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def funding_source_list(request):
    if request.method == 'GET':
        sources = FundingSource.objects.all()
        serializer = FundingSourceSerializer(sources, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FundingSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def funding_source_detail(request, pk):
    try:
        source = FundingSource.objects.get(pk=pk)
    except FundingSource.DoesNotExist:
        return Response({'error': 'funding source not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FundingSourceSerializer(source)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FundingSourceSerializer(source, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        source.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)