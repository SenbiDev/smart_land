from rest_framework import serializers
from .models import SystemConfig

class SystemConfigSerializer(serializers.ModelSerializer):
    # Field tambahan hasil kalkulasi method di models.py
    total_asset_value = serializers.ReadOnlyField()
    total_cash_on_hand = serializers.ReadOnlyField()
    shares_sold = serializers.ReadOnlyField()
    shares_available = serializers.ReadOnlyField()

    class Meta:
        model = SystemConfig
        fields = '__all__'