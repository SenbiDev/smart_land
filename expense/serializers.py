from rest_framework import serializers
from .models import Expense

class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

    def validate(self, data):
        expense_project = data.get('project_id')
        funding = data.get('funding_id')

        if funding:
            funding_project = funding.project

            if funding_project and funding_project != expense_project:
                raise serializers.ValidationError({
                    "funding_id": f"Dana ini terikat khusus untuk proyek '{funding_project.name}'. Tidak bisa digunakan untuk proyek ini."
                })
        
        return data

class ExpenseDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project_id.name', read_only=True, default='-')
    asset_name = serializers.CharField(source='project_id.asset.name', read_only=True, default='-')
    funding_source_name = serializers.CharField(source='funding_id.source.name', read_only=True)
    
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
            'funding_source_name',
            'created_at'
        ]