from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Investor
from .serializers import InvestorSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated]) 
def list_investor(request):  # [PENTING] Nama fungsi sesuai dengan urls.py lama
    if request.method == 'GET':
        # [SECURITY] Investor hanya boleh lihat datanya sendiri
        if request.user.role and request.user.role.name == 'Investor':
            investors = Investor.objects.filter(user=request.user).select_related('user')
        else:
            # Admin/Operator boleh lihat semua
            investors = Investor.objects.select_related('user').all()

        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Hanya Admin yang boleh create
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def investor_detail(request, pk):
    try:
        investor = Investor.objects.select_related('user').get(pk=pk)
    except Investor.DoesNotExist:
        return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

    # [SECURITY] Investor tidak boleh intip ID orang lain
    if request.user.role and request.user.role.name == 'Investor':
        if investor.user != request.user:
            return Response({'error': 'Akses ditolak.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = InvestorSerializer(investor)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Cek Permission
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # [FIX] Tambahkan partial=True agar field 'user' tidak wajib dikirim saat update
        serializer = InvestorSerializer(investor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not (request.user.is_superuser or (request.user.role and request.user.role.name in ['Admin', 'Superadmin'])):
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        investor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)