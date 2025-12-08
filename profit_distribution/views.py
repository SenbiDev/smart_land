from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ProfitDistribution
from .serializers import ProfitDistributionSerializer
from authentication.permissions import IsAdminOrSuperadmin, IsOperatorOrAdmin, IsViewerOrInvestorReadOnly

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated]) # atau sesuaikan permission custom jika perlu
def profit_distribution_list(request):
    if request.method == 'GET':
        distributions = ProfitDistribution.objects.select_related('production__asset').all()
        
        # --- REFACTOR START: Data Scoping ---
        if request.user.role and request.user.role.name == 'Investor':
            # Hanya tampilkan distribusi profit dari aset dimana investor menanam modal
            distributions = distributions.filter(production__asset__ownerships__investor__user=request.user).distinct()
        # --- REFACTOR END ---

        serializer = ProfitDistributionSerializer(distributions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Pastikan hanya admin/sistem yang bisa buat ini (biasanya otomatis by system di module production)
        is_admin = request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])
        if not is_admin:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfitDistributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def profit_distribution_detail(request, pk):
    try:
        distribution = ProfitDistribution.objects.select_related('production__asset').get(pk=pk)
    except ProfitDistribution.DoesNotExist:
        return Response({'message': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    # Cek akses Investor
    if request.user.role and request.user.role.name == 'Investor':
        has_access = False
        if distribution.production and distribution.production.asset:
             has_access = distribution.production.asset.ownerships.filter(investor__user=request.user).exists()
        
        if not has_access:
            return Response({'error': 'Akses ditolak.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ProfitDistributionSerializer(distribution)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Cek admin
        is_admin = request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])
        if not is_admin:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfitDistributionSerializer(distribution, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Cek admin
        is_admin = request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])
        if not is_admin:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        distribution.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)