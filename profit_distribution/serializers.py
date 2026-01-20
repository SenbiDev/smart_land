from rest_framework import serializers
from .models import ProfitDistribution, ProfitDistributionItem

class ProfitDistributionItemSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.name', read_only=True)
    
    class Meta:
        model = ProfitDistributionItem
        fields = ['id', 'investor', 'investor_name', 'amount', 'role', 'description']

class ProfitDistributionSerializer(serializers.ModelSerializer):
    items = ProfitDistributionItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProfitDistribution
        fields = ['id', 'date', 'total_distributed', 'notes', 'items', 'created_at']