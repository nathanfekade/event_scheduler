"""User serializer module for handling user data in the event scheduler."""
from typing import Any, Dict
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, handling user creation and updates."""
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value: str) -> str:
        """Validate that the email is provided and unique.

        Args:
            value: The email address to validate.

        Raises:
            serializers.ValidationError: If the email is empty
            or already exists.

        Returns:
            The validated email address.
        """
        if not value:
            raise serializers.ValidationError("Email address is required")
        if User.objects.filter(email=value).exists():
            if not self.instance or self.instance.email != value:
                raise serializers.ValidationError(
                    "Email already in use"
                )
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a new user with the provided data.

        Args:
            validated_data: Dictionary containing user data.

        Returns:
            The created User instance.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """Update an existing user with the provided data.

        Args:
            instance: The User instance to update.
            validated_data: Dictionary containing updated user data.

        Returns:
            The updated User instance.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
