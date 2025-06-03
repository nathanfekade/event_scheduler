"""
Views for managing events and their occurrences in the events application.
"""
from datetime import timezone as dt_timezone
from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer

class EventListView(APIView):
    """View to list or create events for authenticated users."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def get(self, request, format=None):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Any) -> Response:
        """
        Create a new event for the authenticated user.
        """
        serializer = EventSerializer(
            data=request.data,
            context={'request': request}
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetailView(APIView):
    """View to retrieve, update, or delete
    a single event for authenticated users."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request: Any, pk: int) -> Response:
        """
        Retrieve a single event by ID for the authenticated user.
        """
        event = get_object_or_404(Event, pk=pk, user=request.user)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Any, pk: int) -> Response:
        """
        Update an existing event for the authenticated user.
        """
        event = get_object_or_404(Event, pk=pk, user=request.user)
        serializer = EventSerializer(
            instance=event,
            data=request.data,
            context={'request': request},
            partial=True
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Any, pk: int) -> Response:
        """
        Delete an existing event for the authenticated user.
        """
        event = get_object_or_404(Event, pk=pk, user=request.user)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
