from django.shortcuts import render
from datetime import date
import calendar

def assignment_calendar(request, year=None, month=None):
    today = date.today()

    if year is None or month is None:
        year = today.year
        month = today.month

    year = int(year)
    month = int(month)

    # FIX: Start week on Sunday
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    month_label = date(year, month, 1).strftime("%B")

    # Previous month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Next month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        "year": year,
        "month": month,
        "month_label": month_label,
        "calendar": month_days,
        "today": today,

        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,

        "sunday_days": [],
        "wednesday_days": [],
    }

    return render(request, "assignments/assignment_calendar.html", context)
