from rest_framework import serializers
from .models import Production, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductionSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()
    asset_details = serializers.SerializerMethodField()

    class Meta:
        model = Production
        fields = [
            'id', 
            'asset', 'asset_details', 
            'product', 'product_details', 
            'quantity', 
            'unit_price', 
            'date', 'status', 
            'created_at', 'updated_at'
        ]

    def get_product_details(self, obj):
        if not obj.product:
            return None
        return {
            "id": obj.product.id,
            "name": obj.product.name,
            "unit": obj.product.unit,
            # [FIX] Tambahkan ini agar Stok Gudang di Frontend tidak 0
            "current_stock": obj.product.current_stock 
        }

    def get_asset_details(self, obj):
        if not obj.asset:
            return None
        return {
            "id": obj.asset.id,
            "name": obj.asset.name,
            "type": getattr(obj.asset, 'type', 'Unknown') 
        }