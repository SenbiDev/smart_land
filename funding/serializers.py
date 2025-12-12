from rest_framework import serializers
from django.db.models import Sum
from .models import Funding

class FundingSerializer(serializers.ModelSerializer):
    # Tambahkan field komputasi agar muncul di List View
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    project_name = serializers.SerializerMethodField()
    
    # Field kalkulasi keuangan
    total_terpakai = serializers.SerializerMethodField()
    sisa_dana = serializers.SerializerMethodField()
    persen_terpakai = serializers.SerializerMethodField()

    class Meta:
        model = Funding
        fields = [
            'id', 'project', 'project_name', 'source', 'source_name', 'source_type',
            'amount', 'date_received', 'purpose', 'status', 'created_at',
            'total_terpakai', 'sisa_dana', 'persen_terpakai'
        ]
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True}
        }

    def get_project_name(self, obj):
        return obj.project.name if obj.project else "Dana Belum Dialokasikan"

    def get_total_terpakai(self, obj):
        # Menghitung total expense yang memiliki funding_id ini
        # Menggunakan related_name='expenses' dari model Expense
        total = obj.expenses.aggregate(Sum('amount'))['amount__sum']
        return total if total else 0

    def get_sisa_dana(self, obj):
        total_terpakai = self.get_total_terpakai(obj)
        return obj.amount - total_terpakai

    def get_persen_terpakai(self, obj):
        if obj.amount == 0:
            return 0
        total_terpakai = self.get_total_terpakai(obj)
        return (total_terpakai / obj.amount) * 100


class FundingDetailSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    project_name = serializers.SerializerMethodField()

    # Field kalkulasi keuangan (PENTING untuk Detail View)
    total_terpakai = serializers.SerializerMethodField()
    sisa_dana = serializers.SerializerMethodField()
    persen_terpakai = serializers.SerializerMethodField()

    class Meta:
        model = Funding
        fields = [
            'id', 'project', 'project_name', 'source', 'source_name', 'source_type',
            'amount', 'date_received', 'purpose', 'status', 'created_at',
            'total_terpakai', 'sisa_dana', 'persen_terpakai'
        ]

    def get_project_name(self, obj):
        return obj.project.name if obj.project else "Dana Belum Dialokasikan"

    # --- LOGIKA PERHITUNGAN (Sama dengan FundingSerializer) ---
    def get_total_terpakai(self, obj):
        total = obj.expenses.aggregate(Sum('amount'))['amount__sum']
        return total if total else 0

    def get_sisa_dana(self, obj):
        total_terpakai = self.get_total_terpakai(obj)
        return obj.amount - total_terpakai

    def get_persen_terpakai(self, obj):
        if obj.amount == 0:
            return 0
        total_terpakai = self.get_total_terpakai(obj)
        return (total_terpakai / obj.amount) * 100


class FundingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funding
        fields = ['project', 'source', 'amount', 'date_received', 'purpose', 'status']
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True}
        }