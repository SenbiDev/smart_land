from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Expense
from django.db.models import Sum
from .serializers import ExpenseSerializer
from funding.models import Funding

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
def expense_list_create(request):
    if request.method == 'GET':
        project_id = request.GET.get('project_id') 
        funding_id = request.GET.get('funding_id')
        asset_id = request.GET.get('asset_id')

        expenses = Expense.objects.all()

        if project_id: expenses = expenses.filter(project_id=project_id)
        if funding_id: expenses = expenses.filter(funding_id=funding_id)
        if asset_id: expenses = expenses.filter(asset_id=asset_id),

        serializer = ExpenseSerializer(expenses, many=True)
        return Response({serializer.data})
    
    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            funding_id = request.data.get('funding_id')
            try:
                funding = Funding.objects.get(id=funding_id)
            except Funding.DoesNotExist:
                return Response({'error': 'funding tidak di temukan'},status=status.HTTP_400_BAD_REQUEST)
            expense_amount = serializer.validated_data['amount']
            total_expense = Expense.objects.filter(funding_id=funding_id).aggregate(total=Sum('amount'))['total'] or 0

            if total_expense + expense_amount > funding.amount:
                return Response({'error': 'Dana tidak cukup'},status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            funding.amount -= expense_amount
            funding.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def expense_detail_update_delete(request, pk):
    try:
        expense = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    elif request.method == 'PUT':
        old_amount =  expense.amount
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            new_amount = serializer.validated_data['amount']
            funding = expense.funding_id
            total_expense_lain = Expense.objects.filter(funding_id=funding).exclude(id=expense.id).aggregate(total=Sum('amount'))['total'] or 0

            if total_expense_lain + new_amount > funding.amount + old_amount:
                return Response({'error': 'dana tidak mencukupi untuk update'},status=status.HTTP_400_BAD_REQUEST)
            
            funding.amount += old_amount
            funding.amount -= new_amount
            funding.save()

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        funding = expense.funding_id
        refund_amount = expense.amount
        funding.amount +=refund_amount
        funding.save() 
        expense.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def funding_expense_summary(request, funding_id):
    expenses = Expense.objects.filter(funding_id=funding_id)
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    serializer = ExpenseSerializer(expenses, many=True)
    return Response({
        'funding_id': funding_id,
        'total_expense': total,
        'expenses': serializer.data
    })
