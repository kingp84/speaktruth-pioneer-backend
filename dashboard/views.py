from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date

@login_required
def member_home(request):
    today = date.today()
    year = today.year
    month = today.month

    context = {
        "year": year,
        "month": month,
    }

    return render(request, "dashboard/member_home.html", context)


