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
        fields = ('username', 'email', 'password', 'password2', 'role')
        extra_kwargs = {
            'role': {'required': False, 'default': 'user'}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'user')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
