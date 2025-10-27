# File: senbidev/smart_land/smart_land-faiz/expense/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum
from .models import Expense
from .serializers import ExpenseSerializer
<<<<<<< HEAD
from funding.models import Funding

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def expense_list_create(request):
=======
# Impor izin kustom baru
from authentication.permissions import IsAdminOrSuperadmin, IsOpratorOrAdmin

@api_view(['GET', 'POST'])
@permission_classes([IsOpratorOrAdmin]) # Oprator boleh GET (list) dan POST (create)
def list_expense(request):
>>>>>>> 81605ad0fdd8bc04bc9e0ea82437994b41368ecf
    if request.method == 'GET':
        project_id = request.GET.get('project_id') 
        funding_id = request.GET.get('funding_id')
        asset_id = request.GET.get('asset_id')

        expenses = Expense.objects.all()

        if project_id:
            expenses = expenses.filter(project_id=project_id)
        if funding_id:
            expenses = expenses.filter(funding_id=funding_id)
        if asset_id:
            expenses = expenses.filter(asset_id=asset_id)

        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            funding_id = request.data.get('funding_id')
            try:
                funding = Funding.objects.get(id=funding_id)
            except Funding.DoesNotExist:
                return Response({'error': 'Funding tidak ditemukan'}, status=status.HTTP_400_BAD_REQUEST)

            expense_amount = serializer.validated_data['amount']
            total_expense = Expense.objects.filter(funding_id=funding_id).aggregate(total=Sum('amount'))['total'] or 0

            if total_expense + expense_amount > funding.amount:
                return Response({'error': 'Dana tidak cukup'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            funding.amount -= expense_amount
            funding.save()

            return Response({
                'expense': serializer.data,
                'funding_summary': {
                    'funding_id': funding.id,
                    'funding_amount': funding.amount + expense_amount,
                    'total_expense': total_expense + expense_amount,
                    'remaining_amount': funding.amount
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
<<<<<<< HEAD
@permission_classes([permissions.IsAuthenticated])
def expense_detail_update_delete(request, pk):
=======
@permission_classes([IsOpratorOrAdmin]) # Oprator boleh GET (detail)
def expense_detail(request, pk):
>>>>>>> 81605ad0fdd8bc04bc9e0ea82437994b41368ecf
    try:
        expense = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

<<<<<<< HEAD
    elif request.method == 'PUT':
        old_amount = expense.amount
=======
    # Tambahkan pengecekan role manual untuk PUT dan DELETE
    is_admin = request.user.role == 'Admin' or request.user.role == 'Superadmin'

    if request.method == 'PUT':
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat mengubah data.'}, status=status.HTTP_403_FORBIDDEN)
        
>>>>>>> 81605ad0fdd8bc04bc9e0ea82437994b41368ecf
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            new_amount = serializer.validated_data['amount']
            funding = expense.funding_id
            total_expense_lain = Expense.objects.filter(funding_id=funding).exclude(id=expense.id).aggregate(total=Sum('amount'))['total'] or 0

            if total_expense_lain + new_amount > funding.amount + old_amount:
                return Response({'error': 'Dana tidak cukup untuk update'}, status=status.HTTP_400_BAD_REQUEST)

            # Update dana
            funding.amount += old_amount
            funding.amount -= new_amount
            funding.save()

            serializer.save()

            return Response({
                'expense': serializer.data,
                'funding_summary': {
                    'funding_id': funding.id,
                    'funding_amount': funding.amount + new_amount,
                    'total_expense': total_expense_lain + new_amount,
                    'remaining_amount': funding.amount
                }
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
<<<<<<< HEAD
        funding = expense.funding_id
        refund_amount = expense.amount
        funding.amount += refund_amount
        funding.save()
        expense.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def funding_expense_summary(request, funding_id):
    try:
        funding = Funding.objects.get(id=funding_id)
    except Funding.DoesNotExist:
        return Response({'error': 'Funding not found'}, status=status.HTTP_404_NOT_FOUND)

    expenses = Expense.objects.filter(funding_id=funding_id)
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    serializer = ExpenseSerializer(expenses, many=True)

    return Response({
        'funding_id': funding_id,
        'funding_amount': funding.amount,
        'total_expense': total,
        'remaining_amount': funding.amount - total,
        'expenses': serializer.data
    })
=======
        if not is_admin:
            return Response({'error': 'Hanya Admin yang dapat menghapus data.'}, status=status.HTTP_403_FORBIDDEN)
        
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
>>>>>>> 81605ad0fdd8bc04bc9e0ea82437994b41368ecf
