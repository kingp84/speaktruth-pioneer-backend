from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("date", "service_type", "role", "family", "person")
    list_filter = ("service_type", "role")
    search_fields = ("family", "notes", "person__first_name", "person__last_name")

    # This controls what fields appear in the admin form
    fields = ("date", "service_type", "role", "family", "person", "notes")


