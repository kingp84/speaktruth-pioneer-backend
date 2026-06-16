from datetime import date
import calendar

def is_second_wednesday(dt: date):
    """Return True if the given date is the 2nd Wednesday of the month."""
    return dt.weekday() == 2 and 8 <= dt.day <= 14

def is_fifth_sunday(dt):
    # Find the first Sunday of the month
    first = dt.replace(day=1)
    while first.weekday() != 6:  # 6 = Sunday
        first = first.replace(day=first.day + 1)

    # The 5th Sunday is 28 days after the first
    fifth = first.replace(day=first.day + 28)

    return fifth.month == dt.month and dt == fifth

