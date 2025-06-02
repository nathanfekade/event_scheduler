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
from .utils import get_event_occurrences

class EventListView(APIView):
    """View to list or create events for authenticated users."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request: Any) -> Response:
        """
        Retrieve all event occurrences for
        the authenticated user from the current time (UTC).
        """
        events = Event.objects.filter(user=request.user)
        start_date = timezone.now().astimezone(dt_timezone.utc)

        occurrences = []
        for event in events:
            event_occurrences = get_event_occurrences(
                event,
                start_date,
                max_occurrences=1000,
                max_future_years=10
            )
            for occ in event_occurrences:
                end_time = None
                if not event.is_all_day and event.end_time:
                    duration = event.end_time - event.start_time
                    end_time = occ + duration
                occurrences.append({
                    'event_id': event.id,
                    'title': event.title,
                    'start': occ.isoformat(),
                    'end': end_time.isoformat() if end_time else None,
                    'is_all_day': event.is_all_day,
                    'description': event.description
                })

        occurrences.sort(key=lambda x: x['start'])

        return Response(occurrences, status=status.HTTP_200_OK)

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
