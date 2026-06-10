from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from urllib.parse import quote

from .models import DirectoryEntry

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


@login_required
def directory_view(request):
    today = date.today()

    members = DirectoryEntry.objects.all().order_by("last_name", "first_name")

    context = {
        "members": members,
        "today": today,
        "year": today.year,
        "month": today.month,
    }

    return render(request, "directory/directory.html", context)


@login_required
def directory_pdf(request):
    if not WEASYPRINT_AVAILABLE:
        return HttpResponse(
            "PDF generation is not available on this server.",
            status=501
        )

    members = DirectoryEntry.objects.all().order_by("last_name", "first_name")

    html_string = render_to_string("directory/directory_pdf.html", {
        "members": members
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename=\"directory.pdf\"'
    return response
