from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from members.views import (login_view, logout_view, member_home, songleader_app_info)

from assignments.views import (
    monthly_assignments,
    assignment_calendar,
    assignment_calendar_month,
    daily_assignments,
    monthly_assignments_pdf,
    api_assignments_for_day,
)

from directory.views import (
    directory_view,
    directory_pdf,   # <-- THIS WAS MISSING
)


def home_redirect(request):
    return redirect("member_home")


urlpatterns = [
    path("", home_redirect, name="home"),
    path("admin/", admin.site.urls),

    # Authentication
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Member home
    path("members/", member_home, name="member_home"),

    # Assignments
    path("assignments/<int:year>/<int:month>/", monthly_assignments, name="monthly_assignments"),
    path("assignments/calendar/", assignment_calendar, name="assignment_calendar"),
    path("assignments/calendar/<int:year>/<int:month>/", assignment_calendar_month, name="assignment_calendar_month"),
    path("assignments/<int:year>/<int:month>/<int:day>/", daily_assignments, name="daily_assignments"),

    # Assignment PDFs
    path("assignments/pdf/<int:year>/<int:month>/", monthly_assignments_pdf, name="monthly_assignments_pdf"),
    path("api/<int:year>/<int:month>/<int:day>/", api_assignments_for_day, name="api_assignments_for_day"),
    path("members/songleader-app/", songleader_app_info, name="songleader_app_info"),


    # Directory
    path("directory/", directory_view, name="directory"),

    # Directory PDF
    path("directory/pdf/", directory_pdf, name="directory_pdf"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
