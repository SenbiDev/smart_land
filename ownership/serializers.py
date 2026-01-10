from rest_framework import serializers
from .models import Ownership

class OwnershipSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.user.username', read_only=True)
    # Handle nama aset (bisa null jika Dana Mengendap)
    asset_name = serializers.SerializerMethodField()
    # Ambil nilai investasi dari funding terkait
    total_investment = serializers.DecimalField(source='funding.amount', max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Ownership
        # [PENTING] Tambahkan 'status' di sini
        fields = [
            'id', 'investor', 'investor_name', 
            'asset', 'asset_name', 
            'funding', 'units', 
            'ownership_percentage', 'investment_date', 
            'status', # <--- INI WAJIB ADA
            'total_investment'
        ]

    def get_asset_name(self, obj):
        return obj.asset.name if obj.asset else "Dana Mengendap (Cash)"

# Serializer untuk Summary (Opsional, jika dipakai di view lain)
class OwnershipSummarySerializer(serializers.Serializer):
    total_investors = serializers.IntegerField()
    total_units = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_investment = serializers.DecimalField(max_digits=20, decimal_places=2)
    price_per_unit = serializers.DecimalField(max_digits=20, decimal_places=2)

class OwnershipCompositionSerializer(serializers.Serializer):
    investor_id = serializers.IntegerField()
    investor_name = serializers.CharField()
    investor_type = serializers.CharField()
    units = serializers.IntegerField()
    percentage = serializers.FloatField()
    total_investment = serializers.FloatField()
    join_date = serializers.DateField()
    status = serializers.CharField()