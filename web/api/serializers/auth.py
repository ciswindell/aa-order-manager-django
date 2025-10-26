"""Authentication serializers."""

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff"]
        read_only_fields = ["id", "is_staff"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to include user data in response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user data to response
        data["user"] = UserSerializer(self.user).data
        return data
