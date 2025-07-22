from rest_framework import serializers
from .models import KategoriAset, Asset, Pemilik

class KategoriAsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriAset
        fields = '__all__'

class AsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class PemilikSerializer(serializers.ModelSerializer):
    class Meta:
        model= Pemilik
        fields= '__all__'