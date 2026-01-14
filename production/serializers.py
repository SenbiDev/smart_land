from rest_framework import serializers
from .models import Production

class ProductionSerializer(serializers.ModelSerializer):
    # Menampilkan nama aset (bukan cuma ID) saat GET data
    asset_name = serializers.ReadOnlyField(source='asset.name')

    class Meta:
        model = Production
        fields = '__all__'