from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("member_home")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def member_home(request):
    today = date.today()
    return render(request, "members/home.html", {
        "year": today.year,
        "month": today.month,
    })
