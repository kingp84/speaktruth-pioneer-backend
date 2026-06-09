from django.shortcuts import render
from django.utils import timezone
from calendar import monthrange
from datetime import date
from assignments.models import Assignment
from directory.models import Role
from assignments.utils import is_second_wednesday, is_fifth_sunday

def monthly_assignments(request, year, month):
    # Determine month name
    month_name = date(year, month, 1).strftime("%B")

    # Get all assignments for the month
    assignments = Assignment.objects.filter(
        date__year=year,
        date__month=month
    ).select_related("person", "role")

    # Group monthly roles (Lord’s Supper, Communion Prep, etc.)
    monthly_roles = assignments.filter(service_type="MONTHLY")

    sundays = {}
    wednesdays = {}

    for a in assignments:
        dt = a.date

        # --- Sunday Assignments ---
        if a.service_type in ["SUN_AM", "SUN_PM"]:
            sundays.setdefault(dt, {"AM": [], "PM": [], "notes": []})

            # Add assignment
            if a.service_type == "SUN_AM":
                sundays[dt]["AM"].append(a)
            else:
                sundays[dt]["PM"].append(a)

            # 5th Sunday Logic
            if is_fifth_sunday(dt):
                sundays[dt]["notes"].append(
                    "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service."
                )
                # Remove normal PM assignments
                sundays[dt]["PM"] = []

        # --- Wednesday Assignments ---
        elif a.service_type == "WED_PM":
            wednesdays.setdefault(dt, {"items": [], "notes": []})
            wednesdays[dt]["items"].append(a)

            # Singing Night Logic
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
