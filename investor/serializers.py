from rest_framework import serializers
from .models import Investor
from django.contrib.auth import get_user_model

User = get_user_model()

class InvestorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Investor
        fields = ['id', 'user', 'username', 'email', 'contact', 'join_date', 'total_investment']
        extra_kwargs = {
            'user': {'required': True}
        }