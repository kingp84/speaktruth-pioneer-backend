from django.shortcuts import render, get_list_or_404
from datetime import date
from assignments.models import Assignment

def daily_assignments(request, year, month, day):
    target_date = date(year, month, day)

    assignments = Assignment.objects.filter(date=target_date).select_related("person", "role")

    # Group by service type
    sun_am = assignments.filter(service_type="SUN_AM")
    sun_pm = assignments.filter(service_type="SUN_PM")
    wed_pm = assignments.filter(service_type="WED_PM")

    context = {
        "date": target_date,
        "sun_am": sun_am,
        "sun_pm": sun_pm,
        "wed_pm": wed_pm,
    }

    return render(request, "assignments/daily_assignments.html", context)
