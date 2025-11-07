from rest_framework import serializers
from .models import Expense

# Serializer sederhana untuk CREATE/UPDATE
class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# Serializer "Pintar" untuk GET (dengan relasi)
class ExpenseDetailSerializer(serializers.ModelSerializer):
    # Nama relasi dari project & funding
    project_name = serializers.CharField(source='project_id.name', read_only=True)
    asset_name = serializers.CharField(source='project_id.asset.name', read_only=True)
    funding_source = serializers.CharField(source='funding_id.source.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id',
            'category',
            'amount',
            'date',
            'description',
            'proof_url',
            'project_id',
            'project_name', 
            'asset_name',     
            'funding_id',
            'funding_source',
            'created_at'
        ]