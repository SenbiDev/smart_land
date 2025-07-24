from rest_framework import serializers
from .models import DistributionDetail

class DistributionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionDetail
        fields = '__all__'