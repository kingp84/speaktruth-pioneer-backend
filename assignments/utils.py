from datetime import date
import calendar

def is_second_wednesday(dt: date):
    """Return True if the given date is the 2nd Wednesday of the month."""
    return dt.weekday() == 2 and 8 <= dt.day <= 14

def is_fifth_sunday(dt):
    # Must be a Sunday to even be considered
    if dt.weekday() != 6:  # 6 = Sunday
        return False

    # Count how many Sundays are in this month
    count = 0
    day = 1
    while True:
        try:
            d = dt.replace(day=day)
        except ValueError:
            break  # past end of month

        if d.weekday() == 6:
            count += 1

        day += 1

    # If there are 5 Sundays, the last one is the 5th
    if count < 5:
        return False

    # Find the actual 5th Sunday
    sunday_count = 0
    day = 1
    while True:
        try:
            d = dt.replace(day=day)
        except ValueError:
            break

        if d.weekday() == 6:
            sunday_count += 1
            if sunday_count == 5:
                return dt == d

        day += 1


