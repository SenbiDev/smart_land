from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions 
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated

# [TAMBAHAN IMPORTS] Diperlukan untuk logika filter Investor
from ownership.models import Ownership
from investor.models import Investor

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def list_project(request):
    user = request.user
    
    # Default: Ambil semua proyek (untuk Admin, Operator, Viewer)
    projects = Project.objects.select_related('asset').all().order_by('-start_date')

    # [LOGIC KHUSUS INVESTOR]
    # Jika yang login adalah Investor, filter hanya proyek yang asetnya mereka miliki
    if user.role and user.role.name == 'Investor':
        try:
            # 1. Dapatkan profile investor dari user yang login
            investor_profile = Investor.objects.get(user=user)
            
            # 2. Cari ID aset yang dimiliki oleh investor ini di tabel Ownership
            owned_asset_ids = Ownership.objects.filter(
                investor=investor_profile
            ).values_list('asset_id', flat=True)
            
            # 3. Filter proyek berdasarkan aset tersebut
            projects = projects.filter(asset_id__in=owned_asset_ids)
            
        except Investor.DoesNotExist:
            # Jika user role Investor tapi belum terdaftar di tabel Investor, kosongkan data
            projects = Project.objects.none()
        except Exception:
            # Safety catch
            projects = Project.objects.none()

    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def tambah_project(request):
    # Hanya Admin/Superadmin yang boleh create
    is_allowed = request.user.is_superuser or (
        request.user.role and request.user.role.name in ['Admin', 'Superadmin']
    )
    
    if not is_allowed:
         return Response({'error': 'Hanya Admin yang dapat menambah data.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated]) 
def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    # Cek Role Manual untuk Update/Delete
    is_admin = request.user.is_superuser or (
        request.user.role and request.user.role.name in ['Admin', 'Superadmin']
    )

    if request.method == 'PUT':
        if not is_admin:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_admin:
             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response({'message': 'Project deleted'}, status=status.HTTP_204_NO_CONTENT)