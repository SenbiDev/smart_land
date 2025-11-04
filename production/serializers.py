from rest_framework import serializers
from .models import Production

class ProductionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer sederhana untuk Create dan Update.
    Hanya menerima input, validasi di views.
    """
    class Meta:
        model = Production
        # Sertakan field status yang baru
        fields = [
            'name', 'asset', 'date', 'quantity', 'unit', 'unit_price', 'status'
        ]
        read_only_fields = ['total_value'] # total_value dihitung di view

class ProductionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer "Pintar" untuk GET (Read).
    Menambahkan data dari relasi (Asset).
    """
    # --- TAMBAHAN BARU ---
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_type = serializers.CharField(source='asset.type', read_only=True)
    # ---------------------

    class Meta:
        model = Production
        fields = [
            'id',
            'name',
            'asset',
            'asset_name',  # Baru
            'asset_type',  # Baru
            'date',
            'quantity',
            'unit',
            'unit_price',
            'total_value',
            'created_at',
            'status',      # Baru
        ]