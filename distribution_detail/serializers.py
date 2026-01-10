from rest_framework import serializers
from .models import DistributionDetail

class DistributionDetailSerializer(serializers.ModelSerializer):
    # Menampilkan nama depan user dari relasi investor -> user
    investor_name = serializers.CharField(source='investor.user.first_name', read_only=True)

    class Meta:
        model = DistributionDetail
        fields = ['id', 'investor', 'investor_name', 'ownership_percentage', 'amount_received']