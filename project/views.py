from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions 
from django.db.models import Q 
from .models import Project
from .serializers import ProjectSerializer
from authentication.permissions import IsAdminOrSuperadmin
from expense.models import Expense
from ownership.models import Ownership
from investor.models import Investor 

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_project(request):
    user = request.user
    projects = Project.objects.all().order_by('-start_date') 

    if user.role == 'Investor':
        try:
            investor = user.investor
            owned_asset_ids = Ownership.objects.filter(investor=investor).values_list('asset_id', flat=True).distinct()
            relevant_project_ids = Expense.objects.filter(
                asset_id__in=owned_asset_ids,
                project_id__isnull=False
            ).values_list('project_id', flat=True).distinct()

            projects = projects.filter(id__in=relevant_project_ids)

        except Investor.DoesNotExist:
            projects = Project.objects.none()

    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated]) 
def tambah_project(request):
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
@permission_classes([permissions.IsAuthenticated]) 
def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    is_admin = request.user.is_superuser or (
        request.user.role and request.user.role.name in ['Admin', 'Superadmin']
    )

    if request.method == 'PUT':
        if not is_admin:
             return Response({'error': 'Hanya Admin yang dapat mengubah data.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_admin:
             return Response({'error': 'Hanya Admin yang dapat menghapus data.'}, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response({'message': 'Project deleted'}, status=status.HTTP_204_NO_CONTENT)