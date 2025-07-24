from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Ownership
from .serializers import OwnershipSerializer

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ownership_list(request):
    if request.method == 'GET':
        ownerships = Ownership.objects.all()
        serializer = OwnershipSerializer(ownerships, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OwnershipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ownership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)