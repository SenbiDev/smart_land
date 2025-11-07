# File: authentication/serializers.py
from rest_framework import serializers
from .models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'role')

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2= serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        # HAPUS 'role' dari fields agar tidak bisa diinput saat registrasi
        fields = ('username', 'email', 'password', 'password2')
        # HAPUS extra_kwargs untuk role

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        # Role otomatis 'Viewer' dari default model CustomUser
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
            # Tidak perlu set 'role' di sini
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'