"""User views module for handling user-related API endpoints."""
from typing import Any, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import UserSerializer


class UserList(APIView):
    """API view for creating new users."""

    def post(self, request: Any, format: Optional[str] = None) -> Response:
        """Create a new user.

        Args:
            request: The HTTP request containing user data.
            format: The format of the response (optional).

        Returns:
            Response with created user data or errors.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    """API view for retrieving, updating,
    or deleting authenticated user data.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        """Retrieve the authenticated user's data.

        Args:
            request: The HTTP request.
            format: The format of the response (optional).

        Returns:
            Response with user data.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Any, format: Optional[str] = None) -> Response:
        """Update the authenticated user's data.

        Args:
            request: The HTTP request containing updated data.
            format: The format of the response (optional).

        Returns:
            Response with updated user data or errors.
        """
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Any, format: Optional[str] = None) -> Response:
        """Delete the authenticated user.

        Args:
            request: The HTTP request.
            format: The format of the response (optional).

        Returns:
            Response with no content.
        """
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
