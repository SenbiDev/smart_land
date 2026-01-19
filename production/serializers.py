from rest_framework import serializers
from .models import Production, Product

# --- PERHATIKAN: SAYA MENGHAPUS IMPORT DARI ASSET ---
# Kita tidak import AsetSerializer lagi supaya tidak error 500

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductionSerializer(serializers.ModelSerializer):
    # 1. Product Details (Aman karena satu folder)
    product_details = ProductSerializer(source='product', read_only=True)

    # 2. Asset Details (SOLUSI ERROR 500)
    # Kita buat field custom manual tanpa perlu import file lain
    asset_details = serializers.SerializerMethodField()

    class Meta:
        model = Production
        fields = [
            'id', 
            'asset', 'asset_details',     # asset (Input ID), asset_details (Output Object)
            'product', 'product_details', # product (Input ID), product_details (Output Object)
            'quantity', 'unit_price', 'date', 'status', 
            'created_at', 'updated_at'
        ]

    # Fungsi ini otomatis dipanggil untuk mengisi field 'asset_details'
    def get_asset_details(self, obj):
        # Jika data produksi punya aset, kita kembalikan data simpelnya
        if obj.asset:
            return {
                "id": obj.asset.id,
                "name": obj.asset.name,
                "type": obj.asset.type  # Pastikan di model Asset ada field 'type' atau 'asset_type'
            }
        return None