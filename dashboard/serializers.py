from rest_framework import serializers

class DashboardSerializers(serializers.Serializer):
    total_assets = serializers.IntegerField()
    total_funding = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_yield = serializers.DecimalField(max_digits=15, decimal_places=2)
    owenersip_percentage = serializers.FloatField(allow_null=True)