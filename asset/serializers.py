from rest_framework import serializers
from .models import Asset, Owner

class AsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Owner
        fields= '__all__'