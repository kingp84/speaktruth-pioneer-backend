"""
URL configuration for speaktruth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from dashboard.views import member_home
from assignments.views import monthly_assignments
from assignments.views_calendar import assignment_calendar
from assignments.views_daily import daily_assignments
from directory.views import directory_view

def home_redirect(request):
    return redirect("member_home")

urlpatterns = [
    path("", home_redirect, name="home"),
    path("admin/", admin.site.urls),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("members/", member_home, name="member_home"),
    path("assignments/<int:year>/<int:month>/", monthly_assignments, name="monthly_assignments"),
    path("assignments/calendar/", assignment_calendar, name="assignment_calendar"),
    path("assignments/calendar/<int:year>/<int:month>/", assignment_calendar_month, name="assignment_calendar_month"),
    path("assignments/<int:year>/<int:month>/<int:day>/", daily_assignments, name="daily_assignments"),
    path("directory/", directory_view, name="directory"),
]



