from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from urllib.parse import quote

from .models import DirectoryEntry

# ---------------------------------------------------------
# OPTIONAL PDF ENGINE (SAFE IMPORT)
# ---------------------------------------------------------
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


# ---------------------------------------------------------
# DIRECTORY VIEW
# ---------------------------------------------------------
@login_required
def directory_view(request):
    members = DirectoryEntry.objects.all().order_by("last_name", "first_name")

    context = {
        "members": members,
    }

    return render(request, "directory/directory.html", context)


# ---------------------------------------------------------
# DIRECTORY PDF VIEW (DYNAMIC, SAFE)
# ---------------------------------------------------------
@login_required
def directory_pdf(request):
    # If WeasyPrint is not installed on the server, avoid crashing
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
    response["Content-Disposition"] = 'attachment; filename="directory.pdf"'
    return response
