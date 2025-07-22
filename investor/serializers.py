from rest_framework import serializers
from .models import Investor
from django.contrib.auth import get_user_model

User = get_user_model()

class InvestorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Investor
        fields = ['id', 'user', 'contact', 'join_date', 'total_investment']