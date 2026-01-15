from rest_framework import serializers
from .models import ProfitDistribution

class ProfitDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitDistribution
        fields = '__all__'
        # Mencegah user kirim data hitungan manual via API
        read_only_fields = (
            'landowner_total_amount', 
            'investor_total_amount', 
            'retained_earnings', 
            'dividend_per_share', 
            'distribution_details'
        )