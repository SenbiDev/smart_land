from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Expense
from django.db.models import Sum
from .serializers import ExpenseSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def list_expense(request):
    if request.method == 'GET':
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def expense__list_create(request):
    if request.method == 'GET':
        project_id = request.GET.get('project_id')
        funding_id = request.GET.get('funding_id')
        asset_id = request.GET.get('asset_id')

        expenses = Expense.objects.all()
        if project_id : expenses = expenses.filter(project_id = project_id)
        if funding_id : expenses = expenses.filter(funding_id = funding_id)
        if asset_id : expenses = expenses.filter(asset_id = asset_id)
        total = expenses.aaggregate(total=Sum('amount'))['total'] or 0 
        
        serializer = ExpenseSerializer(expenses, many=True)
        return Response({
            'total_amount': total,
            'expenses': 
        serializer.data
        })
    
    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions])
