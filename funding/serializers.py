from rest_framework import serializers
from .models import Funding
from decimal import Decimal 

# Serializer sederhana untuk CREATE dan UPDATE
class FundingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funding
        fields = '__all__'

# Serializer "Pintar" untuk GET (Read)
class FundingDetailSerializer(serializers.ModelSerializer):
    # 1. Menambahkan nama dari relasi (sesuai ERD)
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    # 2. Menambahkan field kalkulasi (dari views.py)
    total_terpakai = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    sisa_dana = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    persen_terpakai = serializers.FloatField(read_only=True)

    class Meta:
        model = Funding
        fields = [
            'id',
            'amount',
            'date_received',
            'purpose',
            'status',
            'created_at',
            'project',
            'project_name', 
            'source',
            'source_name',  
            'source_type', 
            'total_terpakai', 
            'sisa_dana',      
            'persen_terpakai'
        ]