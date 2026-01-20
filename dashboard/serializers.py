from rest_framework import serializers
from .models import SystemConfig

class SystemConfigSerializer(serializers.ModelSerializer):
    # Daftarkan semua field hitungan di sini
    total_assets = serializers.ReadOnlyField()      # Count
    total_asset_value = serializers.ReadOnlyField() # Value Rp
    total_funding = serializers.ReadOnlyField()
    total_revenue = serializers.ReadOnlyField()
    total_expense = serializers.ReadOnlyField()
    total_yield = serializers.ReadOnlyField()
    total_cash_on_hand = serializers.ReadOnlyField()
    shares_sold = serializers.ReadOnlyField()
    shares_available = serializers.ReadOnlyField()

    class Meta:
        model = SystemConfig
        fields = '__all__'