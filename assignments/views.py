from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date
from assignments.models import Assignment
from assignments.utils import is_second_wednesday, is_fifth_sunday
import calendar

# PDF engine
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

def api_assignments_for_day(request, year, month, day):
    dt = date(year, month, day)

    assignments = Assignment.objects.filter(date=dt).select_related("person", "role")

    data = []

    for a in assignments:
        data.append({
            "id": a.id,
            "role": a.role.name,
            "person": a.person.full_name if a.person else None,
            "service_type": a.service_type,
        })

    notes = []
    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 2 PM. No regular evening service.")
    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    return JsonResponse({
        "date": dt.isoformat(),
        "assignments": data,
        "notes": notes,
    })

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

        # -------------------------
        # SUNDAY ASSIGNMENTS
        # -------------------------
        stype = a.service_type.upper().strip()

        if stype in ["SUNDAY MORNING", "SUNDAY EVENING"]:
            sundays.setdefault(dt, {
                "SUNDAY MORNING": [],
                "SUNDAY EVENING": [],
                "notes": []
            })

            sundays[dt][stype].append(a)

            # 5th Sunday logic
            if is_fifth_sunday(dt):
                note = (
                    "Fellowship Meal at noon. Afternoon service around 1 PM. "
                    "No regular evening service at 6p."
                )
                if note not in sundays[dt]["notes"]:
                    sundays[dt]["notes"].append(note)
                sundays[dt]["SUNDAY EVENING"] = []  # No PM service

        # -------------------------
        # WEDNESDAY ASSIGNMENTS
        # -------------------------
        if a.service_type == "WEDNESDAY EVENING":
            wednesdays.setdefault(dt, {
                "items": [],
                "notes": []
            })

            wednesdays[dt]["items"].append(a)

            if is_second_wednesday(dt):
                note = "Singing Night — congregational singing service."
                if note not in wednesdays[dt]["notes"]:
                    wednesdays[dt]["notes"].append(note)

    today = date.today()

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "monthly_roles": monthly_roles,
        "sundays": dict(sorted(sundays.items())),
        "wednesdays": dict(sorted(wednesdays.items())),
        "today": today,
        "current_year": today.year,
        "current_month": today.month,
    }

    return render(request, "assignments/monthly_assignments.html", context)

# ---------------------------------------------------------
# MONTHLY ASSIGNMENTS PDF
# ---------------------------------------------------------
def monthly_assignments_pdf(request, year, month):
    if not WEASYPRINT_AVAILABLE:
        return HttpResponse("PDF generation is not available on this server.", status=501)

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

        # -------------------------
        # SUNDAY ASSIGNMENTS
        # -------------------------
        if a.service_type in ["SUNDAY MORNING", "SUNDAY EVENING"]:
            sundays.setdefault(dt, {
                "SUNDAY MORNING": [],
                "SUNDAY EVENING": [],
                "notes": []
            })

            sundays[dt][a.service_type].append(a)

            # 5th Sunday logic
            if is_fifth_sunday(dt):
                note = (
                    "Fellowship Meal at noon. Afternoon service around 1 PM. "
                    "No regular evening service at 6p."
                )
                if note not in sundays[dt]["notes"]:
                    sundays[dt]["notes"].append(note)
                sundays[dt]["SUNDAY EVENING"] = []  # No PM service

        # -------------------------
        # WEDNESDAY ASSIGNMENTS
        # -------------------------
        if a.service_type == "WEDNESDAY EVENING":
            wednesdays.setdefault(dt, {
                "items": [],
                "notes": []
            })

            wednesdays[dt]["items"].append(a)

            if is_second_wednesday(dt):
                note = "Singing Night — congregational singing service."
                if note not in wednesdays[dt]["notes"]:
                    wednesdays[dt]["notes"].append(note)

    today = date.today()

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "monthly_roles": monthly_roles,
        "sundays": dict(sorted(sundays.items())),
        "wednesdays": dict(sorted(wednesdays.items())),
        "today": today,
        "current_year": today.year,
        "current_month": today.month,
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

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

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

    morning = assignments.filter(service_type="SUNDAY MORNING")
    evening = assignments.filter(service_type="SUNDAY EVENING")
    wednesday = assignments.filter(service_type="WEDNESDAY EVENING")

    notes = []

    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 1 PM. No regular evening service.")

    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    context = {
        "date": dt,
        "sun_am": morning,
        "sun_pm": evening,
        "wed_pm": wednesday,
        "notes": notes,
        "today": date.today(),
        "year": year,
        "month": month,
    }

    return render(request, "assignments/daily_assignments.html", context)


# ---------------------------------------------------------
# DAILY ASSIGNMENTS PDF
# ---------------------------------------------------------
def daily_assignments_pdf(request, year, month, day):
    if not WEASYPRINT_AVAILABLE:
        return HttpResponse("PDF generation is not available on this server.", status=501)

    dt = date(year, month, day)

    assignments = Assignment.objects.filter(date=dt).select_related("person", "role")

    morning = assignments.filter(service_type="SUNDAY MORNING")
    evening = assignments.filter(service_type="SUNDAY EVENING")
    wednesday = assignments.filter(service_type="WEDNESDAY EVENING")

    notes = []

    if is_fifth_sunday(dt):
        notes.append("Fellowship Meal at noon. Afternoon service around 1 PM. No regular evening service.")

    if is_second_wednesday(dt):
        notes.append("Singing Night — congregational singing service.")

    context = {
        "date": dt,
        "SUNDAY MORNING": morning,
        "SUNDAY EVENING": evening,
        "WEDNESDAY EVENING": wednesday,
        "notes": notes,
    }

    html_string = render_to_string("assignments/daily_assignments.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"assignments_{dt.isoformat()}.pdf\"'
    return response
