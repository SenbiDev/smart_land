from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Project
from .serializers import ProjectSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_project(request):
    project = Project.objects.all()
    serializer = ProjectSerializer(project, many=True)
    return Response(serializer.data) 

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def tambah_project(request):
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
    
    elif request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.delete()
        return Response({'message': 'Project deleted'}, status=status.HTTP_204_NO_CONTENT)