from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DirectoryEntry

@login_required
def directory_view(request):
    members = DirectoryEntry.objects.all().order_by("last_name", "first_name")

    context = {
        "members": members,
    }

    return render(request, "directory/directory.html", context)
