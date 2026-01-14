from rest_framework import serializers
from .models import Asset

class AsetSerializer(serializers.ModelSerializer):
    # Field kalkulasi (Read Only)
    investors_info = serializers.SerializerMethodField()
    total_investment = serializers.ReadOnlyField()
    
    # Format gambar agar tampil URL lengkap
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = Asset
        fields = [
            'id', 
            'name', 
            'type',           # Pilihan lama (lahan, alat, dll)
            'location', 
            'size', 
            'value',
            'acquisition_date', 
            'ownership_status', # Pilihan lama (full_ownership, dll)
            'image',            # Ganti document_url jadi image
            'landowner',        # Sekarang ini teks biasa
            'landowner_share_percentage', 
            'total_investment',
            'investors_info', 
            'created_at'
        ]
    
    def get_investors_info(self, obj):
        """
        Mengambil info investor dari tabel Ownership (Apps lain).
        """
        # Kita gunakan try-except agar tidak error jika app ownership belum siap
        try:
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
        except AttributeError:
            return []

class AsetCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer khusus untuk Input Data (Create/Update).
    Memastikan validasi persentase berjalan.
    """
    image = serializers.ImageField(required=False)

    class Meta:
        model = Asset
        fields = [
            'name', 'type', 'location', 'size', 'value',
            'acquisition_date', 'ownership_status', 'image',
            'landowner', 'landowner_share_percentage'
        ]
    
    def validate_landowner_share_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Persentase harus antara 0-100")
        return value