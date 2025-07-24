from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Expense
from .serializers import ExpanceSerializer

# Create your views here.

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def list_expense(request):
    if request.method == 'GET':
        expense = Expense.objects.all()
        serializer = ExpanceSerializer(expense, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ExpanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def tambah_ex(request):