from rest_framework import serializers
from .models import Asset, Owner

class OwnerSerializer(serializers.ModelSerializer):
    # Hitung berapa aset yang dimiliki
    total_assets = serializers.SerializerMethodField()
    
    class Meta:
        model = Owner
        fields = ['id', 'nama', 'kontak', 'alamat', 'nomor_rekening', 'bank', 'total_assets']
    
    def get_total_assets(self, obj):
        return obj.assets.count()

class AsetSerializer(serializers.ModelSerializer):
    # Nested serializer untuk menampilkan info owner
    landowner_name = serializers.CharField(source='landowner.nama', read_only=True)
    landowner_contact = serializers.CharField(source='landowner.kontak', read_only=True)
    
    # Info investor (dari tabel Ownership)
    investors_info = serializers.SerializerMethodField()
    total_investment = serializers.ReadOnlyField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'type', 'location', 'size', 'value',
            'acquisition_date', 'ownership_status', 'document_url',
            'landowner', 'landowner_name', 'landowner_contact',
            'landowner_share_percentage', 'total_investment',
            'investors_info', 'created_at'
        ]
    
    def get_investors_info(self, obj):
        """Daftar investor dengan persentase kepemilikan"""
        ownerships = obj.ownerships.select_related('investor__user').all()
        return [
            {
                'investor_id': o.investor.id,
                'investor_name': o.investor.user.username,
                'units': o.units,
                'ownership_percentage': o.ownership_percentage,
                'investment_date': o.investment_date
            }
            for o in ownerships
        ]

class AsetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer khusus untuk Create/Update (tanpa nested fields)"""
    
    class Meta:
        model = Asset
        fields = [
            'name', 'type', 'location', 'size', 'value',
            'acquisition_date', 'ownership_status', 'document_url',
            'landowner', 'landowner_share_percentage'
        ]
    
    def validate_landowner_share_percentage(self, value):
        """Validasi persentase bagi hasil (0-100)"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Persentase harus antara 0-100")
        return value