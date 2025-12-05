from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .models import Expense
from .serializers import ExpenseCreateUpdateSerializer, ExpenseDetailSerializer
from authentication.permissions import IsAdminOrSuperadmin, IsOperatorOrAdmin

@api_view(['GET', 'POST'])
@permission_classes([IsOperatorOrAdmin])
def list_expense(request):
    if request.method == 'GET':
        queryset = Expense.objects.select_related(
            'project_id__asset',
            'funding_id__source'
        ).all().order_by('-date')
        
        asset_id = request.query_params.get('asset')
        if asset_id and asset_id != 'all':
            try:
                queryset = queryset.filter(project_id__asset_id=int(asset_id))
            except (ValueError, TypeError):
                pass
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search)
            )
        
        category = request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        serializer = ExpenseDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExpenseCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            expense = serializer.save()
            return_data = ExpenseDetailSerializer(expense).data
            return Response(return_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOperatorOrAdmin])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.select_related(
            'project_id__asset',
            'funding_id__source'
        ).get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExpenseDetailSerializer(expense)
        return Response(serializer.data)

    is_admin = request.user.is_superuser or (
        request.user.role and request.user.role.name in ['Admin', 'Superadmin']
    )

    if request.method == 'PUT':
        if not is_admin:
            return Response(
                {'error': 'Hanya Admin yang dapat mengubah data.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ExpenseCreateUpdateSerializer(expense, data=request.data)
        if serializer.is_valid():
            expense = serializer.save()
            return_data = ExpenseDetailSerializer(expense).data
            return Response(return_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_admin:
            return Response(
                {'error': 'Hanya Admin yang dapat menghapus data.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)