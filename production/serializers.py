from rest_framework import serializers
from .models import Production

class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = '__all__'
        read_only_fields = ['total_value']