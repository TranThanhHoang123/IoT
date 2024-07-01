from django.utils import timezone
from datetime import timedelta


def is_updated_date_within_minutes(updated_date, minutes):
    if updated_date is None:
        return True  # Allow history creation if there's no previous date

    now = timezone.now()

    # Ensure both dates are aware datetime objects
    if updated_date.tzinfo is None:
        updated_date = timezone.make_aware(updated_date, timezone.get_default_timezone())

    # Calculate the time difference
    available_time = updated_date + timedelta(minutes=minutes)

    return now >= available_time
