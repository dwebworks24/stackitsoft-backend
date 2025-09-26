# home/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Users

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'phone', 'first_name', 'last_name',
                  'date_of_birth', 'profile_image', 'referal_code', 'pincode',
                  'address', 'role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'username', 'phone', 'password']

    def create(self, validated_data):
        return Users.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")
        data['user'] = user
        return data

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'phone', 'pincode', 'address', 'profile_image']
