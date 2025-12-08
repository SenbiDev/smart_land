from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions 
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def list_project(request):
    # [TRANSPARANSI] Semua user login (Investor, Viewer, dll) BISA melihat semua proyek
    projects = Project.objects.all().order_by('-start_date')
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def tambah_project(request):
    # [PERBAIKAN] Fungsi ini dikembalikan agar match dengan urls.py Anda
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