from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ProfitDistribution
from .serializers import ProfitDistributionSerializer

# Create your views here.
@api_view(['GET', 'POST'])
def profit_distribution_list(request):
    if request.method == 'GET':
        productions = ProfitDistribution.objects.all().order_by('-date')
        serializer = ProfitDistributionSerializer(productions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def production_detail(request, pk):
    try:
        production = Production.objects.get(pk=pk)
    except Production.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductionSerializer(production)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProductionSerializer(production, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        production.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)