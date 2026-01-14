from rest_framework import serializers
from .models import Sale

class SaleSerializer(serializers.ModelSerializer):
    proof_image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = Sale
        fields = '__all__'