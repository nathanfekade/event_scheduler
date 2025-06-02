"""
Utility functions for generating event occurrences.
"""
from datetime import timezone as dt_timezone
from datetime import timedelta, datetime, date
from typing import Any, List, Union

from dateutil.rrule import rrulestr
from django.utils import timezone


def get_event_occurrences(
    event: Any,
    start_date: datetime,
    max_occurrences: int = 1000,
    max_future_years: int = 10,
) -> List[Union[datetime, date]]:
    """
    Generate a list of occurrence datetimes
    for an event starting from a date, with limits.
    Args:
        event: Event instance with start_time, recurrence_rule, and is_all_day attributes
        start_date: timezone-aware datetime (start of range)
        max_occurrences: Maximum number of occurrences to generate (default: 1000)
        max_future_years: Maximum years into the future to generate
        occurrences (default: 10)
    Returns:
        List of occurrence datetimes (or dates for all-day events in UTC)
    Raises:
        ValueError: If start_date is not timezone-aware
    """
    if not timezone.is_aware(start_date):
        raise ValueError("start_date must be timezone-aware")

    max_future_date = timezone.now() + timedelta(days=365 * max_future_years)
    end_date = max_future_date

    if not event.recurrence_rule:
        if start_date <= event.start_time <= end_date:
            return [event.start_time.astimezone(dt_timezone.utc).date()
                     if event.is_all_day else event.start_time
                    ]
        return []

    try:
        rule = rrulestr(event.recurrence_rule, dtstart=event.start_time)
    except ValueError:
        return []

    occurrences = []
    for occ in rule:
        if occ > end_date:
            break
        if occ >= start_date:
            occurrences.append(occ)
            if len(occurrences) >= max_occurrences:
                break
    if event.is_all_day:
        occurrences = [occ.astimezone(dt_timezone.utc).date() for occ in occurrences]

    occurrences.sort()
    return occurrences
