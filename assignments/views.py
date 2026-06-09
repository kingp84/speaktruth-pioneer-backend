from django.shortcuts import render, redirect
from django.utils import timezone
from calendar import monthrange
from datetime import date
from assignments.models import Assignment
from directory.models import Role
from assignments.utils import is_second_wednesday, is_fifth_sunday


# -----------------------------
# MONTHLY ASSIGNMENTS VIEW
# -----------------------------
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
                    "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service."
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


# -----------------------------
# CALENDAR VIEW (MONTH GRID)
# -----------------------------
def assignment_calendar(request):
    today = timezone.now().date()
    return redirect("assignment_calendar_month", year=today.year, month=today.month)


def assignment_calendar_month(request, year, month):
    first_day = date(year, month, 1)
    _, num_days = monthrange(year, month)

    days = [date(year, month, d) for d in range(1, num_days + 1)]

    assignments = Assignment.objects.filter(
        date__year=year,
        date__month=month
    )

    assignment_dates = set(a.date for a in assignments)

    context = {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "days": days,
        "assignment_dates": assignment_dates,
    }

    return render(request, "assignments/calendar.html", context)


# -----------------------------
# DAILY ASSIGNMENTS VIEW
# -----------------------------
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
