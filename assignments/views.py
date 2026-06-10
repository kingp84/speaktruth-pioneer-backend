from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import date
import calendar

from assignments.models import Assignment
from assignments.utils import is_second_wednesday, is_fifth_sunday

# PDF engine
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    EASYPRINT_AVAILABLE = False



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
                if "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service at 6p." not in sundays[dt]["notes"]:
                    sundays[dt]["notes"].append(
                        "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service at 6p."
                    )
                sundays[dt]["PM"] = []  # No PM service on 5th Sunday

        # Wednesday assignments
        elif a.service_type == "WED_PM":
            wednesdays.setdefault(dt, {"items": [], "notes": []})
            wednesdays[dt]["items"].append(a)

            if is_second_wednesday(dt):
                if "Singing Night — congregational singing service." not in wednesdays[dt]["notes"]:
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
# MONTHLY ASSIGNMENTS PDF
# ---------------------------------------------------------
def monthly_assignments_pdf(request, year, month):
    if not WEASYPRINT_AVAILABLE:
        return HttpResponse("PDF generation is not available on this server.", status=501)

    assignments = Assignment.objects.filter(
        date__year=year,
        date__month=month
    ).select_related("person", "role")

    monthly_roles = assignments.filter(service_type="MONTHLY")

    sundays = {}
    wednesdays = {}

    for a in assignments:
        dt = a.date

        if a.service_type in ["SUN_AM", "SUN_PM"]:
            sundays.setdefault(dt, {"AM": [], "PM": [], "notes": []})

            if a.service_type == "SUN_AM":
                sundays[dt]["AM"].append(a)
            else:
                sundays[dt]["PM"].append(a)

            if is_fifth_sunday(dt):
                if "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service at 6p." not in sundays[dt]["notes"]:
                    sundays[dt]["notes"].append(
                        "Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service at 6p."
                    )
                sundays[dt]["PM"] = []

        elif a.service_type == "WED_PM":
            wednesdays.setdefault(dt, {"items": [], "notes": []})
            wednesdays[dt]["items"].append(a)

            if is_second_wednesday(dt):
                if "Singing Night — congregational singing service." not in wednesdays[dt]["notes"]:
                    wednesdays[dt]["notes"].append("Singing Night — congregational singing service.")

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "monthly_roles": monthly_roles,
        "sundays": dict(sorted(sundays.items())),
        "wednesdays": dict(sorted(wednesdays.items())),
    }

    html_string = render_to_string("assignments/monthly_assignments.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"assignments_{year}_{month}.pdf\"'
    return response


# ---------------------------------------------------------
# CALENDAR REDIRECT
# ---------------------------------------------------------
def assignment_calendar(request):
    today = timezone.now().date()
    return redirect("assignment_calendar_month", year=today.year, month=today.month)


# ---------------------------------------------------------
# MONTHLY CALENDAR GRID VIEW
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
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    # Next month/year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

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
# DAILY ASSIGNMENTS VIEW
# ---------------------------------------------------------
def daily_assignments(request, year, month, day):
    dt = date(year, month, day)

    assignments = Assignment.objects.filter(date=dt).select_related("person", "role")

    sun_am = assignments.filter(service_type="SUN_AM")
    sun_pm = assignments.filter(service_type="SUN_PM")
    wed_pm = assignments.filter(service_type="WED_PM")

    notes = []

    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service.")

    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    today = date.today()

    context = {
        "date": dt,
        "sun_am": sun_am,
        "sun_pm": sun_pm,
        "wed_pm": wed_pm,
        "notes": notes,
        "today": today,
        "year": today.year,
        "month": today.month,
    }

    return render(request, "assignments/daily_assignments.html", context)



# ---------------------------------------------------------
# DAILY ASSIGNMENTS PDF
# ---------------------------------------------------------
def daily_assignments_pdf(request, year, month, day):
    if not WEASYPRINT_AVAILABLE:
        return HttpResponse("PDF generation is not available on this server.", status=501)

    assignments = Assignment.objects.filter(date=dt).select_related("person", "role")

    sun_am = assignments.filter(service_type="SUN_AM")
    sun_pm = assignments.filter(service_type="SUN_PM")
    wed_pm = assignments.filter(service_type="WED_PM")

    notes = []

    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service.")

    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    context = {
        "date": dt,
        "sun_am": sun_am,
        "sun_pm": sun_pm,
        "wed_pm": wed_pm,
        "notes": notes,
    }

    html_string = render_to_string("assignments/daily_assignments.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"assignments_{dt.isoformat()}.pdf\"'
    return response
