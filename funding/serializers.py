from rest_framework import serializers
from .models import Funding

class FundingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funding
        fields = '__all__'
        # [PERUBAHAN] Validasi project tidak wajib
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True}
        }

class FundingDetailSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Funding
        fields = [
            'id', 'project', 'project_name', 'source', 'source_name', 'source_type',
            'amount', 'date_received', 'purpose', 'status', 'created_at'
        ]

    def get_project_name(self, obj):
        # [PERUBAHAN] Handle jika project kosong
        return obj.project.name if obj.project else "Dana Belum Dialokasikan"

class FundingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funding
        fields = ['project', 'source', 'amount', 'date_received', 'purpose', 'status']
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True}
        }