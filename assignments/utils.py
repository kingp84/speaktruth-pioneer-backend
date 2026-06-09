from datetime import date
import calendar

def is_second_wednesday(dt: date):
    """Return True if the given date is the 2nd Wednesday of the month."""
    return dt.weekday() == 2 and 8 <= dt.day <= 14

def is_fifth_sunday(dt: date):
    """Return True if the given date is the 5th Sunday of the month."""
    return dt.weekday() == 6 and dt.day + 7 > calendar.monthrange(dt.year, dt.month)[1]
