"""
Serializers for the events application.
"""
from datetime import timezone as dt_timezone
from typing import Any, Dict
from rest_framework import serializers
from django.utils import timezone
from dateutil.rrule import rrulestr
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model, handling validation, creation and update"""
    class Meta:
        model = Event
        fields = [
                  'id', 'title', 'description', 'start_time',
                  'end_time', 'is_all_day', 'recurrence_rule', 'user'
                  ]
        read_only_fields = ['id', 'user']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event data for full-day, time-specific events, and recurrence rules."""
        validated_data = data.copy()
        is_all_day = data.get('is_all_day', False)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        title = data.get('title')
        recurrence_rule = data.get('recurrence_rule')

        if not title or title.strip() == '':
            raise serializers.ValidationError("Title is required and cannot be empty.")

        if not start_time:
            raise serializers.ValidationError("Start time is required for all events.")

        if start_time and not timezone.is_aware(start_time):
            raise serializers.ValidationError("Start time must be timezone-aware.")
        if end_time and not timezone.is_aware(end_time):
            raise serializers.ValidationError("End time must be timezone-aware.")

        if is_all_day:
            if end_time:
                raise serializers.ValidationError(
                    "Full-day events should not specify an end time."
                    )
            validated_data['start_time'] = start_time.replace(
                                                        hour=0,
                                                        minute=0,
                                                        second=0,
                                                        microsecond=0)
            start_time = validated_data['start_time']
        else:
            if not end_time:
                raise serializers.ValidationError(
                    "Non-full-day events must specify an end time."
                    )
            if start_time >= end_time:
                raise serializers.ValidationError("End time must be after start time.")
        if not is_all_day and end_time:
            if (end_time - start_time).total_seconds() > 24 * 60 * 60:
                raise serializers.ValidationError(
                    "Non-full-day events cannot exceed 24 hours."
                    )
        recurrence_rule = validated_data.get('recurrence_rule')
        if recurrence_rule:
            try:
                start_time = validated_data['start_time']
                rrulestr(recurrence_rule, dtstart=start_time)
            except ValueError as e:
                raise serializers.ValidationError("Invalid recurrence rule format: ", e)

        return validated_data

    def create(self, validated_data: Dict[str, Any]) -> Event:
        """
        Create an event with the authenticated user.

        Args:
            validated_data: Validated event data.

        Returns:
            Created Event instance.
        """
        validated_data = validated_data.copy()
        if 'start_time' in validated_data:
            validated_data['start_time'] = validated_data['start_time'].astimezone(
                dt_timezone.utc
                )
        if 'end_time' in validated_data:
            validated_data['end_time'] = validated_data['end_time'].astimezone(
                dt_timezone.utc
                )
        return Event.objects.create(user=self.context['request'].user, **validated_data)

    def update(self, instance: Event, validated_data: Dict[str, Any]) -> Event:
        """
        Update an existing event.

        Args:
            instance: Event instance to update.
            validated_data: Validated event data.

        Returns:
            Updated Event instance.
        """
        validated_data = validated_data.copy()
        if 'start_time' in validated_data:
            validated_data['start_time'] = validated_data['start_time'].astimezone(
                dt_timezone.utc
                )
        if 'end_time' in validated_data:
            validated_data['end_time'] = validated_data['end_time'].astimezone(
                dt_timezone.utc
                )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
