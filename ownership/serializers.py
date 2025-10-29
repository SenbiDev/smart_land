from rest_framework import serializers
from .models import Ownership
from decimal import Decimal

class OwnershipSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.user.username', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    investor_type = serializers.SerializerMethodField()
    total_investment = serializers.SerializerMethodField()

    class Meta:
        model = Ownership
        fields = [
            'id', 'investor', 'investor_name', 'investor_type',
            'asset', 'asset_name', 'funding',
            'units', 'ownership_percentage', 'investment_date',
            'total_investment'
        ]
        read_only_fields = ['ownership_percentage']

    def get_investor_type(self, obj):
        username = obj.investor.user.username.lower()
        if 'pt' in username or 'cv' in username:
            return 'corporate'
        elif 'yayasan' in username:
            return 'yayasan'
        return 'individual'

    def get_total_investment(self, obj):
        return getattr(obj.funding, 'amount', Decimal('0.00'))


class OwnershipSummarySerializer(serializers.Serializer):
    total_investors = serializers.IntegerField()
    total_units = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_investment = serializers.DecimalField(max_digits=15, decimal_places=2)
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2)


class OwnershipCompositionSerializer(serializers.Serializer):
    investor_id = serializers.IntegerField()
    investor_name = serializers.CharField()
    investor_type = serializers.CharField()
    units = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentage = serializers.FloatField()
    total_investment = serializers.DecimalField(max_digits=15, decimal_places=2)
    join_date = serializers.DateField()
    status = serializers.CharField()
