from rest_framework import serializers
from .models import Expense

class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

    def validate(self, data):
        # ... validasi logika bisnis ...
        return data

class ExpenseDetailSerializer(serializers.ModelSerializer):
    # Gunakan SerializerMethodField agar AMAN jika relasi null
    project_name = serializers.SerializerMethodField()
    asset_name = serializers.SerializerMethodField()
    funding_source_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'amount', 'date', 'description', 
            'proof_url', 'project_id', 'funding_id', 'created_at',
            'project_name', 'asset_name', 'funding_source_name'
        ]

    def get_project_name(self, obj):
        return obj.project_id.name if obj.project_id else '-'

    def get_asset_name(self, obj):
        # Akses nested relation dengan aman
        if obj.project_id and obj.project_id.asset:
            return obj.project_id.asset.name
        return '-'

    def get_funding_source_name(self, obj):
        if obj.funding_id and obj.funding_id.source:
            return obj.funding_id.source.name
        return '-'