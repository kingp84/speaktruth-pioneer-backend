from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'service_type', 'role', 'person')
    list_filter = ('service_type', 'role')
    search_fields = ('person__first_name', 'person__last_name')
    fields = ('date', 'service_type', 'role', 'person', 'notes')

