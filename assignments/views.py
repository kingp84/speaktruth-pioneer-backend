from django.shortcuts import render, redirect
from django.utils import timezone
from calendar import monthrange
from datetime import date
from assignments.models import Assignment
from assignments.utils import is_second_wednesday, is_fifth_sunday
import calendar


# ---------------------------------------------------------
# MONTHLY ASSIGNMENTS VIEW
# ---------------------------------------------------------
def monthly_assignments(request, year, month):
    month_name = date(year, month, 1).strftime("%B")

    assignments = Assignment.objects.filter(
        date__year=year,
        date__month=month
    ).select_related("person", "role")

    monthly_roles = assignments.filter(service_type="MONTHLY")

    sundays = {}
    wednesdays = {}

    for a in assignments:
        dt = a.date

        # Sunday assignments
        if a.service_type in ["SUN_AM", "SUN_PM"]:
            sundays.setdefault(dt, {"AM": [], "PM": [], "notes": []})

            if a.service_type == "SUN_AM":
                sundays[dt]["AM"].append(a)
            else:
                sundays[dt]["PM"].append(a)

            # 5th Sunday logic
            if is_fifth_sunday(dt):
                sundays[dt]["notes"].append(
                    "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service at 6p."
                )
                sundays[dt]["PM"] = []

        # Wednesday assignments
        elif a.service_type == "WED_PM":
            wednesdays.setdefault(dt, {"items": [], "notes": []})
            wednesdays[dt]["items"].append(a)

            if is_second_wednesday(dt):
                wednesdays[dt]["notes"].append("Singing Night — congregational singing service.")

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "monthly_roles": monthly_roles,
        "sundays": dict(sorted(sundays.items())),
        "wednesdays": dict(sorted(wednesdays.items())),
    }

    return render(request, "assignments/monthly_assignments.html", context)


# ---------------------------------------------------------
# CALENDAR REDIRECT (GO TO CURRENT MONTH)
# ---------------------------------------------------------
def assignment_calendar(request):
    today = timezone.now().date()
    return redirect("assignment_calendar_month", year=today.year, month=today.month)


# ---------------------------------------------------------
# MONTHLY CALENDAR GRID VIEW (CORRECTED)
# ---------------------------------------------------------
def assignment_calendar_month(request, year, month):
    month_date = date(year, month, 1)
    month_name = month_date.strftime("%B")
    today = timezone.now().date()

    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_weeks = cal.monthdayscalendar(year, month)

    assignments = Assignment.objects.filter(
        date__year=year,
        date__month=month
    )

    assignment_dates = set(a.date.strftime("%Y-%m-%d") for a in assignments)

    # Previous month/year
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Next month/year
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "calendar": month_weeks,
        "today": today,
        "assignment_dates": assignment_dates,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, "assignments/calendar.html", context)


# ---------------------------------------------------------
# DAILY ASSIGNMENTS VIEW (FULLY FIXED)
# ---------------------------------------------------------
def daily_assignments(request, year, month, day):
    dt = date(year, month, day)

    assignments = Assignment.objects.filter(date=dt).select_related("person", "role")
    monthly_roles = Assignment.objects.filter(service_type="MONTHLY").select_related("person", "role")

    notes = []

    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service.")

    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    context = {
        "date": dt,
        "assignments": assignments,
        "monthly_roles": monthly_roles,
        "notes": notes,
    }

    return render(request, "assignments/daily_assignments.html", context)
