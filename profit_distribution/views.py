from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ProfitDistribution
from .serializers import ProfitDistributionSerializer

@api_view(['GET', 'POST'])
def profit_distribution_list(request):
    if request.method == 'GET':
        distributions = ProfitDistribution.objects.all()
        serializer = ProfitDistributionSerializer(distributions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProfitDistributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def profit_distribution_detail(request, pk):
    try:
        distribution = ProfitDistribution.objects.get(pk=pk)
    except ProfitDistribution.DoesNotExist:
        return Response({'message': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfitDistributionSerializer(distribution)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfitDistributionSerializer(distribution, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        distribution.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
