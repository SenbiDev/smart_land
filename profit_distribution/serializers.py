from rest_framework import serializers
from .models import ProfitDistribution

class ProfitDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitDistribution
        fields = '__all__'